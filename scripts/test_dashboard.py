"""Verification runner for the Chittoor Environmental Intelligence Dashboard.

Executes automated tests validating data contracts, schema integrity, forecast boundaries,
stress score bounds, and data immutability.
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def run_tests() -> bool:
    print("=" * 70)
    print("CHITTOOR ENVIRONMENTAL INTELLIGENCE DASHBOARD VERIFICATION SUITE")
    print("=" * 70)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Python: {sys.executable}")
    print("-" * 70)

    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(PROJECT_ROOT / "dashboard" / "tests"),
        pattern="test_*.py"
    )

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("-" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
