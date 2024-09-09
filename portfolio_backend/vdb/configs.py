from pymilvus import CollectionSchema, DataType, FieldSchema
from pymilvus.milvus_client import IndexParams


class VDBConfig:
    def __init__(self) -> None:
        self.vector_column = "text_vector"
        self.vector_db_fields = [
            {"name": self.vector_column, "dtype": DataType.FLOAT_VECTOR, "dim": 1536},
            {"name": "id", "dtype": DataType.INT64, "is_primary": True, "auto_id": False},
            {"name": "text", "dtype": DataType.VARCHAR, "max_length": 10000},
            {"name": "topic", "dtype": DataType.VARCHAR, "max_length": 100},
        ]
        self.vector_db_index = {"index_type": "FLAT", "metric_type": "L2", "params": {}}
        self.topk = 5
        self.threshold = 1.7
        self.search_params = {"metric_type": "L2", "params": {}}
        self.collection_name = "portfolio_data"
        self.vdb_name = "./portfolio.db"

    @property
    def schema(self) -> CollectionSchema:
        fields = [FieldSchema(**field) for field in self.vector_db_fields]
        return CollectionSchema(fields=fields)

    @property
    def index_params(self) -> IndexParams:
        return IndexParams(field_name=self.vector_column, **self.vector_db_index)


vdb_config = VDBConfig()
