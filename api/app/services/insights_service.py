from datetime import date, timedelta
from uuid import UUID

from loguru import logger

from app.repositories.insights_repository import InsightsRepository


class InsightsService:
    def __init__(self, insights_repo: InsightsRepository):
        self.insights_repo = insights_repo

    @staticmethod
    def _calculate_percent_change(current: float, previous: float) -> float:
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100

    async def get_weekly_comparison(self, user_id: UUID, any_date: date) -> dict:
        logger.info(f"Generating weekly comparison for user {user_id} on {any_date}")

        current_week_start, current_week_end = self.insights_repo._get_week_bounds(
            any_date
        )
        previous_week_start, previous_week_end = self.insights_repo._get_week_bounds(
            current_week_start - timedelta(days=7)
        )

        logger.debug(
            f"Current week: {current_week_start} to {current_week_end}, "
            f"Previous week: {previous_week_start} to {previous_week_end}"
        )

        current_total = await self.insights_repo.get_week_total_minutes(
            user_id, current_week_start, current_week_end
        )
        previous_total = await self.insights_repo.get_week_total_minutes(
            user_id, previous_week_start, previous_week_end
        )

        current_group_breakdown = await self.insights_repo.get_week_group_breakdown(
            user_id, current_week_start, current_week_end
        )
        previous_group_breakdown = await self.insights_repo.get_week_group_breakdown(
            user_id, previous_week_start, previous_week_end
        )

        current_top_categories = await self.insights_repo.get_week_top_categories(
            user_id, current_week_start, current_week_end
        )
        previous_top_categories = await self.insights_repo.get_week_top_categories(
            user_id, previous_week_start, previous_week_end
        )

        current_stats = await self.insights_repo.get_week_activities_stats(
            user_id, current_week_start, current_week_end
        )
        previous_stats = await self.insights_repo.get_week_activities_stats(
            user_id, previous_week_start, previous_week_end
        )

        daily_breakdown = await self.insights_repo.get_week_daily_breakdown(
            user_id, current_week_start, current_week_end
        )

        most_productive_day = await self.insights_repo.get_week_most_productive_day(
            user_id, current_week_start, current_week_end
        )
        least_productive_day = await self.insights_repo.get_week_least_productive_day(
            user_id, current_week_start, current_week_end
        )
        longest_activity = await self.insights_repo.get_week_longest_activity(
            user_id, current_week_start, current_week_end
        )

        goals_progress = await self.insights_repo.get_week_goals_progress(
            user_id, current_week_start, current_week_end
        )

        previous_group_map = {
            item["group_name"]: item["minutes"] for item in previous_group_breakdown
        }
        group_breakdown = []
        for item in current_group_breakdown:
            prev_minutes = previous_group_map.get(item["group_name"], 0.0)
            delta = item["minutes"] - prev_minutes
            percent_change = self._calculate_percent_change(
                item["minutes"], prev_minutes
            )
            percent_of_total = (
                (item["minutes"] / current_total * 100) if current_total > 0 else 0.0
            )
            group_breakdown.append(
                {
                    "group_id": item.get("group_id", ""),
                    "group_name": item["group_name"],
                    "group_color": item["color"],
                    "minutes": int(item["minutes"]),
                    "previous_minutes": int(prev_minutes),
                    "minutes_delta": int(delta),
                    "percent_change": percent_change,
                    "percent_of_total": percent_of_total,
                }
            )

        previous_cat_map = {
            item["category_name"]: item["minutes"] for item in previous_top_categories
        }
        top_categories = []
        for item in current_top_categories:
            prev_minutes = previous_cat_map.get(item["category_name"], 0.0)
            delta = item["minutes"] - prev_minutes
            percent_change = self._calculate_percent_change(
                item["minutes"], prev_minutes
            )
            percent_of_total = (
                (item["minutes"] / current_total * 100) if current_total > 0 else 0.0
            )
            top_categories.append(
                {
                    "category_id": item.get("category_id", ""),
                    "category_name": item["category_name"],
                    "group_name": item["group_name"],
                    "group_color": item["group_color"],
                    "minutes": int(item["minutes"]),
                    "previous_minutes": int(prev_minutes),
                    "minutes_delta": int(delta),
                    "percent_change": percent_change,
                    "percent_of_total": percent_of_total,
                }
            )

        current_avg_daily = current_total / 7
        previous_avg_daily = previous_total / 7

        stats = {
            "activities_count": current_stats["activities_count"],
            "previous_activities_count": previous_stats["activities_count"],
            "activities_count_delta": (
                current_stats["activities_count"] - previous_stats["activities_count"]
            ),
            "categories_used": current_stats["unique_categories"],
            "previous_categories_used": previous_stats["unique_categories"],
            "categories_used_delta": (
                current_stats["unique_categories"] - previous_stats["unique_categories"]
            ),
            "average_activity_duration": current_stats["average_duration"],
            "previous_average_activity_duration": previous_stats["average_duration"],
            "average_activity_duration_delta": (
                current_stats["average_duration"] - previous_stats["average_duration"]
            ),
            "average_daily_minutes": current_avg_daily,
            "previous_average_daily_minutes": previous_avg_daily,
            "average_daily_minutes_delta": current_avg_daily - previous_avg_daily,
            "most_productive_day": (
                {
                    "date": most_productive_day["date"].isoformat(),
                    "day_name": most_productive_day["day_name"],
                    "minutes": int(most_productive_day["minutes"]),
                }
                if most_productive_day
                else None
            ),
            "least_productive_day": (
                {
                    "date": least_productive_day["date"].isoformat(),
                    "day_name": least_productive_day["day_name"],
                    "minutes": int(least_productive_day["minutes"]),
                }
                if least_productive_day
                else None
            ),
            "longest_activity": (
                {
                    "category_name": longest_activity["category_name"],
                    "minutes": int(longest_activity["minutes"]),
                    "date": longest_activity["date"].isoformat(),
                    "start_time": "00:00",
                    "end_time": "00:00",
                }
                if longest_activity
                else None
            ),
        }

        daily_breakdown_formatted = [
            {
                "date": item["date"].isoformat(),
                "day_name": item["day_name"],
                "minutes": int(item["minutes"]),
                "activities_count": item["activities_count"],
            }
            for item in daily_breakdown
        ]

        result = {
            "week_start_date": current_week_start.isoformat(),
            "week_end_date": current_week_end.isoformat(),
            "previous_week_start_date": previous_week_start.isoformat(),
            "previous_week_end_date": previous_week_end.isoformat(),
            "total_minutes": int(current_total),
            "previous_total_minutes": int(previous_total),
            "total_minutes_delta": int(current_total - previous_total),
            "total_minutes_percent_change": self._calculate_percent_change(
                current_total, previous_total
            ),
            "group_breakdown": group_breakdown,
            "top_categories": top_categories,
            "stats": stats,
            "daily_breakdown": daily_breakdown_formatted,
            "goals_progress": goals_progress,
        }

        logger.info(
            f"Weekly comparison generated: {current_total} mins total, "
            f"{current_stats['activities_count']} activities"
        )

        return result

    async def get_daily_comparison(self, user_id: UUID, target_date: date) -> dict:
        logger.info(f"Generating daily comparison for user {user_id} on {target_date}")

        previous_date = target_date - timedelta(days=1)

        logger.debug(f"Target date: {target_date}, Previous date: {previous_date}")

        current_total = await self.insights_repo.get_day_total_minutes(
            user_id, target_date
        )
        previous_total = await self.insights_repo.get_day_total_minutes(
            user_id, previous_date
        )

        current_group_breakdown = await self.insights_repo.get_day_group_breakdown(
            user_id, target_date
        )
        previous_group_breakdown = await self.insights_repo.get_day_group_breakdown(
            user_id, previous_date
        )

        current_top_categories = await self.insights_repo.get_day_top_categories(
            user_id, target_date
        )
        previous_top_categories = await self.insights_repo.get_day_top_categories(
            user_id, previous_date
        )

        current_stats = await self.insights_repo.get_day_activities_stats(
            user_id, target_date
        )
        previous_stats = await self.insights_repo.get_day_activities_stats(
            user_id, previous_date
        )

        longest_activity = await self.insights_repo.get_day_longest_activity(
            user_id, target_date
        )

        current_mandatory = await self.insights_repo.get_day_mandatory_minutes(
            user_id, target_date
        )
        previous_mandatory = await self.insights_repo.get_day_mandatory_minutes(
            user_id, previous_date
        )

        previous_group_map = {
            item["group_name"]: item["minutes"] for item in previous_group_breakdown
        }
        group_breakdown = []
        for item in current_group_breakdown:
            prev_minutes = previous_group_map.get(item["group_name"], 0.0)
            delta = item["minutes"] - prev_minutes
            percent_change = self._calculate_percent_change(
                item["minutes"], prev_minutes
            )
            percent_of_total = (
                (item["minutes"] / current_total * 100) if current_total > 0 else 0.0
            )
            group_breakdown.append(
                {
                    "group_id": item.get("group_id", ""),
                    "group_name": item["group_name"],
                    "group_color": item["color"],
                    "minutes": int(item["minutes"]),
                    "previous_minutes": int(prev_minutes),
                    "minutes_delta": int(delta),
                    "percent_change": percent_change,
                    "percent_of_total": percent_of_total,
                }
            )

        previous_cat_map = {
            item["category_name"]: item["minutes"] for item in previous_top_categories
        }
        top_categories = []
        for item in current_top_categories:
            prev_minutes = previous_cat_map.get(item["category_name"], 0.0)
            delta = item["minutes"] - prev_minutes
            percent_change = self._calculate_percent_change(
                item["minutes"], prev_minutes
            )
            percent_of_total = (
                (item["minutes"] / current_total * 100) if current_total > 0 else 0.0
            )
            top_categories.append(
                {
                    "category_id": item.get("category_id", ""),
                    "category_name": item["category_name"],
                    "group_name": item["group_name"],
                    "group_color": item["group_color"],
                    "minutes": int(item["minutes"]),
                    "previous_minutes": int(prev_minutes),
                    "minutes_delta": int(delta),
                    "percent_change": percent_change,
                    "percent_of_total": percent_of_total,
                }
            )

        stats = {
            "activities_count": current_stats["activities_count"],
            "previous_activities_count": previous_stats["activities_count"],
            "activities_count_delta": (
                current_stats["activities_count"] - previous_stats["activities_count"]
            ),
            "categories_used": current_stats["unique_categories"],
            "previous_categories_used": previous_stats["unique_categories"],
            "categories_used_delta": (
                current_stats["unique_categories"] - previous_stats["unique_categories"]
            ),
            "average_activity_duration": current_stats["average_duration"],
            "previous_average_activity_duration": previous_stats["average_duration"],
            "average_activity_duration_delta": (
                current_stats["average_duration"] - previous_stats["average_duration"]
            ),
            "longest_activity": (
                {
                    "category_name": longest_activity["category_name"],
                    "minutes": int(longest_activity["minutes"]),
                    "date": longest_activity["date"].isoformat(),
                    "start_time": longest_activity["start_time"],
                    "end_time": longest_activity["end_time"],
                }
                if longest_activity
                else None
            ),
        }

        current_optional = current_total - current_mandatory
        previous_optional = previous_total - previous_mandatory

        productivity = None
        if current_total > 0 or previous_total > 0:
            mandatory_percent = (
                (current_mandatory / current_total * 100) if current_total > 0 else 0.0
            )
            optional_percent = (
                (current_optional / current_total * 100) if current_total > 0 else 0.0
            )

            productivity = {
                "mandatory_minutes": int(current_mandatory),
                "previous_mandatory_minutes": int(previous_mandatory),
                "mandatory_minutes_delta": int(current_mandatory - previous_mandatory),
                "mandatory_percent_of_total": mandatory_percent,
                "optional_minutes": int(current_optional),
                "previous_optional_minutes": int(previous_optional),
                "optional_minutes_delta": int(current_optional - previous_optional),
                "optional_percent_of_total": optional_percent,
            }

        result = {
            "date": target_date.isoformat(),
            "previous_date": previous_date.isoformat(),
            "total_minutes": int(current_total),
            "previous_total_minutes": int(previous_total),
            "total_minutes_delta": int(current_total - previous_total),
            "total_minutes_percent_change": self._calculate_percent_change(
                current_total, previous_total
            ),
            "group_breakdown": group_breakdown,
            "top_categories": top_categories,
            "stats": stats,
            "productivity": productivity,
        }

        logger.info(
            f"Daily comparison generated: {current_total} mins total, "
            f"{current_stats['activities_count']} activities"
        )

        return result
