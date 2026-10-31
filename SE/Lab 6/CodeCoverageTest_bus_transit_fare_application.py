
import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles


def test_invalid_manifests():
    with pytest.raises(ValueError):
        process_commute_manifest("invalid", 2.0)


def test_negative_booking_fee():
    with pytest.raises(ValueError):
        process_commute_manifest([], -1)


def test_inactive_route():
    result = process_commute_manifest(
        [{"route_active": False}], 2.0
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_all_route_types():
    manifests = [
        {"route_active": True, "route_type": "express",
         "commuters": [{"zones": 1, "type": "regular"}]},
        {"route_active": True, "route_type": "shuttle",
         "commuters": [{"zones": 1, "type": "regular"}]},
        {"route_active": True, "route_type": "local",
         "commuters": [{"zones": 1, "type": "regular"}]},
    ]
    result = process_commute_manifest(manifests, 2.0)
    assert result["status"] == "COMPLETED"


def test_unknown_route():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "unknown"}], 2.0
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_empty_commuters():
    result = process_commute_manifest(
        [{"route_active": True, "commuters": []}], 2.0
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_invalid_zones():
    result = process_commute_manifest(
        [{"route_active": True,
          "commuters": [{"zones": 0}]}], 2.0
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_passenger_types():
    manifests = [{
        "route_active": True,
        "route_type": "local",
        "commuters": [
            {"zones": 2, "type": "student"},
            {"zones": 2, "type": "senior"},
            {"zones": 2, "type": "regular"}
        ]
    }]
    result = process_commute_manifest(manifests, 2.0)
    assert result["status"] == "COMPLETED"


def test_blacklisted_local_commuter():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "local",
          "commuters": [{"blacklisted": True}]}], 2.0
    )
    assert result["status"] == "ZERO_RIDERSHIP"


def test_blacklisted_express_commuter():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "express",
          "commuters": [
              {"zones": 1, "type": "regular"},
              {"zones": 1, "blacklisted": True},
              {"zones": 1, "type": "regular"}
          ]}], 2.0
    )
    assert result["status"] == "ZERO_RIDERSHIP"
    assert result["total_fare"] == 0.0

def test_priority_boarding():
    result = process_commute_manifest(
        [{"route_active": True, "route_type": "local",
          "priority_boarding": True,
          "commuters": [{"zones": 1}]}], 2.0
    )
    assert result["total_fare"] == 5.5


def test_audit_rejected():
    manifests = [
        {"route_active": True, "route_type": "unknown"}
        for _ in range(5)
    ]
    result = process_commute_manifest(manifests, 2.0)
    assert result["status"] == "AUDIT_REJECTED"


def test_completed_status():
    result = process_commute_manifest(
        [{"route_active": True, "commuters": [{"zones": 1}]}], 2.0
    )
    assert result["status"] == "COMPLETED"


def test_no_turnstile_data():
    assert inspect_smartcard_turnstiles([]) == "NO_DATA"


def test_turnstile_operational():
    assert inspect_smartcard_turnstiles([[1, 2, 3, 1]]) == "OPERATIONAL"


def test_turnstile_failure_reset():
    assert inspect_smartcard_turnstiles([[4, 1, 4]]) == "OPERATIONAL"


def test_turnstile_jam():
    assert inspect_smartcard_turnstiles([[4, 4]]) == "TURNSTILE_JAM"


def test_multiple_turnstiles():
    assert inspect_smartcard_turnstiles([[4], [1, 2, 3]]) == "OPERATIONAL"
