"""
Manual test script for insights endpoint.

This script tests the daily insights endpoint with mock data.
Run with: uv run python tests/manual/test_insights_endpoint.py
"""

import asyncio
from datetime import date, time

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.models.activity import Activity, Category, Group
from app.models.user import User
from app.repositories.insights_repository import InsightsRepository
from app.services.insights_service import InsightsService


async def setup_test_data(session: AsyncSession, user_id: int):
    test_group = Group(user_id=user_id, name="Test Work", color="#FF5733")
    session.add(test_group)
    await session.flush()

    test_category = Category(
        user_id=user_id,
        group_id=test_group.id,
        name="Test Development",
        priority=1,
        min_weekly_hours=10,
        target_weekly_hours=40,
        max_weekly_hours=50,
        unit="hours",
        mandatory=True,
    )
    session.add(test_category)
    await session.flush()

    test_date = date(2026, 1, 25)
    previous_date = date(2026, 1, 24)

    activities_today = [
        Activity(
            user_id=user_id,
            category_id=test_category.id,
            date=test_date,
            start_time=time(9, 0),
            end_time=time(12, 0),
            notes="Morning work",
        ),
        Activity(
            user_id=user_id,
            category_id=test_category.id,
            date=test_date,
            start_time=time(13, 0),
            end_time=time(17, 30),
            notes="Afternoon work",
        ),
    ]

    activities_yesterday = [
        Activity(
            user_id=user_id,
            category_id=test_category.id,
            date=previous_date,
            start_time=time(9, 0),
            end_time=time(11, 0),
            notes="Short work",
        ),
    ]

    for activity in activities_today + activities_yesterday:
        session.add(activity)

    await session.commit()
    print(f"✅ Test data created for user {user_id}")
    print(f"   - Group: {test_group.name}")
    print(f"   - Category: {test_category.name}")
    print(f"   - Activities today: {len(activities_today)}")
    print(f"   - Activities yesterday: {len(activities_yesterday)}")


async def test_insights_service():
    async with async_session_maker() as session:
        user = await session.get(User, 1)
        if not user:
            print("❌ No user found with ID 1. Please create a user first.")
            return

        print(f"\n📊 Testing Insights Service for user: {user.email}")

        await setup_test_data(session, user.id)

        insights_repo = InsightsRepository(session)
        insights_service = InsightsService(insights_repo)

        test_date = date(2026, 1, 25)
        result = await insights_service.get_daily_comparison(user.id, test_date)

        print(f"\n✨ Daily Comparison Results for {test_date}:")
        print(f"   Total minutes today: {result['totalMinutes']}")
        print(f"   Total minutes yesterday: {result['previousTotalMinutes']}")
        print(f"   Delta: {result['totalMinutesDelta']} minutes")
        print(f"   Percent change: {result['totalMinutesPercentChange']}%")

        print(f"\n📈 Group Breakdown ({len(result['groupBreakdown'])} groups):")
        for group in result["groupBreakdown"]:
            print(
                f"   - {group['groupName']}: {group['minutes']} min "
                f"(Δ {group['minutesDelta']}, {group['percentChange']}%)"
            )

        print(f"\n🏆 Top Categories ({len(result['topCategories'])} categories):")
        for cat in result["topCategories"]:
            print(
                f"   - {cat['categoryName']}: {cat['minutes']} min "
                f"({cat['percentOfTotal']}% of total)"
            )

        print(f"\n📊 Statistics:")
        stats = result["stats"]
        print(
            f"   Activities: {stats['activitiesCount']} (Δ {stats['activitiesCountDelta']})"
        )
        print(f"   Categories used: {stats['categoriesUsed']}")
        print(f"   Avg duration: {stats['averageActivityDuration']} min")
        if stats["longestActivity"]:
            longest = stats["longestActivity"]
            print(
                f"   Longest: {longest['categoryName']} "
                f"({longest['minutes']} min, {longest['startTime']}-{longest['endTime']})"
            )

        if result["productivity"]:
            prod = result["productivity"]
            print(f"\n⚡ Productivity:")
            print(
                f"   Mandatory time: {prod['mandatoryMinutes']} min "
                f"({prod['mandatoryPercentOfTotal']}%)"
            )

        print("\n✅ Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_insights_service())
