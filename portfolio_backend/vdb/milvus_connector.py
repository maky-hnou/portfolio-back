from typing import Any

from pymilvus import CollectionSchema, MilvusClient


class MilvusDB:
    def __init__(self, db: str):
        self.client = MilvusClient(db)

    def create_collection(
        self,
        collection_name: str,
        dimension: int,
        schema: CollectionSchema,
        index: None | dict[str, Any] = None,
    ) -> None:
        self.client.create_collection(
            collection_name=collection_name,
            dimension=dimension,
            schema=schema,
            index_params=index,
            consistency_level="Strong",
        )

    def insert_data(self, collection_name: str, data: list[Any]) -> None:
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
