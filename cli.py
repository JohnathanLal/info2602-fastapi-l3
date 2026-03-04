import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User, Todo, Category
from sqlmodel import select

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db:
        drop_all()
        create_db_and_tables()

        bob = User(username='bob', email='bob@mail.com')
        bob.set_password("bobpass")
        db.add(bob)
        db.commit()
        db.refresh(bob)

        todo = Todo(text='Wash dishes', user_id=bob.id)
        db.add(todo)
        db.commit()
        db.refresh(todo)

        print("Database Initialized")


@cli.command()
def add_task(username: str, task: str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        user.todos.append(Todo(text=task))
        db.add(user)
        db.commit()
        print("Task added for user")


@cli.command()
def toggle_todo(todo_id: int, username: str):
    with get_session() as db:
        todo = db.exec(select(Todo).where(Todo.id == todo_id)).one_or_none()
        if not todo:
            print("Todo doesn't exist")
            return
        if todo.user.username != username:
            print("Todo doesn't belong to that user")
            return
        todo.toggle()
        db.add(todo)
        db.commit()
        print(f"Todo item's done state set to {todo.done}")


@cli.command()
def list_todo_categories(todo_id: int, username: str):
    with get_session() as db:
        todo = db.exec(select(Todo).where(Todo.id == todo_id)).one_or_none()
        if not todo:
            print("Todo doesn't exist")
            return
        if todo.user.username != username:
            print("Todo doesn't belong to that user")
            return
        print([category.text for category in todo.categories])


@cli.command()
def create_category(username: str, cat_text: str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        category = db.exec(select(Category).where(Category.text==cat_text, Category.user_id==user.id)).one_or_none()
        if category:
            print("Category exists! Skipping creation")
            return
        new_category = Category(text=cat_text, user_id=user.id)
        db.add(new_category)
        db.commit()
        print("Category added for user")


@cli.command()
def list_user_categories(username: str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username==username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        categories = db.exec(select(Category).where(Category.user_id==user.id)).all()
        print([cat.text for cat in categories])

@cli.command()
def assign_category_to_todo(username: str, todo_id: int, category_text: str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username==username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        category = db.exec(select(Category).where(Category.text==category_text, Category.user_id==user.id)).one_or_none()
        if not category:
            category = Category(text=category_text, user_id=user.id)
            db.add(category)
            db.commit()
            db.refresh(category)
            print("Category didn't exist for user, creating it")
        todo = db.exec(select(Todo).where(Todo.id==todo_id, Todo.user_id==user.id)).one_or_none()
        if not todo:
            print("Todo doesn't exist for user")
            return
        todo.categories.append(category)
        db.add(todo)
        db.commit()
        print("Added category to todo")

@cli.command()
def list_todos():
    with get_session() as db:
        todos = db.exec(select(Todo)).all()
        if not todos:
            print("No todos found.")
            return
        for todo in todos:
            print(f"ID:{todo.id}, Text:{todo.text}, User:{todo.user.username}, Done:{todo.done}")


@cli.command()
def delete_todo(todo_id: int):
    with get_session() as db:
        todo = db.exec(select(Todo).where(Todo.id==todo_id)).one_or_none()
        if not todo:
            print("Todo not found.")
            return
        db.delete(todo)
        db.commit()
        print(f"Todo ID {todo_id} deleted.")


@cli.command()
def complete_user_todos(username: str):
    with get_session() as db:
        user = db.exec(select(User).where(User.username==username)).one_or_none()
        if not user:
            print("User doesn't exist")
            return
        todos = user.todos
        if not todos:
            print("User has no todos.")
            return
        for todo in todos:
            todo.done = True
            db.add(todo)
        db.commit()
        print(f"All todos for {username} are now marked as complete.")


if __name__ == "__main__":
    cli()