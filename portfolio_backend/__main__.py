import os
import shutil
from ast import literal_eval

import uvicorn
from langchain_openai import OpenAIEmbeddings

from portfolio_backend.gunicorn_runner import GunicornApplication
from portfolio_backend.services.embeddor.embeddings import Embedding
from portfolio_backend.settings import settings
from portfolio_backend.utils.utils import create_text_df, file_exists, read_from_csv
from portfolio_backend.vdb.configs import vdb_config
from portfolio_backend.vdb.milvus_connector import MilvusDB


def set_multiproc_dir() -> None:
    """Set multiproc_dir env variable.

    This function cleans up the multiprocess directory
    and recreates it. These actions are required by prometheus-client
    to share metrics between processes.

    After cleanup, it sets two variables.
    Uppercase and lowercase because different
    versions of the prometheus-client library
    depend on different environment variables,
    so I've decided to export all needed variables,
    to avoid undefined behaviour.
    """
    shutil.rmtree(settings.prometheus_dir, ignore_errors=True)
    os.makedirs(settings.prometheus_dir, exist_ok=True)
    os.environ["prometheus_multiproc_dir"] = str(  # noqa SIM112
        settings.prometheus_dir.expanduser().absolute(),
    )
    os.environ["PROMETHEUS_MULTIPROC_DIR"] = str(
        settings.prometheus_dir.expanduser().absolute(),
    )


def set_vector_db() -> None:
    vector_db = MilvusDB(db=vdb_config.vdb_name)
    if not vector_db.has_collection(collection_name=vdb_config.collection_name):
        vector_db.create_collection(
            collection_name=vdb_config.collection_name,
            dimension=1536,
            schema=vdb_config.schema,
            index=vdb_config.index_params,
        )
        if not file_exists(filename="portfolio_backend/static/data/embedded_text.csv"):
            # Create text_df
            text_df = create_text_df(parent_path="portfolio_backend/static/data/text_data")
            embedding_model = OpenAIEmbeddings(model=settings.embedding_model, openai_api_key=settings.openai_api_key)
            text_df[vdb_config.vector_column] = text_df.apply(
                lambda x: Embedding(text=x["text"], embedding_model=embedding_model).text_embedding,
                axis=1,
            )

            text_df.to_csv("portfolio_backend/static/data/embedded_text.csv", index=False)
        else:
            # csv file exists
            print("csv file exists")
            text_df = read_from_csv(filename="portfolio_backend/static/data/embedded_text.csv")
        text_df[vdb_config.vector_column] = text_df[vdb_config.vector_column].apply(literal_eval)
        vector_db.insert_data(collection_name=vdb_config.collection_name, data=text_df.to_dict("records"))
    else:
        print("collection exists!")


def main() -> None:
    """Entrypoint of the application."""
    set_multiproc_dir()
    set_vector_db()
    if settings.reload:
        uvicorn.run(
            "portfolio_backend.web.application:get_app",
            workers=settings.workers_count,
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
            log_level=settings.log_level.value.lower(),
            factory=True,
        )
    else:
        # We choose gunicorn only if reload option is not used, because reload feature doesn't work with Uvicorn
        # workers.
        GunicornApplication(
            "portfolio_backend.web.application:get_app",
            host=settings.host,
            port=settings.port,
            workers=settings.workers_count,
            factory=True,
            accesslog="-",
            loglevel=settings.log_level.value.lower(),
            access_log_format='%r "-" %s "-" %Tf',  # noqa: WPS323
        ).run()


if __name__ == "__main__":
    main()
