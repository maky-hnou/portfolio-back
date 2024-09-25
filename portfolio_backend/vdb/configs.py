"""Module containing the VDBConfig class for configuring the vector database.

This module defines the VDBConfig class, which encapsulates the configuration
parameters for a vector database, including schema definitions, index
parameters, and other relevant settings.

Classes:
    VDBConfig: A class that provides configuration settings for the vector
    database, including fields, index parameters, and search parameters.

Dependencies:
    - CollectionSchema: Class from pymilvus to define the schema of the
    vector collection.
    - DataType: Enum from pymilvus representing data types for collection fields.
    - FieldSchema: Class from pymilvus to define individual fields in the
    collection schema.
    - IndexParams: Class from pymilvus to define index parameters for the
    vector database.
"""

from pymilvus import CollectionSchema, DataType, FieldSchema
from pymilvus.milvus_client import IndexParams


class VDBConfig:
    """Configuration class for the vector database."""

    def __init__(self):
        """Initialize VDBConfig with default settings."""
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
        """Get the collection schema for the vector database.

        Returns:
            CollectionSchema: The schema defining the structure of the
            vector collection.
        """
        fields = [FieldSchema(**field) for field in self.vector_db_fields]
        return CollectionSchema(fields=fields)

    @property
    def index_params(self) -> IndexParams:
        """Get the index parameters for the vector database.

        Returns:
            IndexParams: The parameters defining how the vector database
            should index the vector field.
        """
        return IndexParams(field_name=self.vector_column, **self.vector_db_index)


vdb_config = VDBConfig()
