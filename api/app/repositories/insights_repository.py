from datetime import date, timedelta
from uuid import UUID

from loguru import logger
from sqlalchemy import cast, func, select
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity, Category, Group


class InsightsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _get_week_bounds(any_date: date) -> tuple[date, date]:
        """Calculate Monday-Sunday bounds for week containing any_date."""
        weekday = any_date.weekday()  # Monday=0, Sunday=6
        week_start = any_date - timedelta(days=weekday)
        week_end = week_start + timedelta(days=6)
        return week_start, week_end

    async def get_week_total_minutes(
        self, user_id: UUID, week_start: date, week_end: date
    ) -> float:
        """Get total minutes for a week."""
        logger.debug(
            f"Fetching total minutes for user {user_id} "
            f"between {week_start} and {week_end}"
        )

        # Calculate duration in minutes using EXTRACT(epoch from interval)
        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        result = await self.session.execute(
            select(func.coalesce(func.sum(duration_expr), 0.0)).where(
                Activity.user_id == user_id,
                Activity.date >= week_start,
                Activity.date <= week_end,
            )
        )
        total = result.scalar_one()
        logger.debug(f"Total minutes: {total}")
        return float(total)

    async def get_week_group_breakdown(
        self, user_id: UUID, week_start: date, week_end: date
    ) -> list[dict]:
        """Get minutes per group for a week."""
        logger.debug(
            f"Fetching group breakdown for user {user_id} "
            f"between {week_start} and {week_end}"
        )

        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        result = await self.session.execute(
            select(
                Group.id.label("group_id"),
                Group.name.label("group_name"),
                Group.color.label("group_color"),
                func.sum(duration_expr).label("minutes"),
            )
            .join(Category, Category.group_id == Group.id)
            .join(Activity, Activity.category_id == Category.id)
            .where(
                Activity.user_id == user_id,
                Activity.date >= week_start,
                Activity.date <= week_end,
            )
            .group_by(Group.id, Group.name, Group.color)
        )

        breakdown = [
            {
                "group_id": str(row.group_id),
                "group_name": row.group_name,
                "color": row.group_color,
                "minutes": float(row.minutes),
            }
            for row in result.all()
        ]
        logger.debug(f"Group breakdown: {len(breakdown)} groups")
        return breakdown

    async def get_week_top_categories(
        self, user_id: UUID, week_start: date, week_end: date, limit: int = 5
    ) -> list[dict]:
        """Get top N categories by total minutes for a week."""
        logger.debug(
            f"Fetching top {limit} categories for user {user_id} "
            f"between {week_start} and {week_end}"
        )

        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        result = await self.session.execute(
            select(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                Group.name.label("group_name"),
                Group.color.label("group_color"),
                func.sum(duration_expr).label("minutes"),
            )
            .join(Category, Activity.category_id == Category.id)
            .join(Group, Category.group_id == Group.id)
            .where(
                Activity.user_id == user_id,
                Activity.date >= week_start,
                Activity.date <= week_end,
            )
            .group_by(Category.id, Category.name, Group.name, Group.color)
            .order_by(func.sum(duration_expr).desc())
            .limit(limit)
        )

        top_categories = [
            {
                "category_id": str(row.category_id),
                "category_name": row.category_name,
                "group_name": row.group_name,
                "group_color": row.group_color,
                "minutes": float(row.minutes),
            }
            for row in result.all()
        ]
        logger.debug(f"Top categories: {len(top_categories)} found")
        return top_categories

    async def get_week_activities_stats(
        self, user_id: UUID, week_start: date, week_end: date
    ) -> dict:
        """Get activity statistics for a week."""
        logger.debug(
            f"Fetching activity stats for user {user_id} "
            f"between {week_start} and {week_end}"
        )

        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        result = await self.session.execute(
            select(
                func.count(Activity.id).label("activities_count"),
                func.coalesce(func.avg(duration_expr), 0.0).label("average_duration"),
                func.count(func.distinct(Activity.category_id)).label(
                    "unique_categories"
                ),
            ).where(
                Activity.user_id == user_id,
                Activity.date >= week_start,
                Activity.date <= week_end,
            )
        )

        row = result.one()
        stats = {
            "activities_count": row.activities_count,
            "average_duration": float(row.average_duration),
            "unique_categories": row.unique_categories,
        }
        logger.debug(f"Activity stats: {stats}")
        return stats

    async def get_week_daily_breakdown(
        self, user_id: UUID, week_start: date, week_end: date
    ) -> list[dict]:
        """Get daily breakdown for a week (7 elements Mon-Sun)."""
        logger.debug(
            f"Fetching daily breakdown for user {user_id} "
            f"between {week_start} and {week_end}"
        )

        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        result = await self.session.execute(
            select(
                Activity.date,
                func.sum(duration_expr).label("minutes"),
                func.count(Activity.id).label("activities_count"),
            )
            .where(
                Activity.user_id == user_id,
                Activity.date >= week_start,
                Activity.date <= week_end,
            )
            .group_by(Activity.date)
        )

        # Map results by date
        data_by_date = {
            row.date: (float(row.minutes), row.activities_count) for row in result.all()
        }

        # Generate full week (Mon-Sun), fill missing days with zeros
        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        breakdown = []
        current_date = week_start

        for day_name in day_names:
            minutes, activities_count = data_by_date.get(current_date, (0.0, 0))
            breakdown.append(
                {
                    "date": current_date,
                    "day_name": day_name,
                    "minutes": minutes,
                    "activities_count": activities_count,
                }
            )
            current_date += timedelta(days=1)

        logger.debug(f"Daily breakdown: {len(breakdown)} days")
        return breakdown

    async def get_week_most_productive_day(
        self, user_id: UUID, week_start: date, week_end: date
    ) -> dict | None:
        """Get the day with most minutes in a week."""
        logger.debug(
            f"Fetching most productive day for user {user_id} "
            f"between {week_start} and {week_end}"
        )

        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        result = await self.session.execute(
            select(
                Activity.date,
                func.sum(duration_expr).label("minutes"),
            )
            .where(
                Activity.user_id == user_id,
                Activity.date >= week_start,
                Activity.date <= week_end,
            )
            .group_by(Activity.date)
            .order_by(func.sum(duration_expr).desc())
            .limit(1)
        )

        row = result.first()
        if not row:
            logger.debug("No productive days found")
            return None

        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        day_name = day_names[row.date.weekday()]

        most_productive = {
            "date": row.date,
            "day_name": day_name,
            "minutes": float(row.minutes),
        }
        logger.debug(f"Most productive day: {most_productive}")
        return most_productive

    async def get_week_least_productive_day(
        self, user_id: UUID, week_start: date, week_end: date
    ) -> dict | None:
        """Get the day with least minutes (but > 0) in a week."""
        logger.debug(
            f"Fetching least productive day for user {user_id} "
            f"between {week_start} and {week_end}"
        )

        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        result = await self.session.execute(
            select(
                Activity.date,
                func.sum(duration_expr).label("minutes"),
            )
            .where(
                Activity.user_id == user_id,
                Activity.date >= week_start,
                Activity.date <= week_end,
            )
            .group_by(Activity.date)
            .having(func.sum(duration_expr) > 0)
            .order_by(func.sum(duration_expr).asc())
            .limit(1)
        )

        row = result.first()
        if not row:
            logger.debug(
                "No least productive day found (all days empty or no activities)"
            )
            return None

        day_names = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        day_name = day_names[row.date.weekday()]

        least_productive = {
            "date": row.date,
            "day_name": day_name,
            "minutes": float(row.minutes),
        }
        logger.debug(f"Least productive day: {least_productive}")
        return least_productive

    async def get_week_longest_activity(
        self, user_id: UUID, week_start: date, week_end: date
    ) -> dict | None:
        """Get the single longest activity in a week."""
        logger.debug(
            f"Fetching longest activity for user {user_id} "
            f"between {week_start} and {week_end}"
        )

        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        result = await self.session.execute(
            select(
                Activity.date,
                Category.name.label("category_name"),
                duration_expr.label("minutes"),
            )
            .join(Category, Activity.category_id == Category.id)
            .where(
                Activity.user_id == user_id,
                Activity.date >= week_start,
                Activity.date <= week_end,
            )
            .order_by(duration_expr.desc())
            .limit(1)
        )

        row = result.first()
        if not row:
            logger.debug("No longest activity found")
            return None

        longest = {
            "date": row.date,
            "category_name": row.category_name,
            "minutes": float(row.minutes),
        }
        logger.debug(f"Longest activity: {longest}")
        return longest

    async def get_week_goals_progress(
        self, user_id: UUID, week_start: date, week_end: date
    ) -> list[dict] | None:
        """Get goal progress for categories with defined goals."""
        logger.debug(
            f"Fetching goals progress for user {user_id} "
            f"between {week_start} and {week_end}"
        )

        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        # First, get all categories with goals defined (target_weekly_hours > 0)
        categories_result = await self.session.execute(
            select(
                Category.id,
                Category.name,
                Category.min_weekly_hours,
                Category.target_weekly_hours,
                Category.max_weekly_hours,
            ).where(Category.user_id == user_id, Category.target_weekly_hours > 0)
        )

        categories_with_goals = categories_result.all()

        if not categories_with_goals:
            logger.debug("No categories with goals found")
            return None

        # Get actual time spent per category
        activities_result = await self.session.execute(
            select(
                Activity.category_id,
                func.sum(duration_expr).label("minutes"),
            )
            .where(
                Activity.user_id == user_id,
                Activity.date >= week_start,
                Activity.date <= week_end,
            )
            .group_by(Activity.category_id)
        )

        time_by_category = {
            row.category_id: float(row.minutes) for row in activities_result.all()
        }

        # Build goal progress list
        goals_progress = []
        for cat in categories_with_goals:
            current_minutes = time_by_category.get(cat.id, 0.0)
            min_minutes = cat.min_weekly_hours * 60
            target_minutes = cat.target_weekly_hours * 60
            max_minutes = cat.max_weekly_hours * 60

            # Calculate status
            if current_minutes < min_minutes:
                status = "under"
            elif current_minutes < target_minutes:
                status = "on_track"
            elif current_minutes <= max_minutes:
                status = "target_met"
            else:
                status = "over"

            progress_percent = (
                (current_minutes / target_minutes * 100) if target_minutes > 0 else 0.0
            )

            goals_progress.append(
                {
                    "category_id": str(cat.id),
                    "category_name": cat.name,
                    "current_week_minutes": int(current_minutes),
                    "min_weekly_minutes": int(min_minutes),
                    "target_weekly_minutes": int(target_minutes),
                    "max_weekly_minutes": int(max_minutes),
                    "progress_percent": progress_percent,
                    "status": status,
                }
            )

        logger.debug(f"Goals progress: {len(goals_progress)} categories with goals")
        return goals_progress

    async def get_day_total_minutes(self, user_id: UUID, target_date: date) -> float:
        """Get total minutes for a specific day."""
        logger.debug(f"Fetching total minutes for user {user_id} on {target_date}")

        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        result = await self.session.execute(
            select(func.coalesce(func.sum(duration_expr), 0.0)).where(
                Activity.user_id == user_id,
                Activity.date == target_date,
            )
        )
        total = result.scalar_one()
        logger.debug(f"Total minutes: {total}")
        return float(total)

    async def get_day_group_breakdown(
        self, user_id: UUID, target_date: date
    ) -> list[dict]:
        """Get minutes per group for a specific day."""
        logger.debug(f"Fetching group breakdown for user {user_id} on {target_date}")

        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        result = await self.session.execute(
            select(
                Group.id.label("group_id"),
                Group.name.label("group_name"),
                Group.color.label("group_color"),
                func.sum(duration_expr).label("minutes"),
            )
            .join(Category, Category.group_id == Group.id)
            .join(Activity, Activity.category_id == Category.id)
            .where(
                Activity.user_id == user_id,
                Activity.date == target_date,
            )
            .group_by(Group.id, Group.name, Group.color)
        )

        breakdown = [
            {
                "group_id": str(row.group_id),
                "group_name": row.group_name,
                "color": row.group_color,
                "minutes": float(row.minutes),
            }
            for row in result.all()
        ]
        logger.debug(f"Group breakdown: {len(breakdown)} groups")
        return breakdown

    async def get_day_top_categories(
        self, user_id: UUID, target_date: date, limit: int = 5
    ) -> list[dict]:
        """Get top N categories by time spent for a specific day."""
        logger.debug(
            f"Fetching top {limit} categories for user {user_id} on {target_date}"
        )

        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        result = await self.session.execute(
            select(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                Group.name.label("group_name"),
                Group.color.label("group_color"),
                func.sum(duration_expr).label("minutes"),
            )
            .join(Group, Category.group_id == Group.id)
            .join(Activity, Activity.category_id == Category.id)
            .where(
                Activity.user_id == user_id,
                Activity.date == target_date,
            )
            .group_by(Category.id, Category.name, Group.name, Group.color)
            .order_by(func.sum(duration_expr).desc())
            .limit(limit)
        )

        top_cats = [
            {
                "category_id": str(row.category_id),
                "category_name": row.category_name,
                "group_name": row.group_name,
                "group_color": row.group_color,
                "minutes": float(row.minutes),
            }
            for row in result.all()
        ]
        logger.debug(f"Top categories: {len(top_cats)}")
        return top_cats

    async def get_day_activities_stats(self, user_id: UUID, target_date: date) -> dict:
        """Get activity statistics for a specific day."""
        logger.debug(f"Fetching activity stats for user {user_id} on {target_date}")

        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        result = await self.session.execute(
            select(
                func.count(Activity.id).label("activities_count"),
                func.avg(duration_expr).label("avg_duration"),
                func.count(func.distinct(Activity.category_id)).label(
                    "unique_categories"
                ),
            ).where(
                Activity.user_id == user_id,
                Activity.date == target_date,
            )
        )

        row = result.one()
        stats = {
            "activities_count": row.activities_count,
            "average_duration": float(row.avg_duration) if row.avg_duration else 0.0,
            "unique_categories": row.unique_categories,
        }
        logger.debug(f"Activity stats: {stats}")
        return stats

    async def get_day_longest_activity(
        self, user_id: UUID, target_date: date
    ) -> dict | None:
        """Get the longest activity for a specific day."""
        logger.debug(f"Fetching longest activity for user {user_id} on {target_date}")

        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        result = await self.session.execute(
            select(
                Activity.date,
                Activity.start_time,
                Activity.end_time,
                Category.name.label("category_name"),
                duration_expr.label("minutes"),
            )
            .join(Category, Activity.category_id == Category.id)
            .where(
                Activity.user_id == user_id,
                Activity.date == target_date,
            )
            .order_by(duration_expr.desc())
            .limit(1)
        )

        row = result.first()
        if not row:
            logger.debug("No longest activity found")
            return None

        longest = {
            "date": row.date,
            "category_name": row.category_name,
            "start_time": str(row.start_time),
            "end_time": str(row.end_time),
            "minutes": float(row.minutes),
        }
        logger.debug(f"Longest activity: {longest}")
        return longest

    async def get_day_mandatory_minutes(
        self, user_id: UUID, target_date: date
    ) -> float:
        """Get total minutes spent on mandatory categories for a specific day."""
        logger.debug(f"Fetching mandatory minutes for user {user_id} on {target_date}")

        duration_expr = (
            func.extract(
                "epoch",
                cast(Activity.end_time, INTERVAL) - cast(Activity.start_time, INTERVAL),
            )
            / 60
        )

        result = await self.session.execute(
            select(func.coalesce(func.sum(duration_expr), 0.0))
            .select_from(Activity)
            .join(Category, Activity.category_id == Category.id)
            .where(
                Activity.user_id == user_id,
                Activity.date == target_date,
                Category.mandatory == True,  # noqa: E712
            )
        )
        total = result.scalar_one()
        logger.debug(f"Mandatory minutes: {total}")
        return float(total)
