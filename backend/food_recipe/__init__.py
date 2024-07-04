import os
import datetime
from apispec import APISpec
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flasgger import APISpec, Swagger
from flasgger.utils import apispec_to_template
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

last_recipe_change_time = {"key": datetime.datetime.now()}

def change_was_made():
    last_recipe_change_time["key"] = datetime.datetime.now()

def show_last_change():
    return jsonify(last_recipe_change_time["key"].isoformat())

app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})
app.config.from_object("food_recipe.config.Config")
CORS(app)
app.url_map.strict_slashes = False
app.secret_key = 'eqvQS%iV%Z2FN@nnNzdy9E&E4XrsiV'
db = SQLAlchemy(app)

app.config['JWT_SECRET_KEY'] = '9JkK@#ybt2STqa3Y^TaiXnAYETYTum'
jwt = JWTManager(app)


from food_recipe.admin_api.auth.routes import auth as admin_auth_blueprint
from food_recipe.admin_api.main.routes import main as admin_main_blueprint
from food_recipe.admin_api.static.routes import static as admin_static_blueprint
from food_recipe.client_api.auth.routes import auth as client_auth_blueprint
from food_recipe.client_api.main.routes import main as client_main_blueprint


app.register_blueprint(admin_auth_blueprint, url_prefix='/admin/auth')
app.register_blueprint(admin_main_blueprint, url_prefix='/admin')
app.register_blueprint(admin_static_blueprint)
app.register_blueprint(client_auth_blueprint, url_prefix='/auth')
app.register_blueprint(client_main_blueprint)

spec = APISpec(
    title='Food Recipes API',
    version='1.0.0',
    openapi_version='2.0',
    plugins=[
        FlaskPlugin(),
        MarshmallowPlugin(),
    ],
)

import food_recipe.admin_api.auth.routes as admin_auth_routes
import food_recipe.client_api.auth.routes as client_auth_routes
import food_recipe.client_api.main.routes as client_main_routes
import food_recipe.admin_api.main.routes as admin_main_routes

template = apispec_to_template(
    app=app,
    spec=spec,
    definitions=[
        admin_auth_routes.CreateAppActivationCodeSchema,
    ],
    paths=[
        admin_auth_routes.create_app_activation,
        admin_auth_routes.app_activations,
        admin_auth_routes.login,

        client_auth_routes.login,
        client_auth_routes.activate_app,

        admin_main_routes.get_categories,
        admin_main_routes.get_ingredients,
        admin_main_routes.get_recipes,
        admin_main_routes.get_category,
        admin_main_routes.get_ingredient,
        admin_main_routes.return_recipe,
        admin_main_routes.return_pic,
        admin_main_routes.create_recipe,
        admin_main_routes.create_category,
        admin_main_routes.create_ingredient,
        admin_main_routes.update_category,
        admin_main_routes.update_ingredient,
        admin_main_routes.update_recipe,
        admin_main_routes.delete_category,
        admin_main_routes.delete_ingredient,
        admin_main_routes.delete_recipe,

        client_main_routes.return_last_change,
        client_main_routes.get_recipes,
        client_main_routes.return_pic,
    ]
)

template['securityDefinitions'] = {
    "Bearer": {
        "type": "apiKey",
        "name": "Authorization",
        "in": "header",
        "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
    }
}

app.config['SWAGGER'] = {'uiversion': 3}
swag = Swagger(app, template=template)
