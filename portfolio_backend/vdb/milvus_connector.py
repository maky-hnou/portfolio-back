from typing import Any

from pymilvus import MilvusClient


class Milvus:
    def __init__(self, db_name: str):
        self.client = MilvusClient(db_name=db_name)

    def create_collection(self, collection_name: str, dimension: int) -> None:
        self.client.create_collection(collection_name=collection_name, dimension=dimension)

    def insert_data(self, collection_name: str, data: list[Any]) -> None:
        self.client.insert(collection_name=collection_name, data=data)

    def search(  # noqa: PLR0913
        self,
        collection_name: str,
        search_data: list[float],
        limit: int,
        output_fields: list[str],
        query_filter: str | None = None,
    ) -> list[list[dict[Any, Any]]]:
        return self.client.search(
            collection_name=collection_name,
            data=search_data,
            filter=query_filter,
            limit=limit,
            output_fields=output_fields,
        )

    def query(
        self, collection_name: str, output_fields: list[str], query_filter: str | None = None
    ) -> list[dict[Any, Any]]:
        return self.client.query(
            collection_name=collection_name,
            filter=query_filter,
            output_fields=output_fields,
        )

    def delete_rows(self, collection_name: str) -> None:
        self.client.delete(collection_name=collection_name)

    def close_connection(self) -> None:
        self.client.close()

    def delete_collection(self, collection_name: str) -> None:
        self.client.drop_collection(collection_name=collection_name)

    def list_collections(self) -> list[Any]:
        return self.client.list_collections()

    def has_collection(self, collection_name: str) -> bool:
        return self.client.has_collection(collection_name=collection_name)
