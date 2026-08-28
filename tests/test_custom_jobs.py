"""Tests for custom job creation and validation."""
import pytest
from pydantic import ValidationError
from common.models.job import JobCreate, JobCreateCustom
from common.enums import JobType


def test_standard_job_rejects_invalid_track():
    with pytest.raises(ValidationError):
        JobCreate(
            title="Bad Track Job",
            job_type=JobType.FREIGHT,
            origin_track="invalid-track",   # fails regex
            destination_track="CS-B2S",
            reward=100,
        )


def test_standard_job_accepts_valid_tracks():
    job = JobCreate(
        title="Valid Freight",
        job_type=JobType.FREIGHT,
        origin_track="GF-A1L",
        destination_track="CS-B2S",
        reward=500,
    )
    assert job.origin_track == "GF-A1L"


def test_custom_job_bypasses_track_validation():
    """Custom jobs may use free-text routing points."""
    job = JobCreateCustom(
        title="Mod Sonderzug",
        job_type=JobType.CUSTOM,
        origin_track="FREITEXT-DEPOT-A",
        destination_track="MODDED-STATION-X",
        cargo_description="Spezialgüter",
        reward=9999,
        is_custom=True,
    )
    assert job.is_custom is True
    assert job.job_type == JobType.CUSTOM


def test_custom_job_flagged_correctly():
    job = JobCreateCustom(title="Sonderlauf", job_type=JobType.CUSTOM,
                          origin_track="ANY", destination_track="WHERE")
    assert job.is_custom is True


def test_job_reward_cannot_be_negative():
    with pytest.raises(ValidationError):
        JobCreate(
            title="Negative Reward",
            job_type=JobType.LOGISTICS,
            origin_track="GF-A1L",
            destination_track="HB-B1O",
            reward=-50,
        )


def test_job_wagon_count_cannot_be_negative():
    with pytest.raises(ValidationError):
        JobCreate(
            title="Negative Wagons",
            job_type=JobType.SHUNTING,
            origin_track="GF-A1L",
            destination_track="GF-A2L",
            wagon_count=-1,
        )
