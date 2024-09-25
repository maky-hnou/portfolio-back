"""Module containing the get_milvus_db function for accessing the Milvus database.

This module provides a utility function to retrieve an instance of the MilvusDB
class from the FastAPI application state, allowing for easy access to the
vector database within request handlers.

Functions:
    get_milvus_db: Retrieve the MilvusDB instance from the FastAPI application state.

Dependencies:
    - Request: Class from Starlette representing an incoming HTTP request.
    - MilvusDB: Custom class for interacting with the Milvus vector database.
"""

from starlette.requests import Request

from portfolio_backend.vdb.milvus_connector import MilvusDB


def get_milvus_db(request: Request) -> MilvusDB:
    """Retrieve the MilvusDB instance from the FastAPI application state.

    Args:
        request (Request): The incoming HTTP request containing the application
        state.

    Returns:
        MilvusDB: The instance of MilvusDB from the application state, allowing
        access to the vector database.
    """
    return request.app.state.milvus_db
