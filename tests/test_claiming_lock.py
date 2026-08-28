"""Tests for atomic job claiming – verifies no race condition double-claims."""
import asyncio
import pytest
from unittest.mock import MagicMock
from backend.services.claim_service import claim_job, release_job
from backend.database.models import JobORM
from common.enums import JobStatus


def _make_db_mock(job: JobORM):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = job
    db.commit = MagicMock()
    db.refresh = MagicMock()
    return db


@pytest.mark.asyncio
async def test_single_claim_succeeds():
    job = JobORM(id=1, job_id="GF-LOG-001", title="Test", job_type="LOG",
                 origin_track="GF-A1L", destination_track="CS-B2S",
                 status=JobStatus.UNCLAIMED, cargo_description="",
                 wagon_count=0, total_weight_tons=0, total_length_m=0,
                 reward=100, is_custom=False)
    db = _make_db_mock(job)
    result = await claim_job(job_id=1, player_id=42, username="player_b", db=db)
    assert result.success
    assert job.status == JobStatus.CLAIMED
    assert job.claimed_by_username == "player_b"


@pytest.mark.asyncio
async def test_double_claim_rejected():
    """Simulates two concurrent claim attempts for the same job."""
    job = JobORM(id=2, job_id="GF-LOG-002", title="Test2", job_type="LOG",
                 origin_track="GF-A1L", destination_track="HB-B1O",
                 status=JobStatus.UNCLAIMED, cargo_description="",
                 wagon_count=0, total_weight_tons=0, total_length_m=0,
                 reward=200, is_custom=False)
    db = _make_db_mock(job)

    results = await asyncio.gather(
        claim_job(job_id=2, player_id=1, username="player_b", db=db),
        claim_job(job_id=2, player_id=2, username="player_c", db=db),
    )
    successes = [r for r in results if r.success]
    assert len(successes) == 1, "Exactly one player must win the claim"


@pytest.mark.asyncio
async def test_release_by_owner_succeeds():
    job = JobORM(id=3, job_id="GF-FR-003", title="Test3", job_type="FR",
                 origin_track="GF-A1L", destination_track="CS-B2S",
                 status=JobStatus.CLAIMED, cargo_description="",
                 wagon_count=0, total_weight_tons=0, total_length_m=0,
                 reward=300, is_custom=False,
                 claimed_by_player_id=5, claimed_by_username="player_b")
    db = _make_db_mock(job)
    result = await release_job(job_id=3, player_id=5, role="Operator", db=db)
    assert result.success


@pytest.mark.asyncio
async def test_release_by_other_operator_rejected():
    job = JobORM(id=4, job_id="GF-FR-004", title="Test4", job_type="FR",
                 origin_track="GF-A1L", destination_track="CS-B2S",
                 status=JobStatus.CLAIMED, cargo_description="",
                 wagon_count=0, total_weight_tons=0, total_length_m=0,
                 reward=300, is_custom=False,
                 claimed_by_player_id=5, claimed_by_username="player_b")
    db = _make_db_mock(job)
    result = await release_job(job_id=4, player_id=99, role="Operator", db=db)
    assert not result.success


@pytest.mark.asyncio
async def test_admin_can_force_release():
    job = JobORM(id=5, job_id="GF-FR-005", title="Test5", job_type="FR",
                 origin_track="GF-A1L", destination_track="CS-B2S",
                 status=JobStatus.CLAIMED, cargo_description="",
                 wagon_count=0, total_weight_tons=0, total_length_m=0,
                 reward=300, is_custom=False,
                 claimed_by_player_id=5, claimed_by_username="player_b")
    db = _make_db_mock(job)
    result = await release_job(job_id=5, player_id=1, role="Admin", db=db)
    assert result.success
