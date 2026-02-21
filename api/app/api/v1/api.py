from fastapi import APIRouter

from app.api.v1.endpoints import activity, auth, import_, insights, task, timer

api_router = APIRouter()
api_router.include_router(auth.router, tags=["login"])
api_router.include_router(activity.router, tags=["activity"])
api_router.include_router(task.router, tags=["tasks"])
api_router.include_router(import_.router, prefix="/import", tags=["import"])
api_router.include_router(insights.router, prefix="/insights", tags=["insights"])
api_router.include_router(timer.router, prefix="/timer", tags=["timer"])
