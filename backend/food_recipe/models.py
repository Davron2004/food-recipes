import uuid
from functools import wraps
from flask import abort, url_for
from dataclasses import dataclass

from flask_jwt_extended import get_jwt_identity

from food_recipe import db
from food_recipe.config import ROLE_EDITOR, ROLE_MANAGER


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_jwt_identity = get_jwt_identity()
            admin = AdminAccount.query.filter_by(admin_login=current_jwt_identity['admin_login']).first()
            if admin.admin_role != ROLE_MANAGER and admin.admin_role != role:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

unit_enum = db.Enum('pinch', 'kg', 'gram', 'piece', 'ml', 'liter', 'cup', name="unit_enum")

@dataclass
class AdminAccount(db.Model):
    __tablename__ = "admin_account"

    id = db.Column(db.Integer, primary_key=True)
    admin_login = db.Column(db.String(150), unique=True, nullable=False)
    admin_password_hash = db.Column(db.String(255), nullable=False)
    admin_role = db.Column(db.String(50), nullable=False, default=ROLE_EDITOR)


@dataclass
class AppActivation(db.Model):
    __tablename__ = "app_activation"

    id = db.Column(db.Integer, primary_key=True)
    activation_code = db.Column(db.String(50), unique=True, nullable=False)
    activations_limit = db.Column(db.Integer, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)


@dataclass
class UserAccount(db.Model):
    __tablename__ = "user_account"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    installation_token_hash = db.Column(db.String(255), unique=True, nullable=False)
    app_activation_id = db.Column(db.Integer, db.ForeignKey("app_activation.id", ondelete="RESTRICT"), nullable=False)

    app_activation = db.relationship("AppActivation", backref=db.backref("user_accounts", cascade="all, delete-orphan"))


@dataclass
class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __str__(self) -> str:
        return self.name
    
    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }


@dataclass
class Ingredient(db.Model):
    __tablename__ = "ingredient"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __str__(self) -> str:
        return self.name
    
    def to_json(self):
        return {
            "id": self.id,
            "name": self.name
        }


@dataclass
class Recipe(db.Model):
    __tablename__ = "recipe"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    needs_auth = db.Column(db.Boolean, nullable=False, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    category = db.relationship('Category', backref=db.backref('recipe', lazy=True, cascade="all,delete"))

    def __str__(self) -> str:
        return self.name
    
    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "instructions": self.instructions,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "needs_auth": self.needs_auth,
            "category": self.category.to_json(),
            "ingredients": [ing.to_json() for ing in RecipeIngredient.query.filter(RecipeIngredient.recipe_id == self.id).all()],
            "pictures": [picture.to_json() for picture in Picture.query.filter(Picture.recipe_id == self.id).all()],
        }
    

@dataclass
class Picture(db.Model):
    __tablename__ = "picture"

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=True)

    recipe = db.relationship('Recipe', backref=db.backref('picture', lazy=True, cascade="all,delete"))

    def to_json(self):
        return {
            "url": url_for("admin_main.return_pic", pic_id=self.id, _external=True)
        }
    
@dataclass
class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredient'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(unit_enum, nullable=False)

    ingredient = db.relationship('Ingredient', backref='recipe_ingredient')
    recipe = db.relationship('Recipe', backref='recipe_ingredient')

    def to_json(self):
        return {
            "ingredient": self.ingredient.to_json(),
            "qty": self.quantity,
            "unit": self.unit
        }
    
@dataclass
class IngredientUnit(db.Model):
    __tablename__ = 'ingredient_unit'

    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True, nullable=False)
    unit = db.Column(unit_enum, nullable=False)

    def to_json(self):
        return {
            "ingredient_id": self.ingredient_id,
            "unit": self.unit
        }