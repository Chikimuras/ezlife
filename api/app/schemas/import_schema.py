from app.schemas.base import CamelModel


class ImportResponse(CamelModel):
    groups_created: int
    categories_created: int
    activities_created: int
    errors: list[str]
