from datetime import date as date_type
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity, Category, GlobalConstraints, Group
from app.repositories.user_repository import BaseRepository


class GroupRepository(BaseRepository[Group]):
    def __init__(self, session: AsyncSession):
        super().__init__(Group, session)

    async def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Group]:
        result = await self.session.execute(
            select(Group).where(Group.user_id == user_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(self, id: UUID, user_id: UUID) -> Group | None:
        result = await self.session.execute(
            select(Group).where(Group.id == id, Group.user_id == user_id)
        )
        return result.scalars().first()

    async def update(self, db_obj: Group, obj_in_data: dict) -> Group:
        for field, value in obj_in_data.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: UUID) -> None:
        await self.session.execute(delete(Group).where(Group.id == id))
        await self.session.commit()


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(Category, session)

    async def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Category]:
        result = await self.session.execute(
            select(Category)
            .where(Category.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(self, id: UUID, user_id: UUID) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.id == id, Category.user_id == user_id)
        )
        return result.scalars().first()

    async def update(self, db_obj: Category, obj_in_data: dict) -> Category:
        for field, value in obj_in_data.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: UUID) -> None:
        await self.session.execute(delete(Category).where(Category.id == id))
        await self.session.commit()


class GlobalConstraintsRepository(BaseRepository[GlobalConstraints]):
    def __init__(self, session: AsyncSession):
        super().__init__(GlobalConstraints, session)

    async def get_by_user(self, user_id: UUID) -> GlobalConstraints | None:
        result = await self.session.execute(
            select(GlobalConstraints).where(GlobalConstraints.user_id == user_id)
        )
        return result.scalars().first()

    async def update(
        self, db_obj: GlobalConstraints, obj_in_data: dict
    ) -> GlobalConstraints:
        for field, value in obj_in_data.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj


class ActivityRepository(BaseRepository[Activity]):
    def __init__(self, session: AsyncSession):
        super().__init__(Activity, session)

    async def get_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Activity]:
        result = await self.session.execute(
            select(Activity)
            .where(Activity.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_user_and_date(
        self, user_id: UUID, date: date_type
    ) -> list[Activity]:
        result = await self.session.execute(
            select(Activity)
            .where(Activity.user_id == user_id, Activity.date == date)
            .order_by(Activity.start_time)
        )
        return list(result.scalars().all())

    async def get_by_id_and_user(self, id: UUID, user_id: UUID) -> Activity | None:
        result = await self.session.execute(
            select(Activity).where(Activity.id == id, Activity.user_id == user_id)
        )
        return result.scalars().first()

    async def update(self, db_obj: Activity, obj_in_data: dict) -> Activity:
        for field, value in obj_in_data.items():
            setattr(db_obj, field, value)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: UUID) -> None:
        await self.session.execute(delete(Activity).where(Activity.id == id))
        await self.session.commit()
