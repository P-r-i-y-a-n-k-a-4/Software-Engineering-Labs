
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles


def test_invalid_manifests():
    try:
        process_commute_manifest("invalid", 2.0)
        assert False
    except ValueError:
        assert True


def test_negative_fee():
    try:
        process_commute_manifest([], -1)
        assert False
    except ValueError:
        assert True


def test_inactive_route():
    result = process_commute_manifest(
        [{"route_active": False}], 2.0
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_express_route():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "express",
          "commuters": [{"zones": 1}]}], 2.0
    )
    assert result["status"] == "COMPLETED"


def test_shuttle_route():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "shuttle",
          "commuters": [{"zones": 1}]}], 2.0
    )
    assert result["status"] == "COMPLETED"


def test_local_route():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "local",
          "commuters": [{"zones": 1}]}], 2.0
    )
    assert result["status"] == "COMPLETED"


def test_unknown_route():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "unknown"}], 2.0
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_default_route():
    result = process_commute_manifest(
        [{"route_active": True,
          "commuters": [{"zones": 1}]}], 2.0
    )
    assert result["status"] == "COMPLETED"


def test_invalid_zones():
    result = process_commute_manifest(
        [{"route_active": True,
          "commuters": [{"zones": 0}]}], 2.0
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_valid_zones():
    result = process_commute_manifest(
        [{"route_active": True,
          "commuters": [{"zones": 2}]}], 2.0
    )
    assert result["status"] == "COMPLETED"


def test_blacklisted_express():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "express",
          "commuters": [{"blacklisted": True}]}], 2.0
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_blacklisted_non_express():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "local",
          "commuters": [{"blacklisted": True}]}], 2.0
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_student():
    result = process_commute_manifest(
        [{"route_active": True,
          "commuters": [{"type": "student", "zones": 1}]}], 2.0
    )
    assert result["status"] == "COMPLETED"


def test_senior():
    result = process_commute_manifest(
        [{"route_active": True,
          "commuters": [{"type": "senior", "zones": 1}]}], 2.0
    )
    assert result["status"] == "COMPLETED"


def test_regular():
    result = process_commute_manifest(
        [{"route_active": True,
          "commuters": [{"type": "regular", "zones": 1}]}], 2.0
    )
    assert result["status"] == "COMPLETED"


def test_priority_enabled():
    result = process_commute_manifest(
        [{"route_active": True, "priority_boarding": True,
          "commuters": [{"zones": 1}]}], 2.0
    )
    assert result["status"] == "COMPLETED"


def test_priority_disabled():
    result = process_commute_manifest(
        [{"route_active": True, "priority_boarding": False,
          "commuters": [{"zones": 1}]}], 2.0
    )
    assert result["status"] == "COMPLETED"


def test_audit_rejected():
    manifests = [
        {"route_active": True, "route_type": "unknown"}
        for _ in range(5)
    ]
    result = process_commute_manifest(manifests, 2.0)
    assert result["status"] == "AUDIT_REJECTED"


def test_zero_ridership():
    result = process_commute_manifest([], 2.0)
    assert result["status"] == "ZERO_RIDERSHIP"


def test_completed():
    result = process_commute_manifest(
        [{"route_active": True,
          "commuters": [{"zones": 1}]}], 2.0
    )
    assert result["status"] == "COMPLETED"


def test_no_turnstile_data():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"


def test_turnstile_failure():
    assert inspect_smartcard_turnstiles([[4]]) == "OPERATIONAL"


def test_turnstile_failure_reset():
    assert inspect_smartcard_turnstiles([[4, 1, 4]]) == "OPERATIONAL"


def test_turnstile_jam():
    assert inspect_smartcard_turnstiles([[4, 4]]) == "TURNSTILE_JAM"


def test_turnstile_operational():
    assert inspect_smartcard_turnstiles([[1, 2, 3]]) == "OPERATIONAL"
