#!/usr/bin/env python3
"""Script to test logging system with various error scenarios."""

import asyncio
import httpx
from datetime import timedelta
from app.core.security import create_access_token


async def test_logging_scenarios():
    """Test various error scenarios to verify logging."""
    base_url = "http://localhost:8000/api/v1"

    # Create a test token (user_id = 1)
    token = create_access_token(subject="1", expires_delta=timedelta(hours=1))
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    print(f"🔑 Test Token: {token[:50]}...")
    print("\n" + "=" * 80)

    async with httpx.AsyncClient() as client:
        # Test 1: Validation Error - Invalid time format
        print("\n📝 TEST 1: Validation Error - Invalid Time Format")
        print("-" * 80)
        response = await client.post(
            f"{base_url}/activities",
            headers=headers,
            json={
                "categoryId": "123e4567-e89b-12d3-a456-426614174000",
                "date": "2026-01-25",
                "startTime": "25:00",  # Invalid hour
                "endTime": "08:00",
            },
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Test 2: Validation Error - Invalid UUID
        print("\n📝 TEST 2: Validation Error - Invalid UUID")
        print("-" * 80)
        response = await client.post(
            f"{base_url}/activities",
            headers=headers,
            json={
                "categoryId": "not-a-valid-uuid",
                "date": "2026-01-25",
                "startTime": "09:00",
                "endTime": "10:00",
            },
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Test 3: Validation Error - End time before start time
        print("\n📝 TEST 3: Validation Error - End Time Before Start Time")
        print("-" * 80)
        response = await client.post(
            f"{base_url}/activities",
            headers=headers,
            json={
                "categoryId": "123e4567-e89b-12d3-a456-426614174000",
                "date": "2026-01-25",
                "startTime": "10:00",
                "endTime": "09:00",  # Before start time
            },
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Test 4: Database Integrity Error - Non-existent category
        print("\n📝 TEST 4: Database Integrity Error - Non-existent Category")
        print("-" * 80)
        response = await client.post(
            f"{base_url}/activities",
            headers=headers,
            json={
                "categoryId": "123e4567-e89b-12d3-a456-426614174000",
                "date": "2026-01-25",
                "startTime": "09:00",
                "endTime": "10:00",
            },
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Test 5: Not Found Error
        print("\n📝 TEST 5: Not Found Error - Non-existent Resource")
        print("-" * 80)
        response = await client.get(
            f"{base_url}/activities/999e9999-e99b-99d9-a999-999999999999",
            headers=headers,
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Test 6: Validation Error - Invalid date format
        print("\n📝 TEST 6: Validation Error - Invalid Date Format")
        print("-" * 80)
        response = await client.get(
            f"{base_url}/activities/date/invalid-date", headers=headers
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Test 7: Validation Error - Invalid color in group
        print("\n📝 TEST 7: Validation Error - Invalid Color Format")
        print("-" * 80)
        response = await client.post(
            f"{base_url}/groups",
            headers=headers,
            json={
                "name": "Test Group",
                "color": "red",  # Invalid, needs #RRGGBB
            },
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

        # Test 8: Success Case - Create a group (for comparison)
        print("\n📝 TEST 8: Success Case - Valid Request")
        print("-" * 80)
        response = await client.post(
            f"{base_url}/groups",
            headers=headers,
            json={"name": "Test Logging Group", "color": "#FF5733"},
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

    print("\n" + "=" * 80)
    print("✅ All test scenarios completed!")
    print("\nCheck Docker logs with: docker compose logs app --tail=100")
    print("Check log files in: logs/")


if __name__ == "__main__":
    asyncio.run(test_logging_scenarios())
