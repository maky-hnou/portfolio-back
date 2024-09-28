"""Module providing API routes for managing text data entities.

This module defines two FastAPI endpoints for handling text data:
one for retrieving all text data entries and another for creating a new
text data entry. The endpoints use the `TextDataDAO` for database interaction
and return serialized `TextDataDTO` objects.

Routes:
    - GET /text_data/all: Retrieve all text data entries.
    - POST /text_data: Create a new text data entry.

Dependencies:
    - APIRouter: FastAPI router class used for defining routes.
    - Depends: FastAPI dependency injection utility.
    - TextDataDAO: Data Access Object for handling text data model operations.
    - TextDataModel: Pydantic model representing the database schema for text data.
    - TextDataDTO: Pydantic model representing the data transfer object for text data.
"""

from fastapi import APIRouter
from fastapi.param_functions import Depends

from portfolio_backend.db.dao.text_data_dao import TextDataDAO
from portfolio_backend.db.models.text_data_model import TextDataModel
from portfolio_backend.web.api.text_data.schema import TextDataDTO

router = APIRouter()


@router.get("/text_data/all", response_model=list[TextDataDTO])
async def get_all_text(text_data_dao: TextDataDAO = Depends()) -> list[TextDataModel | None]:
    """Retrieve all text data entries from the database.

    Args:
        text_data_dao (TextDataDAO, optional): The data access object for interacting with
            the text data table. Defaults to FastAPI's `Depends()` to inject the DAO.

    Returns:
        list[TextDataModel | None]: A list of all text data entries in the database,
        or `None` if no entries are found.
    """
    return await text_data_dao.get_all_rows(model_class=TextDataModel)


@router.post("/text_data", response_model=TextDataDTO)
async def create_text_data(text_data: TextDataDTO, text_data_dao: TextDataDAO = Depends()) -> TextDataDTO:
    """Create a new text data entry in the database.

    Args:
        text_data (TextDataDTO): The text data to be created, containing information
            such as filename, text, source, and topic.
        text_data_dao (TextDataDAO, optional): The data access object for interacting
            with the text data table. Defaults to FastAPI's `Depends()` to inject the DAO.

    Returns:
        TextDataDTO: The newly created text data entry, validated and returned as a DTO.
    """
    text_data_model = TextDataModel(**text_data.dict())
    await text_data_dao.add_single_on_conflict_do_nothing(model_instance=text_data_model)
    return TextDataDTO.model_validate(text_data_model)
