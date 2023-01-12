from datetime import datetime
from typing import Union
from fastapi import Query
from pydantic import BaseModel, Field

class CreatePredictionSchema(BaseModel):
    DeployedFromLocation: str = Field(default="Home Station")
    Appliance: str = Field(default="Pump Ladder")
    PropertyCategory: str = Field(default="Other Residential")
    AddressQualifier: str = Field(default="Correct incident location")
    IncidentType: str = Field(default="Fire")
    Distance: float = Field(default=0.608)
    TotalOfPumpInLondon_Out: int = Field(default=3)
    Station_Code_of_ressource: str = Field(default="G30")
    IncidentStationGround_Code: str = Field(default="G30")
    PumpAvailable: str = Field(default="2")
    month: int = Field(default=1)
    temp: float = Field(default=2.6)
    precip: float = Field(default=0.0)
    cloudcover: float = Field(default=0.0)
    visibility: float = Field(default=28.3)
    conditions: str = Field(default="Clear")
    workingday: int = Field(default=1)
    school_holidays: int = Field(default=0)
    congestion_rate: float = Field(default=0.04)

class HistorisationSchema(BaseModel):
    created_at: Union[datetime, None] = Query(default=None)
    username: Union[str, None] = Query(default=None, max_length=50)
