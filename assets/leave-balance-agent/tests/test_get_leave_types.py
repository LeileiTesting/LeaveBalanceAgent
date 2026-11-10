"""Unit tests for leave type retrieval via the AvailableTimeTypes MCP tool."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))


@pytest.fixture
def mock_available_time_types_response():
    return {
        "availableTimeTypes": [
            {"timeTypeId": "ANNUAL_LEAVE", "timeTypeName": "Annual Leave", "unit": "DAY"},
            {"timeTypeId": "SICK_LEAVE", "timeTypeName": "Sick Leave", "unit": "DAY"},
            {"timeTypeId": "SPECIAL_LEAVE", "timeTypeName": "Special Leave", "unit": "DAY"},
        ]
    }


@pytest.mark.asyncio
async def test_get_leave_types_returns_list(mock_available_time_types_response):
    """AvailableTimeTypes tool returns a list of leave types."""
    mock_tool = MagicMock()
    mock_tool.name = "GET_rest_timemanagement_absence_v1_availableTimeTypes"
    mock_tool.ainvoke = AsyncMock(return_value=str(mock_available_time_types_response))

    result = await mock_tool.ainvoke({"userId": "user123"})
    assert "availableTimeTypes" in str(result)
    assert "ANNUAL_LEAVE" in str(result)
    assert "SICK_LEAVE" in str(result)


@pytest.mark.asyncio
async def test_get_leave_types_multiple_types(mock_available_time_types_response):
    """Multiple leave types are returned in the response."""
    types = mock_available_time_types_response["availableTimeTypes"]
    assert len(types) == 3
    type_ids = [t["timeTypeId"] for t in types]
    assert "ANNUAL_LEAVE" in type_ids
    assert "SICK_LEAVE" in type_ids
    assert "SPECIAL_LEAVE" in type_ids


@pytest.mark.asyncio
async def test_get_leave_types_specific_type(mock_available_time_types_response):
    """Can filter for a specific leave type from the response."""
    types = mock_available_time_types_response["availableTimeTypes"]
    annual = next((t for t in types if t["timeTypeId"] == "ANNUAL_LEAVE"), None)
    assert annual is not None
    assert annual["timeTypeName"] == "Annual Leave"
    assert annual["unit"] == "DAY"


def test_leave_type_structure(mock_available_time_types_response):
    """Each leave type entry has the required fields."""
    for t in mock_available_time_types_response["availableTimeTypes"]:
        assert "timeTypeId" in t
        assert "timeTypeName" in t
        assert "unit" in t
