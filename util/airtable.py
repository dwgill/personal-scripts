from typing import Generic, Iterable, Type, TypeVar
import datetime as dt
from pydantic import BaseModel, ConfigDict, Field
from pydantic.type_adapter import TypeAdapter
from pyairtable import Api
import util.env


class AirtableFields(BaseModel):
    name: str = Field(alias="Name")


ATFields = TypeVar("ATFields", bound=AirtableFields)


class AirtableRecord(BaseModel, Generic[ATFields]):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    created_time: dt.datetime = Field(alias="createdTime")
    fields: ATFields




class AirtableApi:
    def __init__(self):
        self.api = Api(util.env.airtable_personal_access_token())


