from datetime import date as date_type
from uuid import UUID

from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.exceptions import DependencyConflictError, NotFoundError
from app.models.activity import Activity, Category, GlobalConstraints, Group
from app.repositories.activity_repository import (
    ActivityRepository,
    CategoryRepository,
    GlobalConstraintsRepository,
    GroupRepository,
)
from app.schemas.activity import (
    ActivityCreate,
    ActivityUpdate,
    CategoryCreate,
    CategoryUpdate,
    GlobalConstraintsUpdate,
    GroupCreate,
    GroupUpdate,
)


class ActivityService:
    def __init__(
        self,
        group_repo: GroupRepository,
        category_repo: CategoryRepository,
        constraints_repo: GlobalConstraintsRepository,
        activity_repo: ActivityRepository,
    ):
        self.group_repo = group_repo
        self.category_repo = category_repo
        self.constraints_repo = constraints_repo
        self.activity_repo = activity_repo

    async def get_groups(self, user_id: UUID) -> list[Group]:
        logger.debug(f"Fetching all groups for user_id={user_id}")
        groups = await self.group_repo.get_by_user(user_id)
        logger.info(f"Found {len(groups)} groups for user_id={user_id}")
        return groups

    async def get_group(self, id: UUID, user_id: UUID) -> Group:
        logger.debug(f"Fetching group id={id} for user_id={user_id}")
        group = await self.group_repo.get_by_id_and_user(id, user_id)
        if not group:
            logger.warning(f"Group not found: id={id}, user_id={user_id}")
            raise NotFoundError(resource="group", resource_id=str(id))
        return group

    async def create_group(self, data: GroupCreate, user_id: UUID) -> Group:
        logger.info(f"Creating group '{data.name}' for user_id={user_id}")
        group = await self.group_repo.create(**data.model_dump(), user_id=user_id)
        logger.success(
            f"Group created: id={group.id}, name='{group.name}', user_id={user_id}"
        )
        return group

    async def update_group(self, id: UUID, data: GroupUpdate, user_id: UUID) -> Group:
        logger.info(f"Updating group id={id} for user_id={user_id}")
        group = await self.get_group(id, user_id)
        updated = await self.group_repo.update(
            group, data.model_dump(exclude_unset=True)
        )
        logger.success(f"Group updated: id={id}")
        return updated

    async def delete_group(self, id: UUID, user_id: UUID) -> None:
        logger.info(f"Deleting group id={id} for user_id={user_id}")
        await self.get_group(id, user_id)
        try:
            await self.group_repo.delete(id)
            logger.success(f"Group deleted: id={id}")
        except IntegrityError as e:
            logger.error(f"Cannot delete group id={id}: has associated categories")
            raise DependencyConflictError(
                resource="group",
                detail="Cannot delete group because it has associated categories",
            ) from e

    async def get_categories(self, user_id: UUID) -> list[Category]:
        logger.debug(f"Fetching all categories for user_id={user_id}")
        categories = await self.category_repo.get_by_user(user_id)
        logger.info(f"Found {len(categories)} categories for user_id={user_id}")
        return categories

    async def get_category(self, id: UUID, user_id: UUID) -> Category:
        logger.debug(f"Fetching category id={id} for user_id={user_id}")
        category = await self.category_repo.get_by_id_and_user(id, user_id)
        if not category:
            logger.warning(f"Category not found: id={id}, user_id={user_id}")
            raise NotFoundError(resource="category", resource_id=str(id))
        return category

    async def create_category(self, data: CategoryCreate, user_id: UUID) -> Category:
        logger.info(
            f"Creating category '{data.name}' for user_id={user_id}, "
            f"group_id={data.group_id}"
        )
        await self.get_group(data.group_id, user_id)
        category = await self.category_repo.create(**data.model_dump(), user_id=user_id)
        logger.success(f"Category created: id={category.id}, name='{category.name}'")
        return category

    async def update_category(
        self, id: UUID, data: CategoryUpdate, user_id: UUID
    ) -> Category:
        logger.info(f"Updating category id={id} for user_id={user_id}")
        category = await self.get_category(id, user_id)
        if data.group_id:
            await self.get_group(data.group_id, user_id)
        updated = await self.category_repo.update(
            category, data.model_dump(exclude_unset=True)
        )
        logger.success(f"Category updated: id={id}")
        return updated

    async def delete_category(self, id: UUID, user_id: UUID) -> None:
        logger.info(f"Deleting category id={id} for user_id={user_id}")
        await self.get_category(id, user_id)
        await self.category_repo.delete(id)
        logger.success(f"Category deleted: id={id}")

    async def get_global_constraints(self, user_id: UUID) -> GlobalConstraints:
        logger.debug(f"Fetching global constraints for user_id={user_id}")
        constraints = await self.constraints_repo.get_by_user(user_id)
        if not constraints:
            logger.info(
                f"No constraints found, creating defaults for user_id={user_id}"
            )
            constraints = await self.constraints_repo.create(user_id=user_id)
        return constraints

    async def update_global_constraints(
        self, data: GlobalConstraintsUpdate, user_id: UUID
    ) -> GlobalConstraints:
        logger.info(f"Updating global constraints for user_id={user_id}")
        constraints = await self.get_global_constraints(user_id)
        updated = await self.constraints_repo.update(
            constraints, data.model_dump(exclude_unset=True)
        )
        logger.success(f"Global constraints updated for user_id={user_id}")
        return updated

    async def get_activities(self, user_id: UUID) -> list[Activity]:
        logger.debug(f"Fetching all activities for user_id={user_id}")
        activities = await self.activity_repo.get_by_user(user_id)
        logger.info(f"Found {len(activities)} activities for user_id={user_id}")
        return activities

    async def get_activities_by_date(
        self, user_id: UUID, date: date_type
    ) -> list[Activity]:
        logger.debug(f"Fetching activities for user_id={user_id}, date={date}")
        activities = await self.activity_repo.get_by_user_and_date(user_id, date)
        logger.info(
            f"Found {len(activities)} activities for user_id={user_id} on {date}"
        )
        return activities

    async def get_activity(self, id: UUID, user_id: UUID) -> Activity:
        logger.debug(f"Fetching activity id={id} for user_id={user_id}")
        activity = await self.activity_repo.get_by_id_and_user(id, user_id)
        if not activity:
            logger.warning(f"Activity not found: id={id}, user_id={user_id}")
            raise NotFoundError(resource="activity", resource_id=str(id))
        return activity

    async def create_activity(self, data: ActivityCreate, user_id: UUID) -> Activity:
        logger.info(
            f"Creating activity for user_id={user_id}, "
            f"category_id={data.category_id}, date={data.date}"
        )
        await self.get_category(data.category_id, user_id)
        activity = await self.activity_repo.create(**data.model_dump(), user_id=user_id)
        logger.success(
            f"Activity created: id={activity.id}, date={activity.date}, "
            f"{activity.start_time}-{activity.end_time}"
        )
        return activity

    async def update_activity(
        self, id: UUID, data: ActivityUpdate, user_id: UUID
    ) -> Activity:
        logger.info(f"Updating activity id={id} for user_id={user_id}")
        activity = await self.get_activity(id, user_id)
        if data.category_id:
            await self.get_category(data.category_id, user_id)
        updated = await self.activity_repo.update(
            activity, data.model_dump(exclude_unset=True)
        )
        logger.success(f"Activity updated: id={id}")
        return updated

    async def delete_activity(self, id: UUID, user_id: UUID) -> None:
        logger.info(f"Deleting activity id={id} for user_id={user_id}")
        await self.get_activity(id, user_id)
        await self.activity_repo.delete(id)
        logger.success(f"Activity deleted: id={id}")
