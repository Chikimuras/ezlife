from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task, TaskActivity, TaskList
from app.repositories.user_repository import BaseRepository


class TaskListRepository(BaseRepository[TaskList]):
    def __init__(self, session: AsyncSession):
        super().__init__(TaskList, session)

    async def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[TaskList]:
        result = await self.session.execute(
            select(TaskList)
            .where(TaskList.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(self, id: UUID, user_id: UUID) -> TaskList | None:
        result = await self.session.execute(
            select(TaskList).where(TaskList.id == id, TaskList.user_id == user_id)
        )
        return result.scalars().first()

    async def update(self, db_obj: TaskList, obj_in_data: dict) -> TaskList:
        for field, value in obj_in_data.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: UUID) -> None:
        await self.session.execute(delete(TaskList).where(TaskList.id == id))
        await self.session.commit()


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(Task, session)

    async def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Task]:
        result = await self.session.execute(
            select(Task)
            .options(selectinload(Task.task_activities))
            .where(Task.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_user_and_list(
        self, user_id: UUID, task_list_id: UUID
    ) -> list[Task]:
        result = await self.session.execute(
            select(Task)
            .options(selectinload(Task.task_activities))
            .where(
                Task.user_id == user_id,
                Task.task_list_id == task_list_id,
            )
        )
        return list(result.scalars().all())

    async def get_by_user_and_status(self, user_id: UUID, status: str) -> list[Task]:
        result = await self.session.execute(
            select(Task)
            .options(selectinload(Task.task_activities))
            .where(Task.user_id == user_id, Task.status == status)
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(self, id: UUID, user_id: UUID) -> Task | None:
        result = await self.session.execute(
            select(Task)
            .options(selectinload(Task.task_activities))
            .where(Task.id == id, Task.user_id == user_id)
        )
        return result.scalars().first()

    async def update(self, db_obj: Task, obj_in_data: dict) -> Task:
        for field, value in obj_in_data.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        result = await self.session.execute(
            select(Task)
            .options(selectinload(Task.task_activities))
            .where(Task.id == db_obj.id)
        )
        return result.scalars().one()

    async def create(self, **kwargs) -> Task:
        db_obj = Task(**kwargs)
        self.session.add(db_obj)
        await self.session.commit()
        result = await self.session.execute(
            select(Task)
            .options(selectinload(Task.task_activities))
            .where(Task.id == db_obj.id)
        )
        return result.scalars().one()

    async def delete(self, id: UUID) -> None:
        await self.session.execute(delete(Task).where(Task.id == id))
        await self.session.commit()


class TaskActivityRepository(BaseRepository[TaskActivity]):
    def __init__(self, session: AsyncSession):
        super().__init__(TaskActivity, session)

    async def get_by_task(self, task_id: UUID) -> list[TaskActivity]:
        result = await self.session.execute(
            select(TaskActivity).where(TaskActivity.task_id == task_id)
        )
        return list(result.scalars().all())

    async def get_by_activity(self, activity_id: UUID) -> TaskActivity | None:
        result = await self.session.execute(
            select(TaskActivity).where(TaskActivity.activity_id == activity_id)
        )
        return result.scalars().first()

    async def delete(self, id: UUID) -> None:
        await self.session.execute(delete(TaskActivity).where(TaskActivity.id == id))
        await self.session.commit()
