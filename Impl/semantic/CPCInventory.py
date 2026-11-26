"""Compare the authored occurrences with the concrete semantic JSON nodes."""

from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import asdict, dataclass
from hashlib import sha512
import json
from types import SimpleNamespace

from ..ast.ASTNodes import MatchNode
from .AnnotationResolver import AnnotationResolver
from .ASTProvenance import BYTE_HASH_KEY, content_fingerprints
from .SemanticNodes import ScopeEnum
from .SymbolTable import BuiltinTypeRegistry


VERSION = 1
_MISSING = object()


@dataclass(frozen=True)
class _Names:
    """Alternative spellings of the same type identity (local or qualified)."""

    values: tuple


@dataclass(frozen=True)
class _Keys:
    values: frozenset


@dataclass(frozen=True)
class Occurrence:
    kind: str
    path: str
    line: int
    column: int
    owner: str
    address: tuple
    fields: object

    def record(self):
        pointer = "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in self.address)
        parts = [self.kind, self.path, self.line, self.column, self.owner]
        value = {
            "kind": self.kind, "path": self.path, "line": self.line, "column": self.column,
            "owner": self.owner, "pointer": pointer,
        }
        if self.kind == "annotation":
            alias = self.fields["alias"]
            parts.append(alias)
            value["alias"] = alias
        value["identity"] = json.dumps(parts, ensure_ascii=False, separators=(",", ":"))
        return value


class CPCReconciliationError(ValueError):
    def __init__(self, occurrence, detail):
        self.occurrence = occurrence
        super().__init__(f"Source reconciliation failed for {occurrence.kind} owned by {occurrence.owner}: {detail}")


def _namespace(source):
    for directive in source.directives:
        if directive.directiveType == "NAMESPACE" and directive.values:
            return directive.values[0].strip('"\' ').lower()
    return "global"


def _difference(expected, actual, field="value"):
    if isinstance(expected, _Names):
        return None if actual in expected.values else field
    if isinstance(expected, _Keys):
        return None if isinstance(actual, dict) and actual.keys() == expected.values else field
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return field
        for name, value in expected.items():
            failure = _difference(value, actual.get(name, _MISSING), f"{field}.{name}")
            if failure is not None:
                return failure
        return None
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(expected) != len(actual):
            return field
        for index, (left, right) in enumerate(zip(expected, actual)):
            failure = _difference(left, right, f"{field}[{index}]")
            if failure is not None:
                return failure
        return None
    return None if type(expected) is type(actual) and expected == actual else field


class CPCInventory:
    """Immutable expectations taken from syntax before semantic conversion."""

    def __init__(self, sources, paths, digests):
        self.paths = dict(paths)
        self.sources = [{"path": path, "sha512": digest} for path, digest in sorted(digests.items())]
        self.syntax = {source.sourceFile: source for source in sources}
        self.namespaces = {source.sourceFile: _namespace(source) for source in sources}
        self.occurrences = []
        self.annotations = AnnotationResolver()
        self.root_counts = dict.fromkeys(
            ("annotations", "contracts", "models", "assumptions", "globalConstraints", "postconditions", "matches"), 0,
        )
        self.declarations = defaultdict(lambda: defaultdict(set))
        self.first = Occurrence("artifact", self.sources[0]["path"], 1, 0, "system", (), {})
        for source in sources:
            self._file(source)
            for kind in ("types", "components", "flows", "strategies", "decisions"):
                self.declarations[self.namespaces[source.sourceFile]][kind].update(
                    node.name for node in getattr(source, kind)
                )
        observed = Counter((row.path, row.line, row.column) for row in self.occurrences if row.kind == "annotation")
        for source in sources:
            path = self.paths[source.sourceFile]
            required = Counter((path, line, column) for line, column in source.cpc_annotation_positions)
            missing = required - observed
            if missing:
                _, line, column = min(missing)
                occurrence = Occurrence("annotation", path, line, column, self.namespaces[source.sourceFile], (), {})
                raise CPCReconciliationError(occurrence, "annotation has no semantic owner")
        self.occurrences = tuple(self.occurrences)
        identities = {row.record()["identity"] for row in self.occurrences}
        if len(identities) != len(self.occurrences):
            raise CPCReconciliationError(self.first, "duplicate source occurrence identity")

    def _location(self, node):
        if isinstance(node, dict):
            return self.paths[node["sourceFile"]], node["line"], node["column"]
        return self.paths[node.sourceFile], node.line, node.column

    def _add(self, node, kind, owner, address, fields, *, map_location=True):
        path, line, column = self._location(node)
        if map_location:
            fields = {**fields, "sourceMap": {"file": path, "startLine": line, "startCol": column}}
        self.occurrences.append(Occurrence(kind, path, line, column, owner, address, deepcopy(fields)))

    def _include_annotations(self, node, scope, owner, address, *, offset=0):
        converted = self.annotations.resolve(node.annotations, scope, validate=False)
        for index, (annotation, semantic) in enumerate(zip(node.annotations, converted), offset):
            fields = semantic.to_dict()
            fields.pop("sourceMap", None)
            self._add(annotation, "annotation", owner, address + ("annotations", index), fields)
        return [{} for _ in converted]

    def _type(self, expr, source, address=None, owner=None):
        if expr is None:
            return None
        name = expr.baseType
        alternatives = {name}
        prefix, separator, tail = name.partition(".")
        if separator:
            for resolved in source.cpc_imports:
                if resolved["alias"] == prefix and resolved["path"] in self.namespaces:
                    namespace = self.namespaces[resolved["path"]]
                    alternatives.add(f"{namespace}.{tail}" if namespace != "global" else tail)
        elif any(node.name == name for node in source.types):
            alternatives.add(f"{self.namespaces[source.sourceFile]}.{name}")
        expected = {
            "baseType": _Names(tuple(sorted(alternatives))),
            "declaredType": name,
            "optional": expr.isOptional,
            "enumValues": list(expr.enumValues or ()),
            "args": [
                self._type(arg, source, address + ("args", index), owner)
                if address is not None and not hasattr(expr, "recordFields") else self._type(arg, source)
                for index, arg in enumerate(expr.genericArgs or ())
            ],
        }
        if expr.literalValue is not None:
            expected["literalValue"] = expr.literalValue
        if hasattr(expr, "recordFields"):
            expected["recordFields"] = [{} for _ in expr.recordFields]
            if address is not None:
                self._parameters(expr.recordFields, source, owner, address + ("recordFields",), "field")
        return expected

    def _fields(self, fields, source, owner, address):
        for field in fields:
            path = address + (field.name,)
            field_owner = f"{owner}.{field.name}"
            annotations = self._include_annotations(field, ScopeEnum.FIELD, field_owner, path)
            self._add(field, "field", field_owner, path, {
                "name": field.name, "typeRef": self._type(field.type, source, path + ("typeRef",), field_owner),
                "isOptional": field.type.isOptional, "alias": getattr(field, "alias", None),
                "annotations": annotations,
            })

    def _parameters(self, parameters, source, owner, address, kind="parameter"):
        for index, parameter in enumerate(parameters):
            path = address + (index,)
            parameter_owner = f"{owner}.{parameter.name}"
            annotations = self._include_annotations(parameter, ScopeEnum.FIELD, parameter_owner, path)
            self._add(parameter, kind, parameter_owner, path, {
                "name": parameter.name, "annotations": annotations,
                "typeRef": self._type(parameter.type, source, path + ("typeRef",), parameter_owner),
            })

    def _signature(self, parameters, result_type, source, owner, address):
        self._parameters(parameters, source, owner, address + ("inputs",))
        fields = {"inputs": [{} for _ in parameters]}
        if result_type is not None:
            fields["output"] = self._type(result_type, source, address + ("output",), owner)
        return fields

    def _step(self, node, owner, address, branch=None):
        if isinstance(node, MatchNode):
            self._match(node, owner, address, branch)
            return
        if not hasattr(node, "action"):
            annotations = self._include_annotations(node, ScopeEnum.FIELD, owner, address)
            source = self.syntax[node.sourceFile]
            self._add(node, "flow_data", owner, address, {
                "operation": "DATA", "targetExpression": {"value": node.name},
                "annotations": annotations, "dataType": self._type(node.type, source, address + ("dataType",), owner),
            })
            return
        operation, target = node.action, node.target
        kind = "step"
        if operation == "OTHERWISE":
            operation, _, target = target.partition(" ")
            operation = operation if operation in ("THROW", "RETURN") else "RETURN"
            kind = "branch"
        annotations = self._include_annotations(node, ScopeEnum.STEP, owner, address)
        fields = {"operation": operation, "targetExpression": {"value": target}, "annotations": annotations}
        if kind != "branch":
            fields.update(
                stepNumber=node.stepNumber, stepId=getattr(node, "stepId", None),
                dependsOn=list(node.dependsOn or ()), postconditions=list(node.postconditions or ()),
                timeout=node.timeout, branch=branch,
            )
            if node.asBinding and node.typePath:
                fields["bindings"] = {node.asBinding: {"symbolId": node.typePath}}
            conditions = getattr(node, "postconditionNodes", [])
            fields["conditionNodes"] = [self._serialized(condition) for condition in conditions]
            for index, condition in enumerate(conditions):
                self._add(condition, "postcondition", owner, address + ("conditionNodes", index),
                          self._serialized(condition), map_location=False)
        else:
            fields["branch"] = "otherwise"
        steps = [
            child for child in node.subSteps or ()
            if getattr(child, "action", None) != "OTHERWISE"
        ]
        handlers = [child for child in steps if getattr(child, "branch", None) == "ON_ERROR"]
        if len(handlers) == 1:
            handler = handlers[0]
            self._step(handler, f"{owner}.error", address + ("errorPath",), "ON_ERROR")
            steps = [child for child in steps if child is not handler]
        for child in node.subSteps or ():
            if getattr(child, "action", None) == "OTHERWISE":
                self._step(child, f"{owner}.otherwise", address + ("otherwisePath",))
        if steps:
            fields["subSteps"] = [{} for _ in steps]
        for index, child in enumerate(steps):
            child_branch = getattr(child, "branch", None)
            child_owner = self._step_owner(owner, child, index, child_branch)
            self._step(child, child_owner, address + ("subSteps", index), child_branch)
        self._add(node, kind, owner, address, fields)

    @staticmethod
    def _step_owner(owner, step, index, branch=None):
        number = getattr(step, "stepId", None) or str(getattr(step, "stepNumber", None) or index + 1)
        return f"{owner}.{branch or 'step'}[{number.rstrip('.')}]"

    def _match(self, node, owner, address, branch):
        self._add(node, "step", owner, address, {
            "operation": "MATCH", "targetExpression": {"value": node.expression},
            "stepNumber": getattr(node, "stepNumber", None), "stepId": getattr(node, "stepId", None),
            "branch": branch, "subSteps": [{} for _ in node.cases],
            "annotations": self._include_annotations(node, ScopeEnum.STEP, owner, address),
        })
        for index, case in enumerate(node.cases):
            case_owner = f"{owner}.case[{index + 1}]"
            pointer = address + ("subSteps", index)
            fields = {"operation": "CASE", "targetExpression": {"value": case.condition}, "patterns": case.patterns}
            if case.steps:
                fields["subSteps"] = [{} for _ in case.steps]
            self._add(case, "branch", case_owner, pointer, fields)
            for step_index, step in enumerate(case.steps):
                step_owner = self._step_owner(case_owner, step, step_index)
                self._step(step, step_owner, pointer + ("subSteps", step_index))

    def _serialized(self, value):
        if isinstance(value, dict):
            return {key: self.paths.get(item, item) if key == "sourceFile" else self._serialized(item)
                    for key, item in value.items()}
        if isinstance(value, list):
            return [self._serialized(item) for item in value]
        return value

    def _root_address(self, name):
        index = self.root_counts[name]
        self.root_counts[name] += 1
        return name, index

    def _file(self, source):
        namespace = self.namespaces[source.sourceFile]
        path = self.paths[source.sourceFile]
        prefix = ("namespaces", namespace)
        file_address = ("compilationUnit", "fileNodes", path)
        offset = self.root_counts["annotations"]
        self.root_counts["annotations"] += len(
            self._include_annotations(source, ScopeEnum.GLOBAL, namespace, (), offset=offset)
        )
        other_directives = [directive for directive in source.directives if directive.directiveType != "IMPORT"]
        for index, directive in enumerate(other_directives):
            self._add(directive, directive.directiveType.lower(), namespace, file_address + ("directives", index),
                      {"directive": directive.directiveType, "values": directive.values})
        imports = [directive for directive in source.directives if directive.directiveType == "IMPORT"]
        for index, (directive, resolved) in enumerate(zip(imports, source.cpc_imports)):
            self._add(directive, "import", namespace, file_address + ("imports", index),
                      {"path": self.paths[resolved["path"]], "alias": directive.alias})

        for node in source.types:
            owner = f"{namespace}.{node.name}"
            address = prefix + ("types", node.name)
            fields = {"name": node.name, "isEnum": node.isEnum, "fields": _Keys(frozenset(f.name for f in node.fields))}
            if node.definition is not None:
                fields["definition"] = self._type(node.definition, source, address + ("definition",), owner)
            fields["annotations"] = self._include_annotations(node, ScopeEnum.TYPE, owner, address)
            self._add(node, "type", owner, address, fields)
            self._fields(node.fields, source, owner, address + ("fields",))

        for node in source.components:
            owner = f"{namespace}.{node.name}"
            address = prefix + ("components", node.name)
            fields = {
                "name": node.name, "pattern": node.pattern or "",
                "dependencies": [{"symbolId": dependency} for dependency in node.dependencies or ()],
                "methods": _Keys(frozenset(method.name for method in node.methods)),
                "fields": _Keys(frozenset(field.name for field in node.fields)),
                "interfaces": self._serialized(node.interfaces),
                "annotations": self._include_annotations(node, ScopeEnum.COMPONENT, owner, address),
            }
            self._add(node, "component", owner, address, fields)
            for index, interface in enumerate(node.interfaces):
                self._add(interface, "interface", owner, address + ("interfaces", index),
                          self._serialized(interface), map_location=False)
            self._fields(node.fields, source, owner, address + ("fields",))
            for method in node.methods:
                method_owner = f"{owner}.{method.name}"
                pointer = address + ("methods", method.name)
                fields = self._signature(method.parameters, method.returnType, source, method_owner, pointer)
                fields["annotations"] = self._include_annotations(method, ScopeEnum.COMPONENT, method_owner, pointer)
                self._add(method, "operation", method_owner, pointer, {"name": method.name, **fields})

        for node in source.flows:
            owner = f"{namespace}.{node.name}"
            address = prefix + ("flows", node.name)
            fields = self._signature(node.parameters, node.returnType, source, owner, address)
            fields.update(
                name=node.name, pipeline=[{} for _ in node.steps],
                annotations=self._include_annotations(node, ScopeEnum.FLOW, owner, address),
            )
            self._add(node, "flow", owner, address, fields)
            for index, step in enumerate(node.steps):
                self._step(step, self._step_owner(owner, step, index), address + ("pipeline", index))

        for node in source.strategies:
            owner = f"{namespace}.{node.name}"
            address = prefix + ("strategies", node.name)
            fields = self._signature(node.inputs, node.output, source, owner, address)
            fields.update(name=node.name, algorithm=node.algorithm, clauses=self._serialized(node.clauses))
            fields["annotations"] = self._include_annotations(node, ScopeEnum.FLOW, owner, address)
            self._add(node, "strategy", owner, address, fields)
            for index, (clause, annotations) in enumerate(zip(node.clauses, node.clauseAnnotations)):
                pointer = address + ("clauses", index)
                fields = self._serialized(clause)
                fields["annotations"] = self._include_annotations(
                    SimpleNamespace(annotations=annotations), ScopeEnum.FLOW, owner, pointer,
                )
                self._add(clause, clause["kind"].lower(), owner, pointer, fields, map_location=False)

        for node in source.decisions:
            owner = f"{namespace}.{node.name}"
            address = prefix + ("decisions", node.name)
            self._add(node, "decision", owner, address, {
                "name": node.name, "chosen": node.chosen, "rationale": node.rationale or "",
                "alternatives": node.alternatives,
                "annotations": self._include_annotations(node, ScopeEnum.GLOBAL, owner, address),
            })
        for node in source.contracts:
            self._contract(node, source, namespace)
        for node in source.models:
            self._root(node, "models", "model", namespace, ScopeEnum.COMPONENT,
                       {"name": node.name, "modelType": node.type, "modelFile": node.file,
                        "verifies": node.verifies, "assumptions": node.assumptions})
        for node in source.assumptions:
            self._root(node, "assumptions", "assumption", namespace, ScopeEnum.COMPONENT,
                       {"name": node.name, "affected": node.affects, "consequence": node.consequence})
        for node in source.constraints:
            scope = ScopeEnum.LOCAL if node.scope == "LOCAL" else ScopeEnum.GLOBAL
            self._root(node, "globalConstraints", node.kind.lower(), namespace, scope,
                       {"name": node.name, "text": node.text, "scope": node.scope})
        for node in source.ensures:
            self._root(node, "postconditions", "postcondition", namespace, ScopeEnum.GLOBAL,
                       {"expression": node.expression})
        for node in source.matches:
            address = self._root_address("matches")
            self._match(node, f"{namespace}.match[{address[-1] + 1}]", address, None)

    def _contract(self, node, source, namespace):
        owner = f"{namespace}.{node.name}"
        address = self._root_address("contracts")
        self._parameters(node.inputs, source, owner, address + ("parameters",))
        self._add(node, "contract", owner, address, {
            "name": node.name, "inputs": self._serialized([asdict(param) for param in node.inputs]),
            "output": self._serialized(asdict(node.output)) if node.output else None,
            "parameters": [{} for _ in node.inputs],
            "resultType": self._type(node.output, source, address + ("resultType",), owner),
            "cases": [{} for _ in node.behaviors],
            "idempotent": node.idempotent, "version": node.version,
            "annotations": self._include_annotations(node, ScopeEnum.COMPONENT, owner, address),
        })
        for index, case in enumerate(node.behaviors.values()):
            case_owner = f"{owner}.{case.name}"
            pointer = address + ("cases", index)
            self._add(case, "case", case_owner, pointer, self._serialized(asdict(case)), map_location=False)
            for guard_index, guard in enumerate(case.when):
                self._add(guard, "guard", case_owner, pointer + ("when", guard_index),
                          self._serialized(asdict(guard)), map_location=False)
            for clause_index, clause in enumerate(case.clauses):
                target = pointer + ("clauses", clause_index)
                self._add(clause, clause["type"].lower(), case_owner, target,
                          self._serialized(clause), map_location=False)
                if "predicate" in clause:
                    self._add(clause["predicate"], "predicate", case_owner, target + ("predicate",),
                              self._serialized(clause["predicate"]), map_location=False)

    def _root(self, node, collection, kind, namespace, scope, fields):
        owner = namespace
        address = self._root_address(collection)
        fields["annotations"] = self._include_annotations(node, scope, owner, address)
        self._add(node, kind, owner, address, fields)

    def reconcile(self, artifact):
        if artifact.get("provenance", {}).get("sources") != self.sources:
            raise CPCReconciliationError(self.first, "source file inventory changed")
        for occurrence in self.occurrences:
            value = artifact
            try:
                for part in occurrence.address:
                    value = value[part]
            except (KeyError, IndexError, TypeError):
                raise CPCReconciliationError(occurrence, "semantic construct is missing or moved") from None
            field = _difference(occurrence.fields, value)
            if field:
                raise CPCReconciliationError(occurrence, f"semantic {field} differs from the source")
        for name, count in self.root_counts.items():
            if len(artifact.get(name, ())) != count:
                raise CPCReconciliationError(self.first, f"unexpected occurrence count in {name}")
        for namespace, groups in self.declarations.items():
            actual = artifact.get("namespaces", {}).get(namespace, {})
            for kind, names in groups.items():
                declarations = actual.get(kind, {})
                actual_names = set(declarations)
                if namespace == "global" and kind == "types":
                    actual_names.difference_update(
                        name for name in BuiltinTypeRegistry.TYPE_NAMES
                        if (declarations.get(name) or {}).get("sourceMap", {}).get("file") == "builtin"
                    )
                if actual_names != names:
                    raise CPCReconciliationError(self.first, f"unexpected declarations in {namespace}.{kind}")
        return [occurrence.record() for occurrence in sorted(
            self.occurrences, key=lambda item: (item.path, item.line, item.column, item.owner, item.kind)
        )]

    def check_serialized(self, artifact, serialized, marker):
        expected = self.reconcile(artifact)
        if artifact.get("source_inventory_version") != VERSION or artifact.get("source_inventory") != expected:
            raise CPCReconciliationError(self.first, "serialized occurrence inventory changed")
        semantic_validate = artifact.get("semantic_validate")
        if not isinstance(semantic_validate, dict) or _difference(marker, semantic_validate):
            raise CPCReconciliationError(self.first, "semantic validation marker changed")
        if _difference(content_fingerprints(artifact), semantic_validate):
            raise CPCReconciliationError(self.first, "semantic content fingerprint changed")
        digest = semantic_validate.get(BYTE_HASH_KEY)
        if not isinstance(digest, str) or len(digest) != 128:
            raise CPCReconciliationError(self.first, "embedded byte fingerprint is missing")
        before, separator, after = serialized.rpartition(f'"{digest}"')
        zeroed = f'{before}"{"0" * 128}"{after}'.encode("utf-8")
        if not separator or sha512(zeroed).hexdigest() != digest:
            raise CPCReconciliationError(self.first, "embedded byte fingerprint differs from the delivered AST")
