from datetime import date, datetime, timedelta
from typing import cast
from uuid import UUID

from dateutil.rrule import rrule, rruleset, rrulestr
from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.exceptions import BadRequestError, DependencyConflictError, NotFoundError
from app.models.task import Task, TaskActivity, TaskList
from app.repositories.task_repository import (
    TaskActivityRepository,
    TaskListRepository,
    TaskRepository,
)
from app.schemas.activity import ActivityCreate
from app.schemas.task import (
    ConvertToActivityRequest,
    TaskCompleteRequest,
    TaskCreate,
    TaskListCreate,
    TaskListUpdate,
    TaskUpdate,
)
from app.services.activity_service import ActivityService


class TaskService:
    def __init__(
        self,
        task_list_repo: TaskListRepository,
        task_repo: TaskRepository,
        task_activity_repo: TaskActivityRepository,
        activity_service: ActivityService,
    ):
        self.task_list_repo = task_list_repo
        self.task_repo = task_repo
        self.task_activity_repo = task_activity_repo
        self.activity_service = activity_service

    async def get_task_lists(self, user_id: UUID) -> list[TaskList]:
        logger.debug(f"Fetching all task lists for user_id={user_id}")
        task_lists = await self.task_list_repo.get_by_user(user_id)
        logger.info(f"Found {len(task_lists)} task lists for user_id={user_id}")
        return task_lists

    async def get_task_list(self, id: UUID, user_id: UUID) -> TaskList:
        logger.debug(f"Fetching task list id={id} for user_id={user_id}")
        task_list = await self.task_list_repo.get_by_id_and_user(id, user_id)
        if not task_list:
            logger.warning(f"Task list not found: id={id}, user_id={user_id}")
            raise NotFoundError(resource="task list", resource_id=str(id))
        return task_list

    async def create_task_list(self, data: TaskListCreate, user_id: UUID) -> TaskList:
        logger.info(f"Creating task list '{data.name}' for user_id={user_id}")
        task_list = await self.task_list_repo.create(
            **data.model_dump(),
            user_id=user_id,
        )
        logger.success(
            f"Task list created: id={task_list.id}, "
            f"name='{task_list.name}', user_id={user_id}"
        )
        return task_list

    async def update_task_list(
        self, id: UUID, data: TaskListUpdate, user_id: UUID
    ) -> TaskList:
        logger.info(f"Updating task list id={id} for user_id={user_id}")
        task_list = await self.get_task_list(id, user_id)
        updated = await self.task_list_repo.update(
            task_list, data.model_dump(exclude_unset=True)
        )
        logger.success(f"Task list updated: id={id}")
        return updated

    async def delete_task_list(self, id: UUID, user_id: UUID) -> None:
        logger.info(f"Deleting task list id={id} for user_id={user_id}")
        await self.get_task_list(id, user_id)
        try:
            await self.task_list_repo.delete(id)
            logger.success(f"Task list deleted: id={id}")
        except IntegrityError as e:
            logger.error(f"Cannot delete task list id={id}: has associated tasks")
            raise DependencyConflictError(
                resource="task list",
                detail="Cannot delete task list because it has associated tasks",
            ) from e

    async def get_tasks(
        self,
        user_id: UUID,
        list_id: UUID | None = None,
        status: str | None = None,
    ) -> list[Task]:
        logger.debug(
            f"Fetching tasks for user_id={user_id}, list_id={list_id}, status={status}"
        )
        if list_id and status:
            tasks = await self.task_repo.get_by_user(user_id)
            filtered_tasks = [
                task
                for task in tasks
                if task.task_list_id == list_id and task.status == status
            ]
            logger.info(
                f"Found {len(filtered_tasks)} tasks for user_id={user_id} "
                f"with list_id={list_id} and status={status}"
            )
            return filtered_tasks

        if list_id:
            tasks = await self.task_repo.get_by_user_and_list(user_id, list_id)
            logger.info(
                f"Found {len(tasks)} tasks for user_id={user_id} with list_id={list_id}"
            )
            return tasks

        if status:
            tasks = await self.task_repo.get_by_user_and_status(user_id, status)
            logger.info(
                f"Found {len(tasks)} tasks for user_id={user_id} with status={status}"
            )
            return tasks

        tasks = await self.task_repo.get_by_user(user_id)
        logger.info(f"Found {len(tasks)} tasks for user_id={user_id}")
        return tasks

    async def get_task(self, id: UUID, user_id: UUID) -> Task:
        logger.debug(f"Fetching task id={id} for user_id={user_id}")
        task = await self.task_repo.get_by_id_and_user(id, user_id)
        if not task:
            logger.warning(f"Task not found: id={id}, user_id={user_id}")
            raise NotFoundError(resource="task", resource_id=str(id))
        return task

    async def create_task(self, data: TaskCreate, user_id: UUID) -> Task:
        logger.info(
            f"Creating task '{data.title}' for user_id={user_id}, "
            f"task_list_id={data.task_list_id}"
        )
        await self.get_task_list(data.task_list_id, user_id)
        if data.category_id:
            await self.activity_service.get_category(data.category_id, user_id)
        task = await self.task_repo.create(**data.model_dump(), user_id=user_id)
        logger.success(f"Task created: id={task.id}, title='{task.title}'")
        return task

    async def update_task(self, id: UUID, data: TaskUpdate, user_id: UUID) -> Task:
        logger.info(f"Updating task id={id} for user_id={user_id}")
        task = await self.get_task(id, user_id)
        update_data = data.model_dump(exclude_unset=True)

        if update_data.get("task_list_id"):
            await self.get_task_list(update_data["task_list_id"], user_id)
        if update_data.get("category_id"):
            await self.activity_service.get_category(
                update_data["category_id"],
                user_id,
            )

        updated = await self.task_repo.update(task, update_data)
        logger.success(f"Task updated: id={id}")
        return updated

    async def delete_task(self, id: UUID, user_id: UUID) -> None:
        logger.info(f"Deleting task id={id} for user_id={user_id}")
        await self.get_task(id, user_id)
        try:
            await self.task_repo.delete(id)
            logger.success(f"Task deleted: id={id}")
        except IntegrityError as e:
            logger.error(f"Cannot delete task id={id}: has associated dependencies")
            raise DependencyConflictError(
                resource="task",
                detail="Cannot delete task because it has associated dependencies",
            ) from e

    async def generate_occurrences(
        self,
        id: UUID,
        user_id: UUID,
        count: int = 10,
    ) -> list[Task]:
        logger.info(
            f"Generating occurrences for task id={id}, user_id={user_id}, count={count}"
        )
        task = await self.get_task(id, user_id)
        if not task.recurrence_rule:
            logger.error(
                "Cannot generate occurrences for task "
                f"id={id}: recurrence_rule is missing"
            )
            raise BadRequestError(detail="Task has no recurrence rule")

        task_start_date = task.scheduled_date or date.today()
        try:
            parsed_rule = rrulestr(
                task.recurrence_rule,
                dtstart=datetime.combine(task_start_date, datetime.min.time()),
            )
        except ValueError as e:
            logger.error(
                f"Invalid recurrence rule for task id={id}: {task.recurrence_rule}"
            )
            raise BadRequestError(detail="Invalid recurrence rule") from e

        if isinstance(parsed_rule, datetime):
            logger.error(
                f"Invalid recurrence rule for task id={id}: expected recurrence set"
            )
            raise BadRequestError(detail="Invalid recurrence rule")

        rule = cast(rrule | rruleset, parsed_rule)

        excluded_dates = set(task.exception_dates or [])
        all_user_tasks = await self.task_repo.get_by_user(user_id)
        existing_occurrence_dates = {
            existing_task.scheduled_date.isoformat()
            for existing_task in all_user_tasks
            if existing_task.id != task.id
            and existing_task.task_list_id == task.task_list_id
            and existing_task.title == task.title
            and existing_task.scheduled_date is not None
            and not existing_task.recurrence_rule
        }

        current_occurrence = rule.after(
            datetime.combine(task_start_date, datetime.min.time()),
            inc=True,
        )

        created_tasks: list[Task] = []
        while current_occurrence and len(created_tasks) < count:
            occurrence_date = current_occurrence.date()
            occurrence_date_str = occurrence_date.isoformat()
            if occurrence_date <= task_start_date:
                current_occurrence = rule.after(current_occurrence, inc=False)
                continue

            if (
                occurrence_date_str in excluded_dates
                or occurrence_date_str in existing_occurrence_dates
            ):
                current_occurrence = rule.after(current_occurrence, inc=False)
                continue

            new_task = await self.task_repo.create(
                user_id=user_id,
                task_list_id=task.task_list_id,
                category_id=task.category_id,
                title=task.title,
                description=task.description,
                status="todo",
                priority=task.priority,
                due_date=None,
                scheduled_date=occurrence_date,
                scheduled_start_time=task.scheduled_start_time,
                scheduled_end_time=task.scheduled_end_time,
                estimated_duration_minutes=task.estimated_duration_minutes,
                position=task.position,
            )
            created_tasks.append(new_task)
            existing_occurrence_dates.add(occurrence_date_str)
            current_occurrence = rule.after(current_occurrence, inc=False)

        logger.success(
            f"Generated {len(created_tasks)} occurrences for task "
            f"id={id}, user_id={user_id}"
        )
        return created_tasks

    async def generate_rolling_occurrences(
        self,
        user_id: UUID,
        horizon_days: int = 14,
    ) -> dict[str, int]:
        logger.info(
            "Running rolling occurrence generation for "
            f"user_id={user_id}, horizon_days={horizon_days}"
        )
        tasks = await self.task_repo.get_by_user(user_id)
        recurring_tasks = [task for task in tasks if task.recurrence_rule]
        horizon_end_date = date.today() + timedelta(days=horizon_days)

        total_created = 0
        for recurring_task in recurring_tasks:
            existing_future = [
                task
                for task in tasks
                if task.id != recurring_task.id
                and task.task_list_id == recurring_task.task_list_id
                and task.title == recurring_task.title
                and task.status == "todo"
                and task.scheduled_date is not None
                and date.today() <= task.scheduled_date <= horizon_end_date
                and not task.recurrence_rule
            ]

            if len(existing_future) >= 3:
                continue

            needed = 3 - len(existing_future)
            generated_tasks = await self.generate_occurrences(
                recurring_task.id,
                user_id,
                count=needed,
            )
            total_created += len(generated_tasks)
            tasks.extend(generated_tasks)

        logger.success(
            "Rolling occurrence generation complete for "
            f"user_id={user_id}: created_count={total_created}, "
            f"recurring_tasks_checked={len(recurring_tasks)}"
        )
        return {
            "created_count": total_created,
            "recurring_tasks_checked": len(recurring_tasks),
        }

    async def complete_task(
        self, id: UUID, user_id: UUID, data: TaskCompleteRequest
    ) -> Task:
        logger.info(f"Completing task id={id} for user_id={user_id}")
        task = await self.get_task(id, user_id)
        updated_task = await self.task_repo.update(task, {"status": "done"})

        if data.add_to_tracker:
            logger.info(f"Creating activity from completed task id={id}")
            category_id = data.category_id or task.category_id
            if not category_id:
                logger.error(
                    f"Cannot create activity for task id={id}: missing category"
                )
                raise BadRequestError(
                    detail="A category_id is required to add this task to tracker"
                )

            activity_date = data.date or task.scheduled_date
            start_time = data.start_time or task.scheduled_start_time
            end_time = data.end_time or task.scheduled_end_time
            if not activity_date or not start_time or not end_time:
                logger.error(
                    f"Cannot create activity for task id={id}: missing date/time fields"
                )
                raise BadRequestError(
                    detail=(
                        "date, start_time, and end_time are "
                        "required to add task to tracker"
                    )
                )

            activity = await self.activity_service.create_activity(
                ActivityCreate(
                    date=activity_date,
                    start_time=start_time,
                    end_time=end_time,
                    category_id=category_id,
                    notes=data.notes or task.description,
                ),
                user_id,
            )

            await self.task_activity_repo.create(
                task_id=task.id,
                activity_id=activity.id,
            )
            logger.success(
                f"Task id={id} linked to activity id={activity.id} "
                f"for user_id={user_id}"
            )
            updated_task = await self.get_task(id, user_id)

        logger.success(f"Task completed: id={id}")
        return updated_task

    async def convert_task_to_activity(
        self, id: UUID, user_id: UUID, data: ConvertToActivityRequest
    ) -> TaskActivity:
        logger.info(f"Converting task id={id} to activity for user_id={user_id}")
        task = await self.get_task(id, user_id)

        category_id = data.category_id or task.category_id
        if not category_id:
            logger.error(f"Cannot convert task id={id}: missing category")
            raise BadRequestError(
                detail="category_id is required to convert task to activity"
            )

        activity = await self.activity_service.create_activity(
            ActivityCreate(
                date=data.date,
                start_time=data.start_time,
                end_time=data.end_time,
                category_id=category_id,
                notes=data.notes or task.description,
            ),
            user_id,
        )

        task_activity = await self.task_activity_repo.create(
            task_id=task.id,
            activity_id=activity.id,
        )

        if task.status != "done":
            await self.task_repo.update(task, {"status": "done"})
            logger.info(f"Task id={id} marked as done after conversion")

        logger.success(
            f"Task converted to activity: task_id={id}, activity_id={activity.id}"
        )
        return task_activity
