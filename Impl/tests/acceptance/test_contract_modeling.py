"""GEP-7 acceptance, design, regression, and rejection scenarios."""

import json
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
from uuid import UUID

import pytest

ROOT = Path(__file__).resolve().parents[3]
EXAMPLES = ROOT / "Specs/examples/gasd-1.2"


def write_spec(directory, name, source):
    path = directory / name
    path.write_text("VERSION 1.2\n" + dedent(source).lstrip(), encoding="utf-8")
    return path


def run_cli(path, *options):
    return subprocess.run(
        [sys.executable, "-m", "Impl.cli", "--gasd-ver", "1.2", *options, str(path)],
        cwd=ROOT, capture_output=True, text=True,
    )


def export_contracts(path, directory, mode="--ast-sem"):
    target = directory / "contract-ast.json"
    completed = run_cli(path, mode, "--ast-output", str(target))
    assert completed.returncode == 0, completed.stderr + completed.stdout
    data = json.loads(target.read_text(encoding="utf-8"))
    files = data if isinstance(data, list) else [data]
    return {contract["name"]: contract for file in files for contract in file["contracts"]}


def cases_by_name(contract):
    if "behaviors" in contract:
        return contract["behaviors"]
    return {case["name"]: case for case in contract["cases"]}


def test_typed_contract_signatures(tmp_path):
    """AT-GEP7-001."""
    write_spec(tmp_path, "common.gasd", """
        NAMESPACE: "test.common"
        TYPE OrderItem:
            sku: String
    """)
    source = write_spec(tmp_path, "orders.gasd", """
        IMPORT "common.gasd" AS Common
        COMPONENT OrderService:
            INTERFACE:
                submit(items: List<Common.OrderItem>, limit: Integer) -> Result<Void>
                reset() -> Void
        CONTRACT OrderService.submit:
            INPUT: items: List<Common.OrderItem>, limit: Integer
            OUTPUT: Result<Void>
            BEHAVIORS:
                CASE accepted:
                    POSTCONDITION: result == void
        CONTRACT OrderService.reset:
            OUTPUT: Void
            BEHAVIORS:
                CASE complete:
                    POSTCONDITION: result == void
    """)
    for mode in ("--ast-sem", "--no-validate"):
        contracts = export_contracts(source, tmp_path, mode)
        submit = contracts["OrderService.submit"]
        assert [parameter["name"] for parameter in submit["inputs"]] == ["items", "limit"]
        assert submit["inputs"][0]["type"]["genericArgs"][0]["baseType"] == "Common.OrderItem"
        assert submit["output"]["genericArgs"][0]["baseType"] == "Void"
        assert not contracts["OrderService.reset"]["inputs"]


def test_guards_round_trip_and_short_circuit(tmp_path):
    """AT-GEP7-002 and NT-GEP7-003."""
    source = write_spec(tmp_path, "order.gasd", """
        TYPE OrderRequest:
            quantity: Integer
        COMPONENT OrderService:
            INTERFACE:
                submit(request: OrderRequest) -> Void
        CONTRACT OrderService.submit:
            INPUT: request: OrderRequest
            OUTPUT: Void
            BEHAVIORS:
                CASE positive:
                    WHEN: request != null
                    WHEN: request.quantity > 0
                    POSTCONDITION: result == void
                CASE fallback:
                    POSTCONDITION: result == void
    """)
    for mode in ("--ast-sem", "--no-validate"):
        contract = export_contracts(source, tmp_path, mode)["OrderService.submit"]
        cases = cases_by_name(contract)
        assert [guard["operator"] for guard in cases["positive"]["when"]] == ["!=", ">"]
        assert cases["fallback"]["when"] == []

    from Impl.semantic.ContractVerifier import CallObservation, VOID, select_eligible_cases, verify_call

    assert {case["name"] for case in select_eligible_cases(contract, {"request": None})} == {"fallback"}
    assert {case["name"] for case in select_eligible_cases(contract, {"request": {"quantity": 1}})} == {
        "positive", "fallback",
    }
    report = verify_call(contract, {"request": {}}, CallObservation("normal", VOID))
    assert report.status == "verification_error"
    assert any("request.quantity" in diagnostic for diagnostic in report.diagnostics)


@pytest.fixture
def payment(tmp_path):
    return write_spec(tmp_path, "payment.gasd", """
        TYPE PaymentCustomer:
            status: String
            customerId: UUID
        COMPONENT PaymentService:
            INTERFACE:
                createCustomer(email: String) -> PaymentCustomer
        CONTRACT PaymentService.createCustomer:
            INPUT: email: String
            OUTPUT: PaymentCustomer
            BEHAVIORS:
                CASE success:
                    WHEN: email != null
                    POSTCONDITION: result.status == "ACTIVE"
                    POSTCONDITION: result.customerId IS UUID
                CASE service_failure:
                    WHEN: email != null
                    THROWS: PaymentGatewayException
                    AFTER: retry(2)
                CASE timeout:
                    WHEN: email != null
                    THROWS: PaymentGatewayException
                    AFTER: 3000ms
                CASE null_input:
                    WHEN: email == null
                    THROWS: IllegalArgumentException
    """)


def test_payment_cases_are_order_independent(payment, tmp_path):
    """AT-GEP7-003. Both eligible exceptional outcomes use the same exception type."""
    from Impl.semantic.ContractVerifier import CallObservation, verify_call

    contract = export_contracts(payment, tmp_path)["PaymentService.createCustomer"]
    reversed_contract = dict(contract, cases=list(reversed(contract["cases"])))
    customer = {"status": "ACTIVE", "customerId": UUID(int=4)}
    gateway = dict(exception_type="PaymentGatewayException")
    observations = [
        (None, CallObservation("exception", exception_type="IllegalArgumentException"), "verified", "null_input"),
        ("alice", CallObservation("normal", customer), "verified", "success"),
        ("alice", CallObservation("exception", elapsed_ms=100, additional_attempts=2, **gateway), "verified", "service_failure"),
        ("alice", CallObservation("exception", elapsed_ms=3000, additional_attempts=0, **gateway), "verified", "timeout"),
        ("alice", CallObservation("exception", elapsed_ms=2999, additional_attempts=3, **gateway), "violation", None),
        ("alice", CallObservation("exception", additional_attempts=0, **gateway), "unverified", "timeout"),
        (None, CallObservation("normal", customer), "violation", None),
    ]
    for email, observation, status, case in observations:
        report = verify_call(contract, {"email": email}, observation)
        assert report.status == status
        assert report.case_names == ([case] if case else [])
        assert report == verify_call(reversed_contract, {"email": email}, observation)


def test_missing_and_disproved_quoted_evidence(tmp_path):
    """AT-GEP7-004."""
    from Impl.semantic.ContractVerifier import CallObservation, verify_call

    source = write_spec(tmp_path, "counter.gasd", """
        COMPONENT Counter:
            INTERFACE:
                update(change: Integer) -> Integer
        CONTRACT Counter.update:
            INPUT: change: Integer
            OUTPUT: Integer
            BEHAVIORS:
                CASE changed:
                    WHEN: change > 0
                    POSTCONDITION: result > 0
                    POSTCONDITION: "The new state is persisted"
    """)
    contract = export_contracts(source, tmp_path)["Counter.update"]
    positive = {"change": 1}
    assert verify_call(contract, positive, CallObservation("normal", 1)).status == "unverified"
    assert verify_call(contract, positive, CallObservation("normal", -1)).status == "violation"
    assert verify_call(contract, {"change": 0}, CallObservation("normal", 1)).status == "violation"
    for is_true, status in ((True, "verified"), (False, "violation")):
        result = CallObservation("normal", 1, quoted_evidence={"changed": {1: is_true}})
        assert verify_call(contract, positive, result).status == status


def test_gasd_12_examples_individually_and_together():
    """RT-GEP7-001."""
    paths = sorted(EXAMPLES.rglob("*.gasd"))
    assert len(paths) >= 31
    for path in [*paths, EXAMPLES]:
        completed = run_cli(path, "--json")
        assert completed.returncode == 0, completed.stdout + completed.stderr
        report = json.loads(completed.stderr)
        assert report["success"] and report["failureCount"] == 0
        assert all(file["success"] and file["warningCount"] == 0 for file in report["reports"])
        if path == EXAMPLES:
            assert report["successCount"] == len(paths)
        else:
            assert any(file["sourceFile"] == str(path.relative_to(ROOT)) for file in report["reports"])


def test_inventory_release_has_independent_state_evidence(tmp_path):
    """RT-GEP7-002."""
    source = EXAMPLES / "multi-file/inventory_service.gasd"
    contract = export_contracts(source, tmp_path)["InventoryService.release_stock"]
    assert set(cases_by_name(contract)) == {"released", "failed"}

    from Impl.semantic.ContractVerifier import CallObservation, VOID, verify_call

    arguments = {"items": [{"sku": "A", "quantity": 3}]}
    stock, reservations = 4, {"order": 3}
    for expected_increase in (3, 0):
        before = stock
        stock += reservations.pop("order", 0)
        assert stock == before + expected_increase
        evidence = {"released": {1: stock == before + expected_increase}}
        observation = CallObservation("success", VOID, quoted_evidence=evidence)
        report = verify_call(contract, arguments, observation)
        assert report.status == "verified" and report.case_names == ["released"]
    observation = CallObservation("failure", {"reason": "unavailable"}, quoted_evidence={"failed": {1: True}})
    assert verify_call(contract, arguments, observation).case_names == ["failed"]
    assert verify_call(contract, arguments, CallObservation("success", VOID)).status == "unverified"


def validate_fragment(tmp_path, contract, interface="apply(value: Integer, label: String) -> Integer"):
    source = write_spec(tmp_path, "invalid.gasd", f"""
        COMPONENT Service:
            INTERFACE:
                {interface}
    """)
    with source.open("a", encoding="utf-8") as handle:
        handle.write(dedent(contract).lstrip())
    return run_cli(source, "--json")


VALID_HEADER = """CONTRACT Service.apply:
    INPUT: value: Integer, label: String
    OUTPUT: Integer
"""


@pytest.mark.parametrize("body", [
    "",
    "    BEHAVIORS:\n",
    "    BEHAVIORS:\n        CASE skipped:\n            WHEN: value > 0\n",
    "    BEHAVIORS:\n        CASE timed:\n            AFTER: 1s\n",
])
def test_lint007_requires_case_outcomes(tmp_path, body):
    """NT-GEP7-001."""
    completed = validate_fragment(tmp_path, VALID_HEADER + body)
    assert completed.returncode != 0
    assert "LINT-007" in completed.stdout + completed.stderr


@pytest.mark.parametrize("clause", [
    "INPUT: value: Integer, value: String",
    "INPUT: value: String, label: Integer",
    "INPUT: value: Integer",
    "INPUT: value: Integer, label: String, extra: Boolean",
])
def test_contract_input_signature_is_checked(tmp_path, clause):
    """NT-GEP7-002."""
    valid_behavior = "    BEHAVIORS:\n        CASE done:\n            POSTCONDITION: result == 1\n"
    header = VALID_HEADER.replace("INPUT: value: Integer, label: String", clause)
    assert validate_fragment(tmp_path, header + valid_behavior).returncode != 0


def test_duplicate_cases_and_output_type_are_checked(tmp_path):
    """NT-GEP7-002."""
    behavior = "    BEHAVIORS:\n        CASE done:\n            POSTCONDITION: result == 1\n"
    duplicate = behavior + "        CASE done:\n            POSTCONDITION: result == 2\n"
    assert validate_fragment(tmp_path, VALID_HEADER + duplicate).returncode != 0
    assert validate_fragment(tmp_path, VALID_HEADER.replace("OUTPUT: Integer", "OUTPUT: String") + behavior).returncode != 0


@pytest.mark.parametrize("clauses", [
    ('WHEN: missing == 1', 'POSTCONDITION: result == 1'),
    ('WHEN: result == 1', 'POSTCONDITION: result == 1'),
    ('WHEN: value.missing == 1', 'POSTCONDITION: result == 1'),
    ('WHEN: label > "prefix"', 'POSTCONDITION: result == 1'),
    ('WHEN: true <= 1', 'POSTCONDITION: result == 1'),
    ('WHEN: value IS MissingType', 'POSTCONDITION: result == 1'),
    ('WHEN: label.get() == 1', 'POSTCONDITION: result == 1'),
    ('POSTCONDITION: result == 1', 'WHEN: value > 0'),
    ('THROWS: Earlier', 'THROWS: Later'),
    ('POSTCONDITION: result == 1', 'AFTER: 1s', 'AFTER: 2s'),
    ('THROWS: Failure', 'AFTER: retry(-1)'),
    ('THROWS: Failure', 'AFTER: retry(true)'),
    ('THROWS: Failure', 'AFTER: retry(2.5)'),
    ('THROWS: Failure', 'AFTER: retry(1, 2)'),
    ('THROWS: Failure', 'AFTER: retry(1 2)'),
])
def test_invalid_guards_and_case_clauses(tmp_path, clauses):
    """NT-GEP7-001 and NT-GEP7-003."""
    behavior = "    BEHAVIORS:\n        CASE done:\n"
    behavior += "".join("            " + clause + "\n" for clause in clauses)
    assert validate_fragment(tmp_path, VALID_HEADER + behavior).returncode != 0


def test_qualified_throws_partial_result_and_timing(tmp_path):
    """AT-GEP7-003 and AT-GEP7-004."""
    from Impl.semantic.ContractVerifier import CallObservation, verify_call

    source = write_spec(tmp_path, "partial.gasd", """
        COMPONENT Worker:
            INTERFACE:
                start() -> Integer
        CONTRACT Worker.start:
            OUTPUT: Integer
            BEHAVIORS:
                CASE interrupted:
                    THROWS: Common.WorkError
                    POSTCONDITION: result >= 4
                    POSTCONDITION: error.code == 12
                    AFTER: 1m
    """)
    contract = export_contracts(source, tmp_path)["Worker.start"]
    observed = dict(payload={"code": 12}, exception_type="Common.WorkError", partial_result=4)
    assert verify_call(contract, {}, CallObservation("exception", **observed, elapsed_ms=60000)).status == "verified"
    assert verify_call(contract, {}, CallObservation("exception", **observed, elapsed_ms=59999)).status == "violation"
    assert verify_call(contract, {}, CallObservation("exception", **observed)).status == "unverified"
    observed.pop("partial_result")
    assert verify_call(contract, {}, CallObservation("exception", **observed, elapsed_ms=60000)).status == "violation"


def test_guards_affect_hash_independent_of_source_location(tmp_path):
    """AC-V2-004-05."""
    text = """
        COMPONENT Limit:
            INTERFACE:
                check(value: Integer) -> Boolean
        CONTRACT Limit.check:
            INPUT: value: Integer
            OUTPUT: Boolean
            BEHAVIORS:
                CASE allowed:
                    WHEN: value > 0
                    WHEN: value < 5
                    POSTCONDITION: result == true
    """
    first = write_spec(tmp_path, "first.gasd", text)
    shifted = write_spec(tmp_path, "shifted.gasd", "// Shift source locations\n" + dedent(text))
    different = write_spec(tmp_path, "different.gasd", text.replace("value < 5", "value < 6"))
    reversed_guards = write_spec(tmp_path, "reversed.gasd", text.replace("value > 0", "value < 5", 1).replace("WHEN: value < 5\n                    POSTCONDITION", "WHEN: value > 0\n                    POSTCONDITION"))
    hashes = [export_contracts(path, tmp_path)["Limit.check"]["hash"]
              for path in (first, shifted, different, reversed_guards)]
    assert len(hashes[0]) == 64
    assert hashes[0] == hashes[1]
    assert hashes[0] != hashes[2] and hashes[0] != hashes[3]


def test_generic_guard_is_and_strict_equality(tmp_path):
    """AT-GEP7-003. Boolean values do not satisfy Integer predicates."""
    from Impl.semantic.ContractVerifier import CallObservation, verify_call

    source = write_spec(tmp_path, "numbers.gasd", """
        COMPONENT Numbers:
            INTERFACE:
                check(values: Any, flag: Any) -> Boolean
        CONTRACT Numbers.check:
            INPUT: values: Any, flag: Any
            OUTPUT: Boolean
            BEHAVIORS:
                CASE integers:
                    WHEN: values IS List<Integer>
                    WHEN: flag != 1
                    POSTCONDITION: result == true
    """)
    contract = export_contracts(source, tmp_path)["Numbers.check"]
    observation = CallObservation("normal", True)
    assert verify_call(contract, {"values": [1], "flag": True}, observation).status == "verified"
    assert verify_call(contract, {"values": [True], "flag": True}, observation).status == "violation"
    assert verify_call(contract, {"values": [1], "flag": 1}, observation).status == "violation"
