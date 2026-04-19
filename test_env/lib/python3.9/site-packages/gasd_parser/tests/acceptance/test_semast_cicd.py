import pytest
from .test_semast_hashing import (
    test_semast_hash_generation,
    test_semast_hash_whitespace_independence,
    test_semast_hash_recursion,
    test_semast_drift_detection,
    test_semast_determinism_guard,
    test_semast_hash_regression_order_independence
)

def test_semast_cicd_hash_generation():
    test_semast_hash_generation()

def test_semast_cicd_whitespace_independence():
    test_semast_hash_whitespace_independence()

def test_semast_cicd_recursion():
    test_semast_hash_recursion()

def test_semast_cicd_drift_detection():
    test_semast_drift_detection()

def test_semast_cicd_determinism():
    test_semast_determinism_guard()

def test_semast_cicd_order_independence():
    test_semast_hash_regression_order_independence()
