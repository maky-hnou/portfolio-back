from pymilvus import CollectionSchema, DataType, FieldSchema


class VDBConfig:
    def __init__(self) -> None:
        self.vector_column = "text_vector"
        self.vector_db_fields = [
            {"name": self.vector_column, "dtype": DataType.FLOAT_VECTOR, "dim": 1536},
            {"name": "id", "dtype": DataType.INT64, "is_primary": True, "auto_id": False},
            {"name": "text", "dtype": DataType.VARCHAR, "max_length": 10000},
            {"name": "topic", "dtype": DataType.VARCHAR, "max_length": 100},
        ]
        self.vector_db_index = {"index_type": "HNSW", "metric_type": "L2", "params": {"M": 8, "efConstruction": 64}}
        self.topk = 2
        self.threshold = 0.45
        self.search_params = {"metric_type": "L2", "params": {"ef": max(64, self.topk)}}
        self.collection_name = "portfolio_data"

    @property
    def schema(self) -> CollectionSchema:
        fields = [FieldSchema(**field) for field in self.vector_db_fields]
        return CollectionSchema(fields=fields)


vdb_config = VDBConfig()
