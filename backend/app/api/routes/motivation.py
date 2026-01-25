from pydantic import Field
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Response

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.base import BaseSchema
from app.services.avatars import RandomAvatarsProvider
from app.services.motivation import MotivationMessagesProvider

router = APIRouter()

motivation_provider = MotivationMessagesProvider()
avatars_provider = RandomAvatarsProvider()


class TodoListDoneDto(BaseSchema):
    task_title: str | None = Field(default=None, alias="taskTitle")


@router.post("/list-done")
async def list_done(dto: TodoListDoneDto, current_user: User = Depends(get_current_user)) -> str:
    msg = await motivation_provider.generate_async(str(current_user.id), dto.task_title)
    return msg


@router.get("/random-avatar/{avatar_type}")
async def random_avatar(avatar_type: str, current_user: User = Depends(get_current_user)):
    if avatar_type not in {RandomAvatarsProvider.MINIAVS, RandomAvatarsProvider.BOTTS}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid avatar type.")

    svg = await avatars_provider.get_avatar_async(avatar_type)
    if not svg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return Response(content=svg, media_type="image/svg+xml")
