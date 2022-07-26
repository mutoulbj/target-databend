"""Tests standard target features using the built-in SDK tests library."""

import os

from typing import Dict, Any

from singer_sdk.testing import get_standard_target_tests

from target_databend.target import TargetDatabend
from target_databend.connector import get_connection

SAMPLE_CONFIG: Dict[str, Any] = {
    "host": os.environ.get("TARGET_DATABEND_HOST", "localhost"),
    "port": os.environ.get("TARGET_DATABEND_PORT", "3307"),
    "user": os.environ.get("TARGET_DATABEND_USER", "root"),
    "password": os.environ.get("TARGET_DATABEND_PASSWORD", ""),
    "dbname": os.environ.get("TARGET_DATABEND_DBNAME", ""),
    "charset": "utf8",
}


# Run standard built-in target tests from the SDK:
def test_standard_target_tests():
    """Run standard target tests from the SDK."""
    tests = get_standard_target_tests(
        TargetDatabend,
        config=SAMPLE_CONFIG,
    )
    for test in tests:
        test()


# TODO: Create additional tests as appropriate for your target.
def test_connection():
    conn = get_connection(config=SAMPLE_CONFIG)
    with conn.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1
