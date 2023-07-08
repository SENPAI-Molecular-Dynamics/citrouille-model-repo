# Repository for Citrouille model files

Allows users to push and pull Citrouille model files over HTTP.

# Architecture

Pushing models require authentication with a token. Tokens are stored in a MySQL table. Models are then indexed in the database with their author/name/version metadata, and stored as objects with MinIO.

Pulling models require no authentication.

# Setup (for development purposes)

The service requires a running MinIO object-storage instance, and a MySQL-compatible instance for token authentication and object tracking.

Create and initialize the database in MySQL:

```
CREATE DATABASE IF NOT EXISTS citrouille;

USE citrouille;

CREATE TABLE IF NOT EXISTS tokens (
  id INT AUTO_INCREMENT PRIMARY KEY,
  token VARCHAR(48) NOT NULL
);

CREATE TABLE IF NOT EXISTS objects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  author VARCHAR(100) NOT NULL,
  name VARCHAR(100) NOT NULL,
  version VARCHAR(10) NOT NULL,
  description TEXT NOT NULL,
  filename TEXT NOT NULL
);
```

Generate an authentication token:

```
$ python3 -c 'import secrets; print(secrets.token_urlsafe(48));
nycQkxrCzrvXEJxUdMtKernljbnLZ3yMD01ARynaIfvhRdZADvQQGOnaKmbbrzO8
```

Store the token in the corresponding MySQL table:

```
USE citrouille;
INSERT INTO tokens (token) VALUES ('nycQkxrCzrvXEJxUdMtKernljbnLZ3yMD01ARynaIfvhRdZADvQQGOnaKmbbrzO8');
```

Configure the variables in `config.py` for MySQL:

```
MYSQL_USERNAME = 'db_user'
MYSQL_PASSWORD = 'db_pass'
MYSQL_HOSTNAME = 'db_address'
```

Configure the variables in `config.py` for MinIO:

```
MINIO_ENDPOINT = 'minio_endpoint'
MINIO_ACCESS_KEY = 'minio_access_key'
MINIO_SECRET_KEY = 'minio_secret_key'
MINIO_BUCKET = 'citrouille-bucket'
```

Create a Python 3.11 venv:

`$ python3.11 -m venv .venv`

Activate it:

`$ source .venv/bin/activate`

Install the Python dependencies:

`$ pip install -r requirements.txt`

Serve with Gunicorn:

`$ gunicorn --bind 0.0.0.0:5000 app:app`

The service should now be up and running.

# Setup (for production)

We recommend using `docker compose` for orchestration of the entire service stack.

Generate an authentication token:

'$ python3 -c 'import secrets; print(secrets.token_urlsafe(48));'

Create a database initalization file for MariaDB, making sure to replace the token value with the token you just generated:

```
$ cat init.sql
CREATE DATABASE IF NOT EXISTS citrouille-db;

USE citrouille-db;

CREATE TABLE IF NOT EXISTS tokens (
  id INT AUTO_INCREMENT PRIMARY KEY,
  token VARCHAR(48) NOT NULL
);

CREATE TABLE IF NOT EXISTS objects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  author VARCHAR(100) NOT NULL,
  name VARCHAR(100) NOT NULL,
  version VARCHAR(10) NOT NULL,
  description TEXT NOT NULL,
  filename TEXT NOT NULL
);

INSERT INTO tokens (token) VALUES ('replace-this-with-your-token');
```

Here is an example file deploying the service with MariaDB and MinIO:

```
$ cat docker-compose.yml
version: '3'
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - 5000:5000
    depends_on:
      - minio
      - mariadb
    environment:
      - MYSQL_HOST=mariadb
      - MINIO_ENDPOINT=minio:9000
      - MINIO_ACCESS_KEY=minio_access_key
      - MINIO_SECRET_KEY=minio_secret_key
      - MINIO_BUCKET=citrouille-bucket
    command: gunicorn --bind 0.0.0.0:5000 app:app

  minio:
    image: minio/minio
    ports:
      - 9000:9000
    environment:
      - MINIO_ROOT_USER=minio_access_key
      - MINIO_ROOT_PASSWORD=minio_secret_key
    volumes:
      - minio-data:/data
    command: server /data

  mariadb:
    image: mariadb
    ports:
      - 3306:3306
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=citrouille-db
      - MYSQL_USER=db_user
      - MYSQL_PASSWORD=db_pass
    volumes:
      - mariadb-data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  minio-data:
  mariadb-data:

```

Deploy with `docker compose`:

`$ docker compose up -d`

The service is now reachable over HTTP. You should hide it behind a reverse-proxy to prevent token leak.