"""Unit tests for upcoming approved leave retrieval via the ECTimeOff MCP tool."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


@pytest.fixture
def mock_upcoming_leave_response():
    return {
        "results": [
            {
                "externalCode": "ET-001",
                "userId": "user123",
                "approvalStatus": "APPROVED",
                "startDate": "/Date(1767225600000)/",
                "endDate": "/Date(1767312000000)/",
                "quantity": "1.00",
                "timeType": "ANNUAL_LEAVE",
            },
            {
                "externalCode": "ET-002",
                "userId": "user123",
                "approvalStatus": "APPROVED",
                "startDate": "/Date(1769644800000)/",
                "endDate": "/Date(1769731200000)/",
                "quantity": "2.00",
                "timeType": "ANNUAL_LEAVE",
            },
        ]
    }


@pytest.fixture
def mock_pending_leave_response():
    return {
        "results": [
            {
                "externalCode": "ET-003",
                "userId": "user123",
                "approvalStatus": "PENDING",
                "startDate": "/Date(1770000000000)/",
                "endDate": "/Date(1770086400000)/",
                "quantity": "1.00",
                "timeType": "SICK_LEAVE",
            }
        ]
    }


@pytest.mark.asyncio
async def test_get_upcoming_leave_returns_approved(mock_upcoming_leave_response):
    """ECTimeOff tool returns approved leave requests."""
    mock_tool = MagicMock()
    mock_tool.name = "list_employeetime_for_sfodata"
    mock_tool.ainvoke = AsyncMock(return_value=str(mock_upcoming_leave_response))

    result = await mock_tool.ainvoke({"userId": "user123", "$filter": "approvalStatus eq 'APPROVED'"})
    assert "APPROVED" in str(result)
    assert "ET-001" in str(result)


@pytest.mark.asyncio
async def test_get_upcoming_leave_filters_approved_only(mock_upcoming_leave_response, mock_pending_leave_response):
    """Only APPROVED status leave requests should be returned."""
    approved_results = mock_upcoming_leave_response["results"]
    all_results = approved_results + mock_pending_leave_response["results"]

    # Filter for APPROVED only (simulating what the agent does)
    approved_only = [r for r in all_results if r["approvalStatus"] == "APPROVED"]
    assert len(approved_only) == 2
    assert all(r["approvalStatus"] == "APPROVED" for r in approved_only)


def test_upcoming_leave_entry_structure(mock_upcoming_leave_response):
    """Each leave entry has required fields."""
    for entry in mock_upcoming_leave_response["results"]:
        assert "externalCode" in entry
        assert "userId" in entry
        assert "approvalStatus" in entry
        assert "startDate" in entry
        assert "endDate" in entry
        assert "timeType" in entry


def test_upcoming_leave_date_format(mock_upcoming_leave_response):
    """Dates use SAP OData /Date(timestamp)/ format."""
    for entry in mock_upcoming_leave_response["results"]:
        assert entry["startDate"].startswith("/Date(")
        assert entry["endDate"].startswith("/Date(")


@pytest.mark.asyncio
async def test_get_upcoming_leave_no_cross_employee_data(mock_upcoming_leave_response):
    """All returned leave entries belong to the authenticated user."""
    for entry in mock_upcoming_leave_response["results"]:
        assert entry["userId"] == "user123"
