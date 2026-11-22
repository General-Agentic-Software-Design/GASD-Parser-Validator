"""Verify GASD 1.2 contracts against raw arguments and observed outcomes."""

import operator
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID

from .ContractValidator import literal_type_value, parse_timing


VOID = object()
_UNAVAILABLE = object()
_NUMERIC = (int, float, Decimal)
_COMPARE = {
    "<": operator.lt, ">": operator.gt, "<=": operator.le, ">=": operator.ge,
}
_ARITHMETIC = {
    "+": operator.add, "-": operator.sub, "*": operator.mul,
    "/": operator.truediv, "^": operator.pow,
}


@dataclass
class CallObservation:
    """A normal, Result success/failure, or exceptional completion.

    Use VOID for the unit value and None for an observed null. Quoted evidence
    is a mapping from case name to zero-based postcondition index to bool.
    """

    completion_mode: str
    payload: object = _UNAVAILABLE
    exception_type: str = None
    partial_result: object = _UNAVAILABLE
    elapsed_ms: float = None
    additional_attempts: int = None
    quoted_evidence: Mapping = field(default_factory=dict)


@dataclass
class VerificationReport:
    status: str
    case_names: list = field(default_factory=list)
    diagnostics: list = field(default_factory=list)


class GuardEvaluationError(ValueError):
    """A reached guard could not be evaluated using the supplied arguments."""

    def __init__(self, diagnostics):
        self.diagnostics = sorted(diagnostics)
        super().__init__("\n".join(self.diagnostics))


class _MissingBinding(ValueError):
    pass


class _MissingEvidence(ValueError):
    pass


def _get(node, name, default=None):
    if isinstance(node, Mapping):
        return node.get(name, default)
    return getattr(node, name, default)


def _all_cases(contract):
    cases = _get(contract, "cases")
    if cases is None:
        cases = _get(contract, "behaviors", ())
    return cases.values() if isinstance(cases, Mapping) else cases


def _lookup(values, path):
    value = values
    for field_name in path.split("."):
        if isinstance(value, Mapping):
            value = value.get(field_name, _UNAVAILABLE)
        else:
            value = getattr(value, field_name, _UNAVAILABLE)
        if value is _UNAVAILABLE:
            raise _MissingBinding(f"'{path}' is unavailable")
    return value


def _strict_equal(left, right):
    if type(left) is not type(right):
        return False
    if isinstance(left, (list, tuple)):
        return len(left) == len(right) and all(_strict_equal(a, b) for a, b in zip(left, right))
    if isinstance(left, Mapping):
        return len(left) == len(right) and all(
            any(_strict_equal(key, other_key) and _strict_equal(value, other_value)
                for other_key, other_value in right.items())
            for key, value in left.items()
        )
    return left == right


def _is_uuid(value):
    if isinstance(value, UUID):
        return True
    if not isinstance(value, str) or len(value) != 36:
        return False
    try:
        return str(UUID(value)) == value.lower()
    except ValueError:
        return False


def _is_datetime(value):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
        except ValueError:
            return False
    return isinstance(value, datetime) and value.utcoffset() == timedelta(0)


def _matches_type(value, expression, type_checks):
    optional = _get(expression, "isOptional", False)
    base = _get(expression, "baseType")
    if optional and value is None:
        return True
    args = _get(expression, "genericArgs") or ()
    if base == "Any":
        return True
    if base == "Void":
        return value is VOID
    if base == "literal":
        return _strict_equal(value, literal_type_value(_get(expression, "literalValue")))
    if base == "Enum":
        return any(_strict_equal(value, literal_type_value(item))
                   for item in _get(expression, "enumValues") or ())
    if base == "List":
        return isinstance(value, list) and all(_matches_type(item, args[0], type_checks) for item in value)
    if base == "Map":
        return isinstance(value, Mapping) and all(
            _matches_type(key, args[0], type_checks) and _matches_type(item, args[1], type_checks)
            for key, item in value.items()
        )
    if base == "Result" and isinstance(value, CallObservation):
        return value.completion_mode == "failure" or (
            value.completion_mode == "success" and value.payload is not _UNAVAILABLE
            and _matches_type(value.payload, args[0], type_checks)
        )
    if base == "UUID":
        return _is_uuid(value)
    if base == "DateTime":
        return _is_datetime(value)
    builtin = {
        "String": str, "Integer": int, "Int": int, "Int32": int,
        "Float": float, "Decimal": Decimal, "Boolean": bool, "Bytes": bytes, "Date": date,
    }.get(base)
    if builtin is not None:
        return type(value) is builtin
    if base in type_checks:
        matched = type_checks[base](value)
        if type(matched) is not bool:
            raise ValueError(f"type check for '{base}' must return a Boolean")
        return matched
    if isinstance(value, Mapping):
        raise _MissingEvidence(f"no type check for '{base}'")
    return value is not None and base in {
        type(value).__name__, f"{type(value).__module__}.{type(value).__qualname__}",
    }


def _is_number(value):
    return type(value) in _NUMERIC


def _evaluate_operand(operand, bindings, functions):
    kind = operand["kind"]
    value = operand.get("value")
    if kind == "reference":
        return _lookup(bindings, value)
    if kind == "float":
        return float(value)
    if kind == "void":
        return VOID
    if kind == "arithmetic":
        left, right = [_evaluate_operand(item, bindings, functions) for item in operand["operands"]]
        if not (_is_number(left) and _is_number(right)):
            raise ValueError("arithmetic requires numeric operands")
        return _ARITHMETIC[operand["operator"]](left, right)
    if kind == "call":
        operands = [_evaluate_operand(item, bindings, functions) for item in operand["operands"]]
        if value not in functions:
            raise _MissingEvidence(f"no evaluator for '{value}'")
        return functions[value](*operands)
    return value


def _evaluate(predicate, bindings, type_checks, functions):
    op = _get(predicate, "operator")
    right_operand = _get(predicate, "right_operand")
    left = _evaluate_operand(_get(predicate, "left_operand"), bindings, functions)
    if op == "IS":
        return _matches_type(left, right_operand["value"], type_checks)
    right = _evaluate_operand(right_operand, bindings, functions)
    if op == "==":
        return _strict_equal(left, right)
    if op == "!=":
        return not _strict_equal(left, right)
    if not (_is_number(left) and _is_number(right)):
        raise ValueError(f"operator '{op}' requires numeric operands")
    return _COMPARE[op](left, right)


def select_eligible_cases(contract, arguments, *, type_checks=None):
    """Evaluate guards before argument validation or invocation.

    Accept a contract node or either form of exported contract. Optional type
    checks adapt custom GASD types to the observer's runtime representation.
    """
    type_checks = type_checks or {}
    eligible = []
    diagnostics = []
    for case in _all_cases(contract):
        for index, guard in enumerate(_get(case, "when", ()), 1):
            try:
                if not _evaluate(guard, arguments, type_checks, {}):
                    break
            except Exception as error:
                diagnostics.append(f"CASE '{_get(case, 'name')}' WHEN {index}: {error}")
                break
        else:
            eligible.append(case)
    if diagnostics:
        raise GuardEvaluationError(diagnostics)
    return eligible


def _bindings(arguments, observation):
    bindings = dict(arguments)
    # Outcome bindings shadow any matching argument names in postconditions.
    bindings.pop("result", None)
    bindings.pop("error", None)
    mode = observation.completion_mode
    if mode == "failure":
        bindings["error"] = observation.payload
    elif mode == "exception":
        bindings["error"] = observation.payload
        if observation.payload is _UNAVAILABLE and observation.exception_type:
            bindings["error"] = {"type": observation.exception_type}
        bindings["result"] = observation.partial_result
    else:
        bindings["result"] = observation.payload
    return bindings


def _timing(value, observation):
    timing = parse_timing(value)
    if timing is None:
        return None
    kind, required = timing
    if kind == "duration":
        elapsed = observation.elapsed_ms
        return None if elapsed is None else _is_number(elapsed) and elapsed >= required
    attempts = observation.additional_attempts
    return None if attempts is None else type(attempts) is int and attempts == required


def _exception_matches(value, observation):
    if observation.exception_type is not None:
        return observation.exception_type == value
    if isinstance(observation.payload, BaseException):
        error_type = type(observation.payload)
        return value in {error_type.__name__, f"{error_type.__module__}.{error_type.__qualname__}"}
    return None


def _postcondition(clause, bindings, evidence, index, type_checks, functions):
    value = clause["value"]
    if clause.get("quoted") or (len(value) >= 2 and value[0] in "\"'" and value[0] == value[-1]
                                and "predicate" not in clause):
        return evidence.get(index)
    predicate = clause.get("predicate")
    if predicate is None:
        return {"true": True, "false": False}.get(value.lower())
    try:
        return _evaluate(predicate, bindings, type_checks, functions)
    except _MissingEvidence:
        return None
    except (AttributeError, TypeError, ValueError, ArithmeticError, KeyError):
        return False


def _case_outcome(case, bindings, observation, type_checks, functions):
    clauses = _get(case, "clauses", ())
    expected_error = next((clause["value"] for clause in clauses if clause["type"] == "THROWS"), None)
    exceptional = observation.completion_mode == "exception"
    if exceptional != (expected_error is not None):
        return False
    completion = _exception_matches(expected_error, observation) if exceptional else True
    if completion is False:
        return False

    evidence = observation.quoted_evidence.get(_get(case, "name"), {})
    missing_evidence = completion is None
    index = 0
    for clause in clauses:
        if clause["type"] == "POSTCONDITION":
            satisfied = _postcondition(clause, bindings, evidence, index, type_checks, functions)
            index += 1
        elif clause["type"] == "AFTER":
            satisfied = _timing(clause["value"], observation)
        else:
            continue
        if satisfied is False:
            return False
        if satisfied is not True:
            missing_evidence = True
    return None if missing_evidence else True


def verify_outcome(cases, arguments, observation, *, type_checks=None, functions=None):
    """Check a completion against previously selected eligible cases."""
    if observation.completion_mode not in {"normal", "success", "failure", "exception"}:
        raise ValueError(f"unknown completion mode '{observation.completion_mode}'")

    matches = []
    possible = []
    bindings = _bindings(arguments, observation)
    for case in cases:
        outcome = _case_outcome(case, bindings, observation, type_checks or {}, functions or {})
        if outcome is True:
            matches.append(_get(case, "name"))
        elif outcome is None:
            possible.append(_get(case, "name"))
    if matches:
        return VerificationReport("verified", sorted(matches))
    if possible:
        return VerificationReport("unverified", sorted(possible))
    return VerificationReport("violation")


def verify_call(contract, arguments, observation, *, type_checks=None, functions=None):
    """Select cases from the original arguments, then verify a recorded call."""
    try:
        cases = select_eligible_cases(contract, arguments, type_checks=type_checks)
    except GuardEvaluationError as error:
        return VerificationReport("verification_error", diagnostics=error.diagnostics)
    return verify_outcome(cases, arguments, observation, type_checks=type_checks, functions=functions)
