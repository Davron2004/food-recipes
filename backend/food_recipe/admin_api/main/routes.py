import io
from datetime import datetime

from flask import (
    Blueprint,
    jsonify,
    send_file,
    request,
    Response
)
from flask_jwt_extended import jwt_required

from food_recipe.utils import optimize_picture
from food_recipe import db, change_was_made
from food_recipe.models import Category, Ingredient, IngredientUnit, Recipe, Picture, RecipeIngredient, role_required
from food_recipe.config import ROLE_MANAGER, ROLE_EDITOR


main = Blueprint('admin_main', __name__)


# API endpoints that return all records in DB
@main.route("/categories", methods=['GET'])
@jwt_required()
@role_required(ROLE_EDITOR)
def get_categories():
    """Get all categories.
    ---
    get:
      description: Retrieve all categories.
      security:
        - Bearer: []
      responses:
        200:
          description: A list of categories
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
    """
    return jsonify([c.to_json() for c in Category.query.all()])


@main.route("/ingredients", methods=['GET'])
@jwt_required()
@role_required(ROLE_EDITOR)
def get_ingredients():
    """Get all ingredients.
    ---
    get:
      description: Retrieve all ingredients.
      security:
        - Bearer: []
      responses:
        200:
          description: A list of ingredients
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
    """
    return jsonify([i.to_json() for i in Ingredient.query.all()])


@main.route("/recipes", methods=['GET'])
@jwt_required()
@role_required(ROLE_EDITOR)
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
    recipes = Recipe.query.all()
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


@main.route("/ingredients/units", methods=['GET'])
@jwt_required()
@role_required(ROLE_EDITOR)
def get_ingredeint_units():
    """Get all ingredient units.
    ---
    get:
      description: Retrieve all ingredient units.
      security:
        - Bearer: []
      responses:
        200:
          description: A list of ingredient units
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
    """
    return jsonify([ing_unit.to_json() for ing_unit in IngredientUnit.query.all()])


# API endpoints that return a single record by ID
@main.route("/categories/<int:category_id>", methods=['GET'])
@jwt_required()
@role_required(ROLE_EDITOR)
def get_category(category_id):
    """Get a category by ID.
    ---
    get:
      description: Retrieve a category by its ID.
      security:
        - Bearer: []
      parameters:
        - in: path
          name: category_id
          required: True
          schema:
            type: integer
      responses:
        200:
          description: A category object
          content:
            application/json:
              schema:
                type: object
    """
    category = Category.query.get_or_404(category_id)
    return jsonify(category.to_json())


@main.route("/ingredients/<int:ingredient_id>", methods=['GET'])
@jwt_required()
@role_required(ROLE_EDITOR)
def get_ingredient(ingredient_id):
    """Get an ingredient by ID.
    ---
    get:
      description: Retrieve an ingredient by its ID.
      security:
        - Bearer: []
      parameters:
        - in: path
          name: ingredient_id
          required: True
          schema:
            type: integer
      responses:
        200:
          description: An ingredient object
          content:
            application/json:
              schema:
                type: object
    """
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    return jsonify(ingredient.to_json())


@main.route("/recipes/<int:rec_id>", methods=['GET'])
@jwt_required()
@role_required(ROLE_EDITOR)
def return_recipe(rec_id):
    """Get a recipe by ID.
    ---
    get:
      description: Retrieve a recipe by its ID.
      security:
        - Bearer: []
      parameters:
        - in: path
          name: rec_id
          required: True
          schema:
            type: integer
      responses:
        200:
          description: A recipe object
          content:
            application/json:
              schema:
                type: object
    """
    recipe = Recipe.query.get_or_404(rec_id)
    ingredients = RecipeIngredient.query.filter(RecipeIngredient.recipe_id == rec_id).all()
    pics = Picture.query.filter(Picture.recipe_id == rec_id).all()

    response = recipe.to_json()
    response["ingredients"] = [ing.to_json() for ing in ingredients]
    response["pictures"] = [pic.id for pic in pics]
    return jsonify(response)


@main.route("/pictures/<string:pic_id>", methods=['GET'])
def return_pic(pic_id):
    """Get a picture by ID.
    ---
    get:
      description: Retrieve a picture by its ID.
      # security:
      #   - Bearer: []
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
    pic = Picture.query.get_or_404(pic_id)
    return send_file(
        io.BytesIO(pic.image_data),
        mimetype='image/jpeg',
        as_attachment=False,
    )


@main.route("/recipes", methods = ['POST'])
@jwt_required()
@role_required(ROLE_EDITOR)
def create_recipe():
    """Create a new recipe.
    ---
    post:
      description: Create a new recipe.
      security:
        - Bearer: []
      requestBody:
        required: True
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                instructions:
                  type: string
                category:
                  type: integer
                ingredients:
                  type: string
                needs_auth:
                  type: boolean
                photo:
                  type: string
      responses:
        201:
          description: Recipe created
          content:
            application/json:
              schema:
                type: object
    """
    name = request.form['name']
    instructions = request.form['instructions']
    category_id = request.form['category']
    needs_auth = request.form.get('needs_auth', True)
    pics = request.files.getlist('pictures')
    
    # is a list of triples (int (ing_id), int (qty), unit_enum)
    ingredients = request.form['ingredients']
    
    curr_recipe = Recipe(
        name = name,
        category = Category.query.filter_by(id=category_id).first(),
        created_at = datetime.now(),
        updated_at = datetime.now(),
        needs_auth = needs_auth,
        category_id = category_id,
        instructions = instructions
    )
    db.session.add(curr_recipe)
    db.session.commit()  # need to commit to get the recipe id

    for i in range(len(pics)):
        if pics[i].filename:
            optimized_picture = optimize_picture(pics[i])
            img = Picture(
                recipe = curr_recipe,
                recipe_id = curr_recipe.id,
                image_data = optimized_picture
            )
            db.session.add(img)

    for ing in ingredients.strip().split(";"):
        if not ing:
            continue
        ing = ing.strip().split(",")
        ing_id = int(ing[0].strip())
        unit = ing[2].strip()
        if not curr_recipe.id:
            raise Exception("nope, recipe id is still null")
        ingrec = RecipeIngredient(
            recipe_id = curr_recipe.id,
            ingredient_id = ing_id,
            quantity = int(ing[1].strip()),
            unit = unit,
            recipe = curr_recipe,
            ingredient = Ingredient.query.filter_by(id=int(ing[0].strip())).first(),
        )
        db.session.add(ingrec)

        # TODO add custom error handling instead of just 404'ing out of it
        Ingredient.query.get_or_404(ing_id)
        ing_unit = IngredientUnit.query.get(ing_id)
        if not ing_unit:
            ing_unit = IngredientUnit(ingredient_id=ing_id, unit=unit)
            db.session.add(ing_unit)
        else:
            ing_unit.unit = unit

    db.session.commit()
    change_was_made()
    return Response(status=201)


@main.route("/categories", methods=['POST'])
@jwt_required()
@role_required(ROLE_EDITOR)
def create_category():
    """Create a new category.
    ---
    post:
      description: Create a new category.
      security:
        - Bearer: []
      requestBody:
        required: True
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
      responses:
        201:
          description: Category created
          content:
            application/json:
              schema:
                type: object
    """
    data = request.get_json()
    name = data.get('name')
    if not name:
        return {"error": "Name is required"}, 400
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_json()), 201


@main.route("/ingredients", methods=['POST'])
@jwt_required()
@role_required(ROLE_EDITOR)
def create_ingredient():
    """Create a new ingredient.
    ---
    post:
      description: Create a new ingredient.
      security:
        - Bearer: []
      requestBody:
        required: True
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
      responses:
        201:
          description: Ingredient created
          content:
            application/json:
              schema:
                type: object
    """
    data = request.get_json()
    name = data.get('name')
    if not name:
        return {"error": "Name is required"}, 400
    ingredient = Ingredient(name=name)
    db.session.add(ingredient)
    db.session.commit()
    return jsonify(ingredient.to_json()), 201


# API endpoints that update a record
@main.route("/categories/<int:category_id>", methods=['PUT'])
@jwt_required()
@role_required(ROLE_EDITOR)
def update_category(category_id):
    """Update a category.
    ---
    put:
      description: Update a category by its ID.
      security:
        - Bearer: []
      parameters:
        - in: path
          name: category_id
          required: True
          schema:
            type: integer
      requestBody:
        required: True
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
      responses:
        200:
          description: Category updated
          content:
            application/json:
              schema:
                type: object
    """
    data = request.get_json()
    name = data.get('name')
    if not name:
        return {"error": "Name is required"}, 400
    category = Category.query.get(category_id)
    if category is None:
        return {"error": "Category not found"}, 404
    category.name = name
    db.session.commit()
    return jsonify(category.to_json()), 200


@main.route("/ingredients/<int:ingredient_id>", methods=['PUT'])
@jwt_required()
@role_required(ROLE_EDITOR)
def update_ingredient(ingredient_id):
    """Update an ingredient.
    ---
    put:
      description: Update an ingredient by its ID.
      security:
        - Bearer: []
      parameters:
        - in: path
          name: ingredient_id
          required: True
          schema:
            type: integer
      requestBody:
        required: True
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
      responses:
        200:
          description: Ingredient updated
          content:
            application/json:
              schema:
                type: object
    """
    data = request.get_json()
    name = data.get('name')
    if not name:
        return {"error": "Name is required"}, 400
    ingredient = Ingredient.query.get(ingredient_id)
    if ingredient is None:
        return {"error": "Ingredient not found"}, 404
    ingredient.name = name
    db.session.commit()
    return jsonify(ingredient.to_json()), 200


@main.route("/recipes/<int:recipe_id>", methods=['PUT'])
@jwt_required()
@role_required(ROLE_EDITOR)
def update_recipe(recipe_id):
    """Update a recipe.
    ---
    put:
      description: Update a recipe by its ID.
      security:
        - Bearer: []
      parameters:
        - in: path
          name: recipe_id
          required: True
          schema:
            type: integer
      requestBody:
        required: True
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                name:
                  type: string
                instructions:
                  type: string
                category:
                  type: integer
                ingredients:
                  type: string
                photo:
                  type: string
      responses:
        200:
          description: Recipe updated
          content:
            application/json:
              schema:
                type: object
    """
    data = request.form
    name = data.get('name')
    instructions = data.get('instructions')
    category_id = data.get('category')
    ingredients = data.get('ingredients')
    needs_auth = data.get('needs_auth')
    old_pics = data.get('pics_to_remain')
    new_pics = request.files.getlist('pictures')

    if not name or not instructions or not category_id:
        return {"error": "Name, instructions, and category_id are required"}, 400
    recipe = Recipe.query.get_or_404(recipe_id)
    recipe.name = name
    recipe.instructions = instructions
    recipe.category_id = category_id
    recipe.category = Category.query.get(category_id)
    if needs_auth:
        recipe.needs_auth = needs_auth

    RecipeIngredient.query.filter_by(recipe_id=recipe_id).delete()

    for ing in ingredients.strip().split(";"):
        if not ing:
            continue
        ing = ing.strip().split(",")
        ing_id = int(ing[0].strip())
        unit = ing[2].strip()
        if not recipe_id:
            raise Exception("nope, recipe id is still null")
        ingrec = RecipeIngredient(
            recipe_id = recipe_id,
            ingredient_id = ing_id,
            quantity = int(ing[1].strip()),
            unit = unit,
            recipe = recipe,
            ingredient = Ingredient.query.filter_by(id=int(ing[0].strip())).first(),
        )
        db.session.add(ingrec)

        Ingredient.query.get_or_404(ing_id)
        ing_unit = IngredientUnit.query.get(ing_id)
        if not ing_unit:
            ing_unit = IngredientUnit(ingredient_id=ing_id, unit=unit)
            db.session.add(ing_unit)
        else:
            ing_unit.unit = unit

    all_pics = Picture.query.filter_by(recipe_id=recipe_id).all()
    for pic in all_pics:
        if str(pic.id) not in old_pics:
            db.session.delete(pic)

    for i in range(len(new_pics)):
        if new_pics[i].filename:
            optimized_picture = optimize_picture(new_pics[i])
            img = Picture(
                recipe = recipe,
                recipe_id = recipe_id,
                image_data = optimized_picture
            )
            db.session.add(img)

    recipe.updated_at = datetime.now()
    db.session.commit()
    change_was_made()
    return jsonify(recipe.to_json()), 200

@main.route("/recipes/<int:recipe_id>/change-auth", methods=['PUT'])
@jwt_required()
@role_required(ROLE_EDITOR)
def change_recipe_auth(recipe_id):
    """Change authentication requirement.
    ---
    put:
      description: Change the authentication requirement of a recipe by its ID.
      security:
        - Bearer: []
      parameters:
      - in: path
        name: recipe_id
        required: True
        schema:
          type: integer
        requestBody:
          required: True
          content:
            application/json:
              schema:
                type: object
                properties:
                  needs_auth:
                    type: boolean
      responses:
        200:
          description: Recipe updated
    """
    recipe = Recipe.query.get_or_404(recipe_id)
    recipe.needs_auth = request.get_json().get('needs_auth')
    db.session.commit()
    change_was_made()
    return Response(status=200)


# API endpoints that delete a record
@main.route("/categories/<int:category_id>", methods=['DELETE'])
@jwt_required()
@role_required(ROLE_EDITOR)
def delete_category(category_id):
    """Delete a category.
    ---
    delete:
      description: Delete a category by its ID.
      security:
        - Bearer: []
      parameters:
        - in: path
          name: category_id
          required: True
          schema:
            type: integer
      responses:
        204:
          description: Category deleted
    """
    category = Category.query.get(category_id)
    if category is None:
        return {"error": "Category not found"}, 404
    db.session.delete(category)
    db.session.commit()
    return '', 204


# TODO do I even need this?
@main.route("/ingredients/<int:ingredient_id>", methods=['DELETE'])
@jwt_required()
@role_required(ROLE_EDITOR)
def delete_ingredient(ingredient_id):
    """Delete an ingredient.
    ---
    delete:
      description: Delete an ingredient by its ID.
      security:
        - Bearer: []
      parameters:
        - in: path
          name: ingredient_id
          required: True
          schema:
            type: integer
      responses:
        204:
          description: Ingredient deleted
    """
    ingredient = Ingredient.query.get(ingredient_id)
    if ingredient is None:
        return {"error": "Ingredient not found"}, 404
    db.session.delete(ingredient)
    db.session.commit()
    return '', 204


@main.route("/recipes/<int:recipe_id>", methods=['DELETE'])
@jwt_required()
@role_required(ROLE_EDITOR)
def delete_recipe(recipe_id):
    """Delete a recipe.
    ---
    delete:
      description: Delete a recipe by its ID.
      security:
        - Bearer: []
      parameters:
        - in: path
          name: recipe_id
          required: True
          schema:
            type: integer
      responses:
        204:
          description: Recipe deleted
    """
    recipe = Recipe.query.get_or_404(recipe_id)
    Picture.query.filter_by(recipe_id=recipe_id).delete()
    RecipeIngredient.query.filter_by(recipe_id=recipe_id).delete()
    db.session.delete(recipe)
    db.session.commit()
    change_was_made()
    return '', 204
