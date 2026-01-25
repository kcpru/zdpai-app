import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user, get_db
from app.models.post import Post, PostComment
from app.models.todo import TodoList
from app.models.user import User
from app.schemas.post import (
    CreatePostCommentRequest,
    CreatePostRequest,
    LikePostCommentRequest,
    LikePostRequest,
    PostCommentResponse,
    PostResponse,
)

router = APIRouter()


def to_post_response(post: Post) -> PostResponse:
    comments = [
        PostCommentResponse(
            id=c.id,
            post_id=c.post_id,
            user_id=c.user_id,
            comment_text=c.comment_text,
            likes_count=c.likes_count,
        )
        for c in post.comments
    ]
    return PostResponse(
        id=post.id,
        todo_list_as_json=post.todo_list_as_json,
        content=post.content,
        likes_count=post.likes_count,
        created_at=post.created_at,
        updated_at=post.updated_at,
        comments=comments,
    )


def todo_list_to_json(todo_list: TodoList) -> str:
    items = [
        {
            "id": str(item.id),
            "title": item.title,
            "description": item.description,
            "isCompleted": item.is_completed,
        }
        for item in todo_list.items
    ]
    payload = {
        "id": str(todo_list.id),
        "name": todo_list.name,
        "createdAt": todo_list.created_at.isoformat(),
        "updatedAt": todo_list.updated_at.isoformat(),
        "userId": str(todo_list.user_id),
        "items": items,
    }
    return json.dumps(payload)


@router.get("", response_model=list[PostResponse])
def get_posts(
    start_index: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    offset = start_index if start_index >= 0 else 0
    stmt = (
        select(Post)
        .options(selectinload(Post.comments))
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(10)
    )
    posts = db.scalars(stmt).all()
    return [to_post_response(p) for p in posts]


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(Post).where(Post.id == post_id).options(
        selectinload(Post.comments))
    post = db.scalars(stmt).first()
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
    return to_post_response(post)


@router.post("", status_code=status.HTTP_200_OK)
def create_post(
    request: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(TodoList)
        .where(TodoList.id == request.todo_list_id, TodoList.user_id == current_user.id)
        .options(selectinload(TodoList.items))
    )
    todo_list = db.scalars(stmt).first()
    if todo_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Todo list not found.")

    now = datetime.now(timezone.utc)
    post = Post(
        content=request.content,
        todo_list_as_json=todo_list_to_json(todo_list),
        created_at=now,
        updated_at=now,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"id": post.id}


@router.post("/{post_id}/comments", response_model=PostCommentResponse)
def comment_on_post(
    post_id: UUID,
    request: CreatePostCommentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    comment_text = request.comment_text.strip()
    if not comment_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Comment text is required.")

    comment = PostComment(post_id=post_id, user_id=current_user.id,
                          comment_text=comment_text, likes_count=0)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return PostCommentResponse(
        id=comment.id,
        post_id=comment.post_id,
        user_id=comment.user_id,
        comment_text=comment.comment_text,
        likes_count=comment.likes_count,
    )


@router.post("/{post_id}/likes")
def like_post(
    post_id: UUID,
    request: LikePostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")

    if request.likes_count < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="LikesCount must be non-negative.")

    post.likes_count += request.likes_count
    db.commit()
    return {"postId": post_id, "likesCount": post.likes_count}


@router.post("/comments/{comment_id}/likes")
def like_comment(
    comment_id: UUID,
    request: LikePostCommentRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.get(PostComment, comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

    increment = request.likes_count if request is not None else 1
    if increment < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="LikesCount must be non-negative.")

    comment.likes_count += increment
    db.commit()
    return {"commentId": comment_id, "likesCount": comment.likes_count}
