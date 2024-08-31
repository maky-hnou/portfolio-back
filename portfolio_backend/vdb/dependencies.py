from starlette.requests import Request

from portfolio_backend.vdb.milvus_connector import MilvusDB


def get_milvus_db(request: Request) -> MilvusDB:
    return request.app.state.milvus_db
