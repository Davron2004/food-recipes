import io
from flask import Blueprint, jsonify, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from food_recipe import app, show_last_change
from food_recipe.models import Picture, Recipe, RecipeIngredient


main = Blueprint('client_main', __name__)


def is_activated_app():
    current_jwt_identity = get_jwt_identity()
    is_activated_app = current_jwt_identity and current_jwt_identity['installation_token_hash']
    return is_activated_app


@main.route("/last-change", methods=['GET'])
@jwt_required(optional=True)
def return_last_change():
    """Get the last change timestamp.
    ---
    get:
      description: Retrieve the timestamp of the last change.
      security:
        - Bearer: []
      responses:
        200:
          description: Last change timestamp
          content:
            application/json:
              schema:
                type: string
                format: date-time
    """
    return show_last_change()


@main.route("/recipes", methods=['GET'])
@jwt_required(optional=True)
def get_recipes():
    """Get all recipes.
    ---
    get:
      description: Retrieve all recipes.
      security:
        - Bearer: []
      responses:
        200:
          description: A list of recipes
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
    """
    if is_activated_app():
        recipes = Recipe.query.order_by(Recipe.id).all()
    else:
        recipes = Recipe.query.order_by(Recipe.id).limit(10).all()

    response = []
    for recipe in recipes:
        recipe_data = recipe.to_json()
        
        # Get picture IDs for the recipe
        pics = Picture.query.filter(Picture.recipe_id == recipe.id).all()
        recipe_data["pictures"] = [pic.id for pic in pics]

        # Get ingredients for the recipe
        ingredients = RecipeIngredient.query.filter(RecipeIngredient.recipe_id == recipe.id).all()
        ingredient_data = []
        for ingredient in ingredients:
            ingredient_data.append({
                "ingredient": ingredient.ingredient.to_json(),
                "qty": ingredient.quantity,
                "unit": ingredient.unit
            })
        recipe_data["ingredients"] = ingredient_data

        response.append(recipe_data)

    return jsonify(response)


@main.route("/pictures/<string:pic_id>", methods=['GET'])
@jwt_required(optional=True)
def return_pic(pic_id):
    """Get a picture by ID.
    ---
    get:
      description: Retrieve a picture by its ID.
      security:
        - Bearer: []
      parameters:
        - in: path
          name: pic_id
          required: True
          schema:
            type: integer
      responses:
        200:
          description: A picture object
          content:
            application/json:
              schema:
                type: object
    """

    # TODO: Check if the app is activated. If not, return only allowed pictures.
    if is_activated_app():
        pass
    else:
        pass

    pic = Picture.query.get_or_404(pic_id)
    
    return send_file(
        io.BytesIO(pic.image_data),
        mimetype='image/jpeg',
        as_attachment=False,
    )
