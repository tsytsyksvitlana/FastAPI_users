# FastAPI
[![Python](https://img.shields.io/badge/-Python-%233776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0a0a)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=0a0a0a)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-%232F5D62?style=for-the-badge&logo=sqlalchemy&logoColor=white&labelColor=0a0a0a)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-%23C8102E?style=for-the-badge&logo=pydantic&logoColor=white&labelColor=0a0a0a)](https://pydantic-docs.helpmanual.io/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-%23316192?style=for-the-badge&logo=postgresql&logoColor=white&labelColor=0a0a0a)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/-Docker-%232496ED?style=for-the-badge&logo=docker&logoColor=white&labelColor=0a0a0a)](https://www.docker.com/)
[![pre-commit](https://img.shields.io/badge/-pre--commit-yellow?style=for-the-badge&logo=pre-commit&logoColor=white&labelColor=0a0a0a)](https://pre-commit.com/)
[![isort](https://img.shields.io/badge/isort-enabled-brightgreen?style=for-the-badge&logo=isort&logoColor=white&labelColor=0a0a0a)](https://pycqa.github.io/isort/)

***
## Production
### Create .env and .env.test file and fill with required data

```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=
POSTGRES_PORT=
```
### Generate an RSA private key, of size 2048
```
mkdir certs
```
```
cd certs
```
```
openssl genrsa -out jwt-private.pem 2048
```
### Extract the public key from the key pair, which can be used in a certificate

```
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```

### Create home network
```
docker network create home
```
### Run docker-compose file
```
docker-compose up -d
```
### To see interactive documentation in Swagger, visit
http://localhost:8000/
### To delete container
```
docker-compose down -v
```
***
## Development
### Finish production setup
### Pre-commit command
```
pre-commit run --all-files
```
### Migrations
```
docker exec -it fastapi-fastapi-1 /bin/sh
```
```
cd /code/web_app
```
```
alembic revision --autogenerate -m "message"
```
```
exit
```
### Testing
```
docker exec -it fastapi-fastapi-1 pytest
```
### CLI
#### Create database
```
docker exec -it fastapi-fastapi-1 python -m web_app.db.cli create
```
#### Drop database
```
docker exec -it fastapi-fastapi-1 python -m web_app.db.cli drop
```
#### Populate database with data
```
docker exec -it fastapi-fastapi-1 python -m web_app.cli populate --file tests/test_data/data.json
```
### Create user with admin role
```
docker exec -it fastapi-fastapi-1 python -m web_app.cli create-admin
```
### To run ipython
```
docker-compose up ipython
```

### Technology

- Python 3
- FastAPI
- Pydantic
- Postgres
- SQLAlchemy
- Docker
