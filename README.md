# portfolio_backend

This project was generated using fastapi_template.

## Uv

This project uses uv. It's a modern dependency management tool.

To run the project use this set of commands:

```bash
uv uv pip install -r pyproject.toml
uv run alembic upgrade head
uv run python -m portfolio_backend
```

This will start the server on the configured host.

You can find swagger documentation at `/api/v1/docs`.

## Project structure

```bash
$ tree "portfolio_backend"
portfolio_backend
├── conftest.py  # Fixtures for all tests.
├── db  # module contains db configurations
│   ├── dao  # Data Access Objects. Contains different classes to interact with database.
│   └── models  # Package contains different models for ORMs.
├── __main__.py  # Startup script. Starts uvicorn.
├── services  # Package for different external services such as rabbit or redis etc.
├── settings.py  # Main configuration settings for project.
├── static  # Static content.
├── tests  # Tests for project.
└── web  # Package contains web server. Handlers, startup config.
    ├── api  # Package with all handlers.
    │   └── router.py  # Main router.
    ├── application.py  # FastAPI application configuration.
    └── lifetime.py  # Contains actions to perform on startup and shutdown.
```

## Configuration

This application can be configured with environment variables.

You can create `.env` file in the root directory and place all
environment variables here.

All environment variables should start with "PORTFOLIO_BACKEND_" prefix.

For example if you see in your "portfolio_backend/settings.py" a variable named like
`random_parameter`, you should provide the "PORTFOLIO_BACKEND_RANDOM_PARAMETER"
variable to configure the value. This behaviour can be changed by overriding `env_prefix` property
in `portfolio_backend.settings.Settings.Config`.

An example of .env file:
```bash
PORTFOLIO_BACKEND_HOST=""
PORTFOLIO_BACKEND_PORT=""
PORTFOLIO_BACKEND_DB_HOST=""
PORTFOLIO_BACKEND_DB_PORT=""
PORTFOLIO_BACKEND_DB_USER=""
PORTFOLIO_BACKEND_DB_PASS=""
PORTFOLIO_BACKEND_DB_BASE=""
PORTFOLIO_BACKEND_OPENAI_API_KEY=""
```

You can read more about BaseSettings class here: https://pydantic-docs.helpmanual.io/usage/settings/

## Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default it runs:
* black (formats your code);
* mypy (validates types);
* isort (sorts imports in all files);
* flake8 (spots possible bugs);


You can read more about pre-commit here: https://pre-commit.com/

## Migrations

If you want to migrate your database, you should run following commands:
```bash
# To run all migrations until the migration with revision_id.
alembic upgrade "<revision_id>"

# To perform all pending migrations.
alembic upgrade "head"
```

### Reverting migrations

If you want to revert migrations, you should run:
```bash
# revert all migrations up to: revision_id.
alembic downgrade <revision_id>

# Revert everything.
 alembic downgrade base
```

### Migration generation

To generate migrations you should run:
```bash
# For automatic change detection.
alembic revision --autogenerate

# For empty file generation.
alembic revision
```
