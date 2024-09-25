"""Module defining metadata for SQLAlchemy models.

This module creates a `MetaData` instance that serves as a container for SQLAlchemy table definitions and
schema configurations. This metadata can be used across various SQLAlchemy models within the application.

Variables:
    meta (MetaData): An instance of SQLAlchemy's MetaData class for defining and organizing database schema.

Dependencies:
    - sqlalchemy: The SQLAlchemy ORM library used for database interaction and schema definition.
"""

import sqlalchemy as sa

meta = sa.MetaData()
