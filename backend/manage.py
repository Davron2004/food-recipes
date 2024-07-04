import os

os.environ['FLASK_APP'] = 'food_recipe/__init__.py'
os.environ['FLASK_RUN_PORT'] = os.environ.get('PORT') # because Heroku uses PORT env variable

from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash
from food_recipe import app, db
import food_recipe
from food_recipe.config import ROLE_EDITOR, ROLE_MANAGER
from food_recipe.utils import optimize_picture
from sqlalchemy import text


cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("create_auth_tables")
def create_auth_tables():
    food_recipe.models.AdminAccount.__table__.create(db.engine)
    food_recipe.models.AppActivation.__table__.create(db.engine)
    food_recipe.models.UserAccount.__table__.create(db.engine)
    db.session.commit()

@cli.command("create_admins")
def create_admin():
    manager = food_recipe.models.AdminAccount(
        admin_login='manager',
        admin_password_hash=generate_password_hash('changeme'),
        admin_role=ROLE_MANAGER)
    db.session.add(manager)

    editor = food_recipe.models.AdminAccount(
        admin_login='editor',
        admin_password_hash=generate_password_hash('changeme'),
        admin_role=ROLE_EDITOR)
    db.session.add(editor)

    db.session.commit()

@cli.command("create_categories")
def create_categories():
    from food_recipe.models import Category
    categories = [
        "Desserts",
        "Bakery",
        "Breakfasts",
        "Snacks",
        "Soups",
        "Main Courses",
        "Salads",
        "Dinners"
    ]
    for category in categories:
        db.session.add(Category(name=category))
    db.session.commit()

@cli.command("drop_db")
def drop_db():
    db.drop_all()
    db.session.commit()

@cli.command("migrate_images_to_db")
def migrate_images_to_db():
    print("Migrating images to database")

    db.session.execute(text("ALTER TABLE picture ADD COLUMN image_data BYTEA NULL"))

    from food_recipe.models import Picture
    pics = Picture.query.all()
    for pic in pics:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{pic.recipe_id}/{pic.name}")
        if os.path.exists(file_path):
            print(f"Processing {pic.id} {pic.name} {pic.recipe_id}")
            pic.image_data = optimize_picture(file_path)
        else:
            print(f"File {file_path} does not exist")
            db.session.delete(pic)

    db.session.commit()

    db.session.execute(text("ALTER TABLE picture ALTER COLUMN image_data SET NOT NULL"))
    db.session.commit()


if __name__ == "__main__":
    cli()
