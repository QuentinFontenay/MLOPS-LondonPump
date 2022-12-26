from datetime import datetime
from pydantic import BaseModel, Field

class CreatePredictionSchema(BaseModel):
    deployedFromLocation: str
    appliance: str
    propertyCategory: str
    addressQualifier: str
    incidentType: str
    distance: str
    totalOfPumpInLondon_Out: str
    station_Code_of_ressource: str
    incidentStationGround_Code: str
    pumpAvailable: str
    month: int
    temp: float
    precip: float
    cloudcover: float
    visibility: str
    workingday: int
    school_holidays: int
    congestion_rate: float

class HistorisationSchema(BaseModel):
    created_at: datetime = Field(default=str(datetime.now())),
    prediction: int = Field(...),
