from app.schemas.base import CamelModel


class GroupBreakdownItem(CamelModel):
    group_id: str
    group_name: str
    group_color: str | None
    minutes: int
    previous_minutes: int
    minutes_delta: int
    percent_change: float
    percent_of_total: float


class TopCategoryItem(CamelModel):
    category_id: str
    category_name: str
    group_name: str
    group_color: str | None
    minutes: int
    previous_minutes: int
    minutes_delta: int
    percent_change: float
    percent_of_total: float


class ProductiveDayDetail(CamelModel):
    date: str
    day_name: str
    minutes: int


class LongestActivityDetail(CamelModel):
    category_name: str
    minutes: int
    date: str
    start_time: str
    end_time: str


class WeeklyStats(CamelModel):
    activities_count: int
    previous_activities_count: int
    activities_count_delta: int
    categories_used: int
    previous_categories_used: int
    categories_used_delta: int
    average_activity_duration: float
    previous_average_activity_duration: float
    average_activity_duration_delta: float
    average_daily_minutes: float
    previous_average_daily_minutes: float
    average_daily_minutes_delta: float
    most_productive_day: ProductiveDayDetail | None
    least_productive_day: ProductiveDayDetail | None
    longest_activity: LongestActivityDetail | None


class DailyBreakdownItem(CamelModel):
    date: str
    day_name: str
    minutes: int
    activities_count: int


class GoalProgressItem(CamelModel):
    category_id: str
    category_name: str
    current_week_minutes: int
    target_weekly_minutes: int
    min_weekly_minutes: int
    max_weekly_minutes: int
    progress_percent: float
    status: str


class WeeklyComparisonResponse(CamelModel):
    week_start_date: str
    week_end_date: str
    previous_week_start_date: str
    previous_week_end_date: str
    total_minutes: int
    previous_total_minutes: int
    total_minutes_delta: int
    total_minutes_percent_change: float
    group_breakdown: list[GroupBreakdownItem]
    top_categories: list[TopCategoryItem]
    stats: WeeklyStats
    daily_breakdown: list[DailyBreakdownItem]
    goals_progress: list[GoalProgressItem] | None


class DailyStats(CamelModel):
    activities_count: int
    previous_activities_count: int
    activities_count_delta: int
    categories_used: int
    previous_categories_used: int
    categories_used_delta: int
    average_activity_duration: float
    previous_average_activity_duration: float
    average_activity_duration_delta: float
    longest_activity: LongestActivityDetail | None


class ProductivityBreakdown(CamelModel):
    mandatory_minutes: int
    previous_mandatory_minutes: int
    mandatory_minutes_delta: int
    mandatory_percent_of_total: float
    optional_minutes: int
    previous_optional_minutes: int
    optional_minutes_delta: int
    optional_percent_of_total: float


class DailyComparisonResponse(CamelModel):
    date: str
    previous_date: str
    total_minutes: int
    previous_total_minutes: int
    total_minutes_delta: int
    total_minutes_percent_change: float
    group_breakdown: list[GroupBreakdownItem]
    top_categories: list[TopCategoryItem]
    stats: DailyStats
    productivity: ProductivityBreakdown | None
