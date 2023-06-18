# itmo-SEM-back
Software Engineering Metodology course project backend. . Software Engineering Course ITMO magistracy 1-year


## Setup required tools

1. Install `python 3.8.*` (https://www.python.org/downloads/release/python-3810/)
1. Install `docker >= 20.10` (https://www.docker.com/)
1. Install `docker-compose >= 2.15` (https://www.docker.com/)
1. Install `poetry`

```shell
# Windows
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# *NIX
curl -sSL https://install.python-poetry.org | python3 -
```

More info at https://python-poetry.org/docs/

If you got an error with python version try to add to `PYTHONPATH` python root dir (for
example `C:\Program Files\Python38`)
```shell
PYTHONPATH="C:\Program Files\Python38"
```

If you got an error with script execiton in **PowerShell**
```shell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
```

## Setup dev env
1. Check installation `poetry --version`
1. Run in project root dir `poetry shell`
1. In opened shell install dependencies with `poetry install`
1. Set up pre-commit hooks `pre-commit install`
1. Create copy of `.env.example` to `.env` in the project root
1. Configure variables (detailed description is in section [env info](#environment))
1. Run with docker-compose (backend will be unhealthy at first run)
```shell
docker-compose -f deploy/local.docker-compose.yml --env-file .env up --build -d
```
1. Open keycloak admin panel at `localhost:8085` and enable old theme (because it is more useful)
![Enable old theme](./docs/old-theme-1.png)
1. Reload page `http://localhost:8085/admin`
1. **regenerate secret** for `service-client` and copy
![Regenerate secret](./docs/regenerate-secret.png)
1. Write secret to `.env`
```
KEYCLOAK_CLIENT_SECRET_SERIVCE=<generated-secret>
```
1. Run with docker-compose again
```shell
docker-compose -f deploy/local.docker-compose.yml --env-file .env up --build -d
```


## Environment

```shell
ENVIRONMENT=DEV         # Required | DEV | PRODUCTION
SECRET_KEY=secret       # Required | secret key that will be used in jwt generation
BACKEND_CORS_ORIGINS=http://localhost:8080,http://localhost:8081  # Optional | allowed origins, separated by comma
FORCE_HTTPS=False       # True | False

POSTGRES_USER=postgres      # Required | Postgres user. It used only with docker to set up postgres and generate DATABASE_URI
POSTGRES_PASSWORD=postgres  # Required | Postgres password. It used only with docker to set up postgres and generate DATABASE_URI
POSTGRES_DB=sem_data             # Required | Postgres db name. It used only with docker to set up postgres and generate DATABASE_URI
DATABASE_URI=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/sem_data  # Required

KEYCLOAK_ADMIN=admin                # Optional
KEYCLOAK_ADMIN_PASSWORD=admin       # Optional
KEYCLOAK_URL=http://localhost:8085  # Required for console run, Optional with docker
KEYCLOAK_REALM=MPI
KEYCLOAK_CLIENT_ID_FRONT=frontend-client
KEYCLOAK_CLIENT_ID_SERIVCE=service-client
KEYCLOAK_CLIENT_SECRET_SERIVCE=client_secret
```

### Requirements export

```shell
poetry export -f requirements.txt -o requirements.txt --without-hashes
```


### Upgrade to the latest migration revision

```shell
poetry run alembic upgrade head
```


### Create migrations revision
WARNING: It use `DATABASE_URI` var from env, so setup in to `.env` when you start migration


```
# for default config
DATABASE_URI=postgresql+asyncpg://postgres:postgres@127.0.0.1:5438/sem_data
```


```shell
poetry run alembic revision --autogenerate -m "<message>"
```
