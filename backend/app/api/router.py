from fastapi import APIRouter

from app.api.routes import admin, auth, health, motivation, post, todo, user

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/api/user", tags=["user"])
api_router.include_router(user.router, prefix="/api/user", tags=["user"])
api_router.include_router(todo.router, prefix="/api/todo", tags=["todo"])
api_router.include_router(post.router, prefix="/api/post", tags=["post"])
api_router.include_router(
    motivation.router, prefix="/api/motivation", tags=["motivation"])
api_router.include_router(admin.router, prefix="/api/admin", tags=["admin"])
