"""Static validation of GASD 1.2 behavioral contracts."""

import ast
import re
from collections import Counter, deque

from .SemanticErrorReporter import ErrorLevel, StructuredSemanticError
from .SemanticNodes import SourceRange
from .SymbolTable import BuiltinTypeRegistry

NUMERIC_TYPES = {"Integer", "Int", "Int32", "Float", "Decimal"}
_DURATION = re.compile(r"([0-9]+)(ms|s|m)\Z")
_RETRY = re.compile(r"retry\(([0-9]+)\)\Z")
_DURATION_MULTIPLIER = {"ms": 1, "s": 1000, "m": 60000}


def parse_timing(value):
    """Return a minimum duration in milliseconds or an exact retry count."""
    duration = _DURATION.fullmatch(value)
    if duration:
        return "duration", int(duration[1]) * _DURATION_MULTIPLIER[duration[2]]
    retry = _RETRY.fullmatch(value)
    if retry:
        return "retry", int(retry[1])
    return None


def literal_type_value(text):
    """Decode a literal type while retaining the exact type of its value."""
    try:
        return ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return text


class ContractValidator:
    def __init__(self, files, reporter):
        self.files = files
        self.reporter = reporter

    def _report(self, file, node, message):
        self.reporter.report(StructuredSemanticError(
            code="CONTRACT", message=message, level=ErrorLevel.ERROR,
            location=SourceRange(file.filePath, node.line, node.column, node.endLine, node.endColumn),
        ))

    def _imported_files(self, file, alias=None):
        for declaration in file.imports:
            if alias is None or declaration["alias"] == alias:
                target = self.files.get(declaration["path"])
                if target is not None:
                    yield target

    def _resolve_method(self, file, target):
        prefix, separator, method_name = target.rpartition(".")
        if not separator:
            return []
        scope, qualified, component_name = prefix.rpartition(".")

        def matching(providers, component_filter):
            return [
                (provider, method)
                for provider in providers
                for component in provider.syntacticRoot.components
                if component_filter is None or component.name == component_filter
                for method in component.methods if method.name == method_name
            ]

        if not qualified:
            local = matching([file], component_name)
            if local:
                return local
            aliased = list(self._imported_files(file, component_name))
            if aliased:
                return matching(aliased, None)
            unaliased_paths = {declaration["path"] for declaration in file.imports if not declaration["alias"]}
            visible = [
                provider for provider in self.files.values()
                if provider.namespace == file.namespace or provider.filePath in unaliased_paths
            ]
            return matching(visible, component_name)

        aliased = list(self._imported_files(file, scope))
        providers = aliased or [
            candidate for candidate in self.files.values() if candidate.namespace == scope.lower()
        ]
        return matching(providers, component_name)

    def _resolve_type(self, file, name):
        prefix, separator, base = name.rpartition(".")
        if separator:
            candidates = list(self._imported_files(file, prefix)) or [
                candidate for candidate in self.files.values() if candidate.namespace == prefix.lower()
            ]
            pending = deque((candidate, 0) for candidate in candidates)
        else:
            pending = deque([(file, 0)])

        visited = set()
        matches = []
        match_depth = None
        while pending:
            candidate, depth = pending.popleft()
            if candidate.filePath in visited or (match_depth is not None and depth > match_depth):
                continue
            visited.add(candidate.filePath)
            for definition in candidate.syntacticRoot.types:
                if definition.name == base:
                    matches.append((candidate, definition))
                    match_depth = depth
            if match_depth is None:
                pending.extend((imported, depth + 1) for imported in self._imported_files(candidate))
        return matches[0] if len(matches) == 1 else None

    def _signature_type(self, file, expression):
        if expression is None:
            return None
        name = expression.baseType
        resolved = self._resolve_type(file, name)
        if resolved:
            source, definition = resolved
            identity = (source.filePath, definition.name)
        else:
            identity = name
        literal = literal_type_value(expression.literalValue) if expression.literalValue is not None else None
        return (
            identity, expression.isOptional, (type(literal), literal),
            tuple(literal_type_value(value) for value in expression.enumValues or ()),
            tuple(self._signature_type(file, argument) for argument in expression.genericArgs or ()),
        )

    def _validate_signature(self, contract, file):
        if not contract.output:
            self._report(file, contract, f"CONTRACT '{contract.name}' must declare an OUTPUT type.")
        names = set()
        for parameter in contract.inputs:
            if parameter.name in names:
                self._report(file, parameter, f"Duplicate CONTRACT input '{parameter.name}'.")
            names.add(parameter.name)
            if not parameter.typeDeclared:
                self._report(file, parameter, f"CONTRACT input '{parameter.name}' must declare a type.")

        candidates = self._resolve_method(file, contract.name)
        if len(candidates) != 1:
            reason = "is ambiguous" if candidates else "does not resolve"
            self._report(file, contract, f"CONTRACT target '{contract.name}' {reason} to an interface method.")
            return
        provider, method = candidates[0]
        supplied = [self._signature_type(file, item.type) for item in contract.inputs]
        expected = [self._signature_type(provider, item.type) for item in method.parameters]
        parameter_positions = {parameter.name: index for index, parameter in enumerate(method.parameters)}
        name_order_matches = all(
            parameter_positions.get(parameter.name, index) == index
            for index, parameter in enumerate(contract.inputs)
        )
        if supplied != expected or not name_order_matches:
            self._report(file, contract, f"CONTRACT '{contract.name}' input signature differs from the interface method.")
        if contract.output and self._signature_type(file, contract.output) != self._signature_type(provider, method.returnType):
            self._report(file, contract, f"CONTRACT '{contract.name}' output type differs from the interface method.")

    def _operand_type(self, file, guard, operand, inputs):
        kind = operand["kind"]
        if kind != "reference":
            return {"integer": "Integer", "float": "Float"}.get(kind, kind)

        reference = operand["value"]
        root, *fields = reference.split(".")
        scope = file
        expression = inputs.get(root)
        for name in fields:
            resolved = self._resolve_type(scope, expression.baseType) if expression is not None else None
            if resolved is None:
                expression = None
                break
            scope, definition = resolved
            expression = next((item.type for item in definition.fields or () if item.name == name), None)
        if expression is None:
            self._report(file, guard, f"WHEN reference '{reference}' does not identify a declared input or field.")
            return None
        if expression.baseType == "literal":
            literal = literal_type_value(expression.literalValue)
            return {int: "Integer", float: "Float", str: "String"}.get(type(literal))
        return expression.baseType

    def _validate_type_test(self, file, guard, expression):
        name = expression["baseType"]
        arguments = expression["genericArgs"] or []
        if name in BuiltinTypeRegistry.TYPE_NAMES:
            problem = BuiltinTypeRegistry.validateGenerics(name, len(arguments))
            if problem:
                self._report(file, guard, f"WHEN IS has an invalid type: {problem}")
        elif name not in {"literal", "Record"} and self._resolve_type(file, name) is None:
            self._report(file, guard, f"WHEN IS type '{name}' does not resolve to a declared type.")
        for argument in arguments:
            self._validate_type_test(file, guard, argument)

    def _validate_case(self, file, case, inputs):
        if case.hasLegacySteps:
            self._report(file, case, f"CASE '{case.name}' contains an unsupported clause.")
        counts = Counter(clause["type"] for clause in case.clauses)
        for name in ("THROWS", "AFTER"):
            if counts[name] > 1:
                self._report(file, case, f"CASE '{case.name}' permits at most one {name} clause.")
        for clause in case.clauses:
            if clause["type"] != "AFTER":
                continue
            value = clause["value"]
            timing = parse_timing(value)
            if value.split("(", 1)[0] == "retry" and timing is None:
                self._report(file, case, f"CASE '{case.name}' requires retry with one nonnegative integer.")
            elif timing is None and not re.fullmatch(r"[#a-zA-Z_][#a-zA-Z0-9_-]*\(.+\)", value):
                self._report(file, case, f"CASE '{case.name}' has an invalid AFTER requirement.")

        for guard in case.when:
            left = self._operand_type(file, guard, guard.left_operand, inputs)
            if guard.operator == "IS":
                self._validate_type_test(file, guard, guard.right_operand["value"])
                continue
            right = self._operand_type(file, guard, guard.right_operand, inputs)
            if guard.operator in {"<", ">", "<=", ">="} and None not in (left, right):
                if left not in NUMERIC_TYPES or right not in NUMERIC_TYPES:
                    self._report(file, guard, f"WHEN operator '{guard.operator}' requires numeric operands.")

    def validate(self, contract, file, cases):
        self._validate_signature(contract, file)
        for duplicate in contract.duplicateCases:
            self._report(file, duplicate, f"Duplicate CASE '{duplicate.name}' in CONTRACT '{contract.name}'.")
        inputs = {parameter.name: parameter.type for parameter in contract.inputs}
        for case in cases:
            self._validate_case(file, case, inputs)
