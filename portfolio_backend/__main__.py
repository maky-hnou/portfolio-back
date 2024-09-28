"""Main application entry point and setup.

This module initializes and configures the FastAPI application,
sets up the multiprocess directory for Prometheus metrics, and
manages the vector database connection using MilvusDB. It includes
functions to handle the embedding generation and data insertion
from a specified CSV file.

Dependencies:
    - os: Module for interacting with the operating system.
    - shutil: Module for file operations.
    - ast: Module for safely evaluating strings as Python literals.
    - uvicorn: ASGI server for running the FastAPI application.
    - OpenAIEmbeddings: Class for generating embeddings.
    - logger: Loguru logger for logging events.
    - GunicornApplication: Custom Gunicorn application runner.
    - Embedding: Class for handling text embeddings.
    - settings: Application configuration settings.
    - create_text_df: Function to create a DataFrame from text files.
    - file_exists: Utility function to check if a file exists.
    - read_from_csv: Function to read data from a CSV file.
    - vdb_config: Configuration for the vector database.
    - MilvusDB: Class for interacting with the Milvus vector database.
"""

import os
import shutil
from ast import literal_eval

import uvicorn
from langchain_openai import OpenAIEmbeddings
from loguru import logger

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
    logger.debug("Cleaning up and setting up multiprocess directory for Prometheus.")
    shutil.rmtree(settings.prometheus_dir, ignore_errors=True)
    os.makedirs(settings.prometheus_dir, exist_ok=True)
    logger.info(f"Multiprocess directory created at {settings.prometheus_dir}.")
    os.environ["prometheus_multiproc_dir"] = str(  # noqa SIM112
        settings.prometheus_dir.expanduser().absolute(),
    )
    os.environ["PROMETHEUS_MULTIPROC_DIR"] = str(
        settings.prometheus_dir.expanduser().absolute(),
    )
    logger.debug("Prometheus environment variables set.")


def set_vector_db() -> None:
    """Set up the vector database connection and manage data insertion.

    This function initializes the connection to the MilvusDB,
    checks for the existence of the specified collection, and
    handles the creation of embeddings from a CSV file if necessary.
    If the embedded text CSV file is missing, it generates the embeddings
    and saves them to the CSV file.

    Logs important steps in the process for tracking and debugging.
    """
    logger.debug("Setting up the vector database connection.")
    vector_db = MilvusDB(db=vdb_config.vdb_name)
    if not vector_db.has_collection(collection_name=vdb_config.collection_name):
        logger.warning(f"Vector DB has no collection {vdb_config.collection_name}. Creating new collection.")
        vector_db.create_collection(
            collection_name=vdb_config.collection_name,
            dimension=1536,
            schema=vdb_config.schema,
            index=vdb_config.index_params,
        )
        logger.info(f"Collection {vdb_config.collection_name} created successfully.")
        if not file_exists(filename="portfolio_backend/static/data/embedded_text.csv"):
            logger.warning("Embedded text CSV file not found. Generating embeddings and creating CSV.")
            text_df = create_text_df(parent_path="portfolio_backend/static/data/text_data")
            embedding_model = OpenAIEmbeddings(
                model=settings.embedding_model,
                openai_api_key=settings.openai_api_key,  # type: ignore
            )
            text_df[vdb_config.vector_column] = text_df.apply(
                lambda x: Embedding(text=x["text"], embedding_model=embedding_model).text_embedding,
                axis=1,
            )
            text_df.to_csv("portfolio_backend/static/data/embedded_text.csv", index=False)
            logger.info("CSV file for embedded text created successfully.")
        else:
            logger.info("Embedded text CSV file already exists.")
            text_df = read_from_csv(filename="portfolio_backend/static/data/embedded_text.csv")
        text_df[vdb_config.vector_column] = text_df[vdb_config.vector_column].apply(literal_eval)
        logger.debug("Inserting data into vector database.")
        vector_db.insert_data(collection_name=vdb_config.collection_name, data=text_df.to_dict("records"))
        logger.info(f"Data inserted into collection {vdb_config.collection_name}.")
    else:
        logger.info(f"Collection {vdb_config.collection_name} already exists.")


def main() -> None:
    """Entrypoint of the application.

    Initializes the application, sets up the multiprocess directory,
    configures the vector database, and runs the server using either
    Uvicorn or Gunicorn based on the settings.
    """
    logger.info("Starting the application.")
    set_multiproc_dir()
    set_vector_db()
    if settings.reload:
        logger.info(f"Running Uvicorn with reload enabled on {settings.host}:{settings.port}.")
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
        logger.info(f"Running Gunicorn with {settings.workers_count} workers on {settings.host}:{settings.port}.")
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
