#!/bin/bash
set -e

poetry run ~/.virtualenvs/portfolio_backend/bin/alembic upgrade head
poetry run ~/.virtualenvs/portfolio_backend/bin/python -m portfolio_backend