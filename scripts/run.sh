#!/bin/bash
set -e

~/.local/bin/poetry run ~/.virtualenvs/portfolio_backend/bin/alembic upgrade head
~/.local/bin/poetry run ~/.virtualenvs/portfolio_backend/bin/python -m portfolio_backend