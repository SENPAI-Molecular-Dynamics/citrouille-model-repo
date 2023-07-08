from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from minio import Minio
from minio.error import InvalidResponseError
import uuid
import yaml
import io
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.MYSQL_URI
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Configure the MiniIO client
minio_client = Minio(
    endpoint=config.MINIO_ENDPOINT,
    access_key=config.MINIO_ACCESS_KEY,
    secret_key=config.MINIO_SECRET_KEY,
    secure=False
)


# Define the Model class to represent the models in the database
class Model(db.Model):
    __tablename__ = config.MYSQL_TABLE_OBJECTS
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(10), nullable=False)
    description = db.Column(db.Text, nullable=False)
    filename = db.Column(db.Text, nullable=False)


# Define the Token class to represent the authentication tokens in the database
class Token(db.Model):
    __tablename__ = config.MYSQL_TABLE_TOKENS
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(48), nullable=False)


# Add a route for pushing models
@app.route('/models', methods=['POST'])
def push_model():
    # Retrieve the authentication token from the request headers
    auth_token = request.headers.get('Authorization')

    # Check if the token is provided
    if not auth_token:
        return jsonify({'message': 'Authentication token required.'}), 401

    # Check if the token is valid
    if not Token.query.filter_by(token=auth_token).first():
        return jsonify({'message': 'Invalid authentication token.'}), 401

    # Retrieve the model data from the request
    model_data = request.get_json()

    # Extract the relevant fields from the model data
    author = model_data.get('author')
    name = model_data.get('name')
    version = model_data.get('version')
    description = model_data.get('description')

    # Check if any of the fields are missing
    if not version or not author or not name or not description:
        return jsonify({'message': 'Missing required fields in the model data.'}), 400

    # Generate a unique filename for the model file
    filename = f'{uuid.uuid4()}.yaml'

    # Convert the model data to YAML format
    model_yaml = yaml.dump(model_data)

    try:
        # Save the model file to MinIO
        minio_client.put_object(config.MINIO_BUCKET_NAME, filename, io.BytesIO(model_yaml.encode()), len(model_yaml))

        # Create a new Model instance and save it to the database
        new_model = Model(version=version, author=author, name=name, description=description, filename=filename)
        db.session.add(new_model)
        db.session.commit()

        return jsonify({'message': 'Model successfully pushed.'}), 201
    except InvalidResponseError:
        return jsonify({'message': 'Unable to access MinIO. Invalid response.'}), 500


@app.route('/models/<author>/<name>/<version>', methods=['GET'])
def pull_model(author, name, version):
    # Retrieve the requested model from the database
    model = Model.query.filter_by(author=author, name=name, version=version).first()

    # Check if the model exists
    if not model:
        return jsonify({'message': 'Model not found.'}), 404

    try:
        # Retrieve the model file from MinIO
        data = minio_client.get_object(config.MINIO_BUCKET_NAME, model.filename)
        model_yaml = data.data.decode()

        return Response(model_yaml, mimetype='application/x-yaml')
    except InvalidResponseError:
        return jsonify({'message': 'Unable to access MinIO. Invalid response.'}), 500


@app.route('/models/<author>/<name>/latest', methods=['GET'])
def pull_latest_model(author, name):
    # Retrieve the latest version of the requested model from the database
    latest_model = Model.query.filter_by(author=author, name=name).order_by(Model.version.desc()).first()

    # Check if the latest model exists
    if not latest_model:
        return jsonify({'message': 'Model not found.'}), 404

    try:
        # Retrieve the model file from MinIO
        data = minio_client.get_object(config.MINIO_BUCKET_NAME, latest_model.filename)
        model_yaml = data.data.decode()

        return Response(model_yaml, mimetype='application/x-yaml')
    except InvalidResponseError:
        return jsonify({'message': 'Unable to access MinIO. Invalid response.'}), 500


if __name__ == '__main__':
    app.run()
