from fastapi import APIRouter
from fastapi.param_functions import Depends

from portfolio_backend.db.dao.text_data_dao import TextDataDAO
from portfolio_backend.db.models.text_data_model import TextDataModel
from portfolio_backend.web.api.text_data.schema import TextDataDTO

router = APIRouter()


@router.get("/text_data/all", response_model=list[TextDataDTO])
async def get_all_text(text_data_dao: TextDataDAO = Depends()) -> list[TextDataModel | None]:
    return await text_data_dao.get_all_rows(model_class=TextDataModel)


@router.post("/text_data/", response_model=TextDataDTO)
async def create_text_data(text_data: TextDataDTO, text_data_dao: TextDataDAO = Depends()) -> TextDataModel:
    text_data_model = TextDataModel(**text_data.dict())
    await text_data_dao.add_single_on_conflict_do_nothing(model_instance=text_data_model)
    return text_data_model
