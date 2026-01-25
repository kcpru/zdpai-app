import json
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.post import Post, PostComment
from app.models.todo import TodoList, TodoTask
from app.models.user import User


def seed_data() -> None:
    db: Session = SessionLocal()
    try:
        if db.query(User).first():
            return

        admin = User(id=uuid4(), username="admin", email="admin@example.com",
                     password_hash=hash_password("password"), is_admin=True)
        user1 = User(id=uuid4(), username="john_doe", email="john@example.com",
                     password_hash=hash_password("password123"))
        user2 = User(id=uuid4(), username="jane_smith", email="jane@example.com",
                     password_hash=hash_password("password123"))
        user3 = User(id=uuid4(), username="bob_wilson", email="bob@example.com",
                     password_hash=hash_password("password123"))

        db.add_all([admin, user1, user2, user3])
        db.flush()

        admin_list1 = TodoList(
            id=uuid4(),
            name="Work Projects",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            user_id=admin.id,
        )
        admin_list2 = TodoList(
            id=uuid4(),
            name="Personal Goals",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            user_id=admin.id,
        )
        db.add_all([admin_list1, admin_list2])
        db.flush()

        tasks1 = [
            TodoTask(id=uuid4(), title="Complete project documentation",
                     description="Write comprehensive documentation for the new API endpoints", is_completed=True, todo_list_id=admin_list1.id),
            TodoTask(id=uuid4(), title="Review pull requests", description="Review and merge pending pull requests from the team",
                     is_completed=False, todo_list_id=admin_list1.id),
            TodoTask(id=uuid4(), title="Deploy to production", description="Deploy latest version to production server",
                     is_completed=False, todo_list_id=admin_list1.id),
        ]
        tasks2 = [
            TodoTask(id=uuid4(), title="Learn new programming language",
                     description="Complete Rust programming course", is_completed=False, todo_list_id=admin_list2.id),
            TodoTask(id=uuid4(), title="Exercise 3 times a week",
                     description="Maintain healthy workout routine", is_completed=True, todo_list_id=admin_list2.id),
        ]
        admin_list1.items = tasks1
        admin_list2.items = tasks2
        db.add_all(tasks1 + tasks2)
        db.flush()

        user1_list = TodoList(id=uuid4(), name="Shopping List", created_at=datetime.now(
            timezone.utc), updated_at=datetime.now(timezone.utc), user_id=user1.id)
        user2_list = TodoList(id=uuid4(), name="Travel Plans", created_at=datetime.now(
            timezone.utc), updated_at=datetime.now(timezone.utc), user_id=user2.id)
        user3_list = TodoList(id=uuid4(), name="Home Renovation", created_at=datetime.now(
            timezone.utc), updated_at=datetime.now(timezone.utc), user_id=user3.id)
        db.add_all([user1_list, user2_list, user3_list])
        db.flush()

        user1_tasks = [
            TodoTask(id=uuid4(), title="Buy groceries", description="Milk, eggs, bread, vegetables",
                     is_completed=False, todo_list_id=user1_list.id),
            TodoTask(id=uuid4(), title="Get gas", description="Fill up the car",
                     is_completed=True, todo_list_id=user1_list.id),
        ]
        user2_tasks = [
            TodoTask(id=uuid4(), title="Book flights", description="Book return flights to Paris for summer vacation",
                     is_completed=False, todo_list_id=user2_list.id),
            TodoTask(id=uuid4(), title="Reserve hotel", description="Reserve 5-star hotel in central Paris",
                     is_completed=False, todo_list_id=user2_list.id),
        ]
        user3_tasks = [
            TodoTask(id=uuid4(), title="Paint living room", description="Paint walls in light blue color",
                     is_completed=False, todo_list_id=user3_list.id),
            TodoTask(id=uuid4(), title="Install new fixtures",
                     description="Replace old light fixtures with new ones", is_completed=True, todo_list_id=user3_list.id),
        ]
        user1_list.items = user1_tasks
        user2_list.items = user2_tasks
        user3_list.items = user3_tasks
        db.add_all(user1_tasks + user2_tasks + user3_tasks)
        db.flush()

        def todo_list_to_json(list_obj: TodoList) -> str:
            items = [
                {
                    "id": str(item.id),
                    "title": item.title,
                    "description": item.description,
                    "isCompleted": item.is_completed,
                }
                for item in list_obj.items
            ]
            payload = {
                "id": str(list_obj.id),
                "name": list_obj.name,
                "createdAt": list_obj.created_at.isoformat(),
                "updatedAt": list_obj.updated_at.isoformat(),
                "userId": str(list_obj.user_id),
                "items": items,
            }
            return json.dumps(payload)

        posts = [
            Post(id=uuid4(), content="Just completed my work project documentation! Really proud of the comprehensive API guide I created. Ready to share with the team. 🚀",
                 created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc), todo_list_as_json=todo_list_to_json(admin_list1)),
            Post(id=uuid4(), content="Started learning Rust! Really excited about this new journey. Already completed the first few chapters of the book. #programming #rust",
                 created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc), todo_list_as_json=todo_list_to_json(admin_list2)),
            Post(id=uuid4(), content="Finally got all my groceries! Meal prep for the week is ready. Time to cook! 👨‍🍳", created_at=datetime.now(
                timezone.utc), updated_at=datetime.now(timezone.utc), todo_list_as_json=todo_list_to_json(user1_list)),
            Post(id=uuid4(), content="Booked my dream vacation to Paris! Can't wait for summer. Planning to visit the Eiffel Tower, Louvre Museum, and many cafes! ✈️🇫🇷",
                 created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc), todo_list_as_json=todo_list_to_json(user2_list)),
            Post(id=uuid4(), content="Living room renovation is coming along great! Just installed the new light fixtures and they look amazing. Next step: painting! 🏠",
                 created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc), todo_list_as_json=todo_list_to_json(user3_list)),
        ]
        db.add_all(posts)
        db.flush()

        comments = [
            PostComment(id=uuid4(), post_id=posts[0].id, user_id=user1.id,
                        comment_text="That's awesome! Great work on the documentation! 👍", likes_count=1),
            PostComment(id=uuid4(), post_id=posts[1].id, user_id=user2.id,
                        comment_text="Rust is so cool! Good luck with your learning journey!", likes_count=2),
            PostComment(id=uuid4(), post_id=posts[3].id, user_id=user3.id,
                        comment_text="Paris is amazing! Don't forget to visit the catacombs!", likes_count=1),
            PostComment(id=uuid4(), post_id=posts[4].id, user_id=admin.id,
                        comment_text="Looking beautiful! Love the light fixtures choice!", likes_count=1),
        ]
        db.add_all(comments)

        db.commit()
    finally:
        db.close()
