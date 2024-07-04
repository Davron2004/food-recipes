import datetime

from flask import (
    Blueprint,
    jsonify,
    request,
)
from flask_jwt_extended import create_access_token, jwt_required
from flasgger import Schema, fields
from marshmallow import Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from werkzeug.security import check_password_hash
from food_recipe import db
from food_recipe.models import AdminAccount, AppActivation, role_required
from food_recipe.config import ROLE_EDITOR, ROLE_MANAGER

from food_recipe.utils import random_numeric_string


class AppActivationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AppActivation
        load_instance = True


class CreateAppActivationCodeSchema(Schema):
    activations_limit = fields.Int(required=True)
    expires_in_days = fields.Int(required=True)
    description = fields.Str(required=True)


auth = Blueprint('admin_auth', __name__)

app_activation_schema = AppActivationSchema()
app_activations_schema = AppActivationSchema(many=True)


@auth.route('/login', methods=['POST'])
def login():
    """User login.
    ---
    post:
      description: User login
      parameters:
        - in: body
          name: body
          required: True
          schema:
            type: object
            properties:
              username:
                type: string
              password:
                type: string
      responses:
        200:
          description: Login successful
          content:
            application/json:
              token: string
        401:
          description: Bad username or password
    """
    admin_login = request.json.get('username')
    admin_password = request.json.get('password')
    admin_account = AdminAccount.query.filter_by(admin_login=admin_login).first()
    if admin_account and check_password_hash(admin_account.admin_password_hash, admin_password):
        access_token = create_access_token(identity={'admin_login': admin_account.admin_login})
        return jsonify(token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401


@auth.route("/app-activations/create-code", methods=['POST'])
@jwt_required()
@role_required(ROLE_MANAGER)
def create_app_activation():
    """Create app activation code.
    ---
    post:
      description: Create activation code
      parameters:
        - in: body
          name: body
          required: True
          schema:
            $ref: '#/definitions/CreateAppActivationCode'
      security:
        - Bearer: []
      responses:
        201:
          description: Activation code created
          content:
            application/json:
              activation_code: string
    """
    schema = CreateAppActivationCodeSchema()
    try:
        data = schema.load(request.get_json())
    except Exception as e:
        return jsonify({"msg": str(e)}), 400

    activations_limit: int = data['activations_limit']
    expires_in_days: int = data['expires_in_days']
    description: str = data['description']

    activation_code = random_numeric_string(15)

    app_activation = AppActivation(
        activation_code=activation_code,
        activations_limit=activations_limit,
        expires_at=datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=expires_in_days),
        description=description,
        created_at=datetime.datetime.now(datetime.UTC),
    )
    
    try:
        db.session.add(app_activation)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": str(e)}), 500

    response = {"activation_code": activation_code}
    return jsonify(response), 201


@auth.route("/app-activations", methods=['GET'])
@jwt_required()
@role_required(ROLE_MANAGER)
def app_activations():
    """Get all app activations.
    ---
    get:
      description: Get all app activations
      security:
        - Bearer: []
      responses:
        200:
          description: List of app activations
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/definitions/AppActivation'
    """
    app_activations = AppActivation.query.all()
    return jsonify(app_activations_schema.dump(app_activations))
