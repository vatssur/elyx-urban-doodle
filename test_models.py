import pytest
from pydantic import ValidationError
from models import Activity, ActivityType

def test_activity_validation():
    # Valid
    act = Activity(
        id="a1", name="Running", type=ActivityType.FITNESS_ROUTINE,
        duration_minutes=30, frequency="DAILY", details="Run",
        facilitator_role=None, location="Park", remote_capable=True,
        prep_time_minutes=5, backup_activities=[], adjustments_if_skipped="none",
        metrics_to_collect=["hr"], resource_requirements=[]
    )
    assert act.name == "Running"
    assert act.transit_time_minutes == 0  # Default check
    assert act.priority == 0  # Default check

    # Invalid type
    with pytest.raises(ValidationError):
        Activity(
            id="a1", name="Running", type="INVALID_TYPE",
            duration_minutes=30, frequency="DAILY", details="Run",
            facilitator_role=None, location="Park", remote_capable=True,
            prep_time_minutes=5, backup_activities=[], adjustments_if_skipped="none",
            metrics_to_collect=["hr"], resource_requirements=[]
        )
