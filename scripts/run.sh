#!/bin/bash
set -e

~/.local/bin/uv run ~/projects/portfolio_backend/venv/bin/alembic upgrade head
~/.local/bin/uv run ~/projects/portfolio_backend/venv/bin/python -m portfolio_backend
