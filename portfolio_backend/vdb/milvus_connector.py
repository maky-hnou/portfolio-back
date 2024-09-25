"""Module containing the MilvusDB class for interacting with the Milvus vector database.

This module defines the MilvusDB class, which provides methods for performing
various database operations, including creating collections, inserting data,
searching, querying, deleting collections, and managing connections.

Classes:
    MilvusDB: A class for managing interactions with a Milvus vector database.

Dependencies:
    - CollectionSchema: Class from pymilvus to define the schema of a collection.
    - MilvusClient: Class from pymilvus for interacting with the Milvus database.
"""

from typing import Any

from pymilvus import CollectionSchema, MilvusClient


class MilvusDB:
    """Class for managing interactions with a Milvus vector database."""

    def __init__(self, db: str):
        """Initialize the MilvusDB instance with the specified database.

        Args:
            db (str): The database connection string.
        """
        self.client = MilvusClient(db)

    def create_collection(
        self,
        collection_name: str,
        dimension: int,
        schema: CollectionSchema,
        index: None | dict[str, Any] = None,
    ) -> None:
        """Create a new collection in the Milvus database.

        Args:
            collection_name (str): The name of the collection to create.
            dimension (int): The dimensionality of the vectors.
            schema (CollectionSchema): The schema defining the collection structure.
            index (None | dict[str, Any], optional): Parameters for indexing the collection. Defaults to None.
        """
        self.client.create_collection(
            collection_name=collection_name,
            dimension=dimension,
            schema=schema,
            index_params=index,
            consistency_level="Strong",
        )

    def insert_data(self, collection_name: str, data: list[Any]) -> None:
        """Insert data into the specified collection.

        Args:
            collection_name (str): The name of the collection to insert data into.
            data (list[Any]): The data to be inserted.
        """
        self.client.insert(collection_name=collection_name, data=data)

    def search(  # noqa: PLR0913
        self,
        collection_name: str,
        search_data: list[list[float]],
        limit: int,
        output_fields: list[str],
        search_params: dict[str, Any],
        query_filter: str | None = None,
        threshold: float = 1.5,
    ) -> str:
        """Search for similar vectors in the specified collection.

        Args:
            collection_name (str): The name of the collection to search in.
            search_data (list[list[float]]): The vectors to search for.
            limit (int): The maximum number of results to return.
            output_fields (list[str]): The fields to include in the output.
            search_params (dict[str, Any]): Parameters for the search.
            query_filter (str | None, optional): An optional filter for the search. Defaults to None.
            threshold (float, optional): The maximum distance for results to be included. Defaults to 1.5.

        Returns:
            str: A string containing the text of the entities that match the search criteria.
        """
        query_result = self.client.search(
            collection_name=collection_name,
            data=search_data,
            filter=query_filter,
            limit=limit,
            output_fields=output_fields,
            search_params=search_params,
        )
        sorted_query_results = sorted(query_result[0], key=lambda x: x["distance"])
        result = ""
        for hit in sorted_query_results:
            if hit.get("distance", 0) < threshold:
                result += f"{hit.get('entity', {}).get('text')}\n"
        return result

    def query(
        self,
        collection_name: str,
        output_fields: list[str],
        query_filter: str | None = None,
    ) -> list[dict[Any, Any]]:
        """Query the specified collection for specified fields.

        Args:
            collection_name (str): The name of the collection to query.
            output_fields (list[str]): The fields to include in the output.
            query_filter (str | None, optional): An optional filter for the query. Defaults to None.

        Returns:
            list[dict[Any, Any]]: A list of dictionaries containing the queried data.
        """
        return self.client.query(
            collection_name=collection_name,
            filter=query_filter,
            output_fields=output_fields,
        )

    def delete_rows(self, collection_name: str) -> None:
        """Delete all rows in the specified collection.

        Args:
            collection_name (str): The name of the collection from which to delete rows.
        """
        self.client.delete(collection_name=collection_name)

    def close_connection(self) -> None:
        """Close the connection to the Milvus database."""
        self.client.close()

    def delete_collection(self, collection_name: str) -> None:
        """Delete the specified collection from the Milvus database.

        Args:
            collection_name (str): The name of the collection to delete.
        """
        self.client.drop_collection(collection_name=collection_name)

    def list_collections(self) -> list[Any]:
        """List all collections in the Milvus database.

        Returns:
            list[Any]: A list of collection names.
        """
        return self.client.list_collections()

    def has_collection(self, collection_name: str) -> bool:
        """Check if the specified collection exists in the Milvus database.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        return self.client.has_collection(collection_name=collection_name)
