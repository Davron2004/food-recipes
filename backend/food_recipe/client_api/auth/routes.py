import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from food_recipe import db
from food_recipe.models import AppActivation, UserAccount
from food_recipe.utils import random_alphanumeric_string


auth = Blueprint('client_auth', __name__)


@auth.route('/login', methods=['POST'])
def login():
    """User login.
    ---
    post:
      description: Authenticates a user using their installation token.
      parameters:
        - in: body
          name: body
          required: True
          schema:
            type: object
            properties:
              installation_token:
                type: string
      responses:
        200:
          description: Access token created
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
        400:
          description: Installation token is required
        401:
          description: Bad installation token
    """
    installation_token = request.json.get('installation_token')
    if not installation_token:
        return jsonify({"msg": "Installation token is required"}), 400
    user = UserAccount.query.filter(UserAccount.installation_token_hash == generate_password_hash(installation_token)).first()
    if user:
        access_token = create_access_token(identity={'installation_token_hash': user.installation_token_hash})
        return jsonify(token=access_token), 200
    return jsonify({"msg": "Bad installation token"}), 401

@auth.route("/activate-app", methods=['POST'])
def activate_app():
    """Activate app.
    ---
    post:
      description: Activate app
      parameters:
        - in: body
          name: body
          required: True
          schema:
            type: object
            properties:
              activation_code:
                type: string
      responses:
        201:
          description: Installation token created
          content:
            application/json:
              installation_token: string
        403:
          description: Activation code expired or exceeded limit
        404:
          description: Activation code not found
    """
    data = request.get_json()
    if not data or 'activation_code' not in data:
        return jsonify({"error": "Activation code is required"}), 400
    
    activation_code = data.get('activation_code')

    try:
        app_activation: AppActivation = AppActivation.query.filter_by(activation_code=activation_code).first()
        if app_activation is None:
            return {"error": "Activation code not found"}, 404
        if app_activation.expires_at.replace(tzinfo=datetime.UTC) < datetime.datetime.now(datetime.UTC):
            return {"error": "Activation code expired"}, 403
        if app_activation.activations_limit <= len(app_activation.user_accounts):
            return {"error": "Activation code exceeded limit"}, 403

        installation_token = random_alphanumeric_string(32)

        user_account = UserAccount(
            created_at=datetime.datetime.now(datetime.timezone.utc),
            installation_token_hash=generate_password_hash(installation_token),
            app_activation_id=app_activation.id,
        )

        db.session.add(user_account)
        db.session.commit()

        response = {"installation_token": installation_token}

        return jsonify(response), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500