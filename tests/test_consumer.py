import json

import pytest

from consumer import parse_message


def test_reads_mixed_formats():
    expected = {"temperatura": 56.32, "humedad": 51, "direccion_viento": "SO"}
    for payload in (json.dumps(expected).encode(), bytes.fromhex("58 01 9b")):
        assert parse_message(payload) == expected


@pytest.mark.parametrize("payload", [None, b"", b"[]", b"{}", b"null", b"\xff\xff\xff", b'{"temperatura": NaN}'])
def test_rejects_invalid_readings(payload):
    with pytest.raises(ValueError):
        parse_message(payload)
