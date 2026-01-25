from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user, get_db
from app.models.todo import TodoList, TodoTask
from app.models.user import User
from app.schemas.todo import (
    TodoListCreateRequest,
    TodoListResponse,
    TodoListUpdateRequest,
    TodoTaskCreateRequest,
    TodoTaskPatchRequest,
    TodoTaskResponse,
    TodoTaskUpdateRequest,
)

router = APIRouter()


def to_task_response(task: TodoTask) -> TodoTaskResponse:
    return TodoTaskResponse(
        id=task.id,
        todo_list_id=task.todo_list_id,
        title=task.title,
        description=task.description,
        is_completed=task.is_completed,
    )


def to_list_response(todo_list: TodoList) -> TodoListResponse:
    items = [to_task_response(t) for t in todo_list.items]
    return TodoListResponse(
        id=todo_list.id,
        name=todo_list.name,
        created_at=todo_list.created_at,
        updated_at=todo_list.updated_at,
        items=items,
    )


@router.get("/lists", response_model=list[TodoListResponse])
def get_lists(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = (
        select(TodoList)
        .where(TodoList.user_id == current_user.id)
        .options(selectinload(TodoList.items))
        .order_by(TodoList.created_at.desc())
    )
    lists = db.scalars(stmt).all()
    return [to_list_response(l) for l in lists]


@router.get("/lists/{list_id}", response_model=TodoListResponse)
def get_list(list_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = (
        select(TodoList)
        .where(TodoList.id == list_id, TodoList.user_id == current_user.id)
        .options(selectinload(TodoList.items))
    )
    todo_list = db.scalars(stmt).first()
    if todo_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return to_list_response(todo_list)


@router.post("/lists", response_model=TodoListResponse, status_code=status.HTTP_201_CREATED)
def create_list(
    request: TodoListCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    name = request.name.strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Name is required.")

    now = datetime.now(timezone.utc)
    todo_list = TodoList(name=name, created_at=now,
                         updated_at=now, user_id=current_user.id)
    db.add(todo_list)
    db.commit()
    db.refresh(todo_list)
    todo_list.items = []
    return to_list_response(todo_list)


@router.put("/lists/{list_id}", response_model=TodoListResponse)
def update_list(
    list_id: UUID,
    request: TodoListUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(TodoList)
        .where(TodoList.id == list_id, TodoList.user_id == current_user.id)
        .options(selectinload(TodoList.items))
    )
    todo_list = db.scalars(stmt).first()
    if todo_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    name = request.name.strip()
    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Name is required.")

    todo_list.name = name
    db.commit()
    return to_list_response(todo_list)


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_list(list_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(TodoList).where(TodoList.id == list_id, TodoList.user_id ==
                                  current_user.id).options(selectinload(TodoList.items))
    todo_list = db.scalars(stmt).first()
    if todo_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    db.delete(todo_list)
    db.commit()
    return None


@router.get("/lists/{list_id}/tasks", response_model=list[TodoTaskResponse])
def get_tasks(list_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    list_exists = db.scalars(select(TodoList.id).where(
        TodoList.id == list_id, TodoList.user_id == current_user.id)).first()
    if not list_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    tasks = db.scalars(select(TodoTask).where(
        TodoTask.todo_list_id == list_id).order_by(TodoTask.title)).all()
    return [to_task_response(t) for t in tasks]


@router.post("/lists/{list_id}/tasks", response_model=TodoTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    list_id: UUID,
    request: TodoTaskCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    list_exists = db.scalars(select(TodoList.id).where(
        TodoList.id == list_id, TodoList.user_id == current_user.id)).first()
    if not list_exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    title = request.title.strip()
    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Title is required.")

    task = TodoTask(
        title=title,
        description=request.description.strip() if request.description else None,
        is_completed=False,
        todo_list_id=list_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return to_task_response(task)


@router.put("/tasks/{task_id}", response_model=TodoTaskResponse)
def update_task(
    task_id: UUID,
    request: TodoTaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(TodoTask).options(selectinload(
        TodoTask.todo_list)).where(TodoTask.id == task_id)
    task = db.scalars(stmt).first()
    if task is None or task.todo_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    title = request.title.strip()
    if not title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Title is required.")

    task.title = title
    task.description = request.description.strip() if request.description else None
    task.is_completed = request.is_completed
    db.commit()
    return to_task_response(task)


@router.patch("/tasks/{task_id}", response_model=TodoTaskResponse)
def patch_task(
    task_id: UUID,
    request: TodoTaskPatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(TodoTask).options(selectinload(
        TodoTask.todo_list)).where(TodoTask.id == task_id)
    task = db.scalars(stmt).first()
    if task is None or task.todo_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if request.is_completed is not None:
        task.is_completed = request.is_completed

    db.commit()
    return to_task_response(task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(TodoTask).options(selectinload(
        TodoTask.todo_list)).where(TodoTask.id == task_id)
    task = db.scalars(stmt).first()
    if task is None or task.todo_list.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    db.delete(task)
    db.commit()
    return None
