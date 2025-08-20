from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Scope(BaseModel):
    type: str
    id: Optional[str] = None

class Effect(BaseModel):
    type: str
    payload: Dict[str, Any]

class Window(BaseModel):
    start: str
    end: str
    rrule: Optional[str] = None

class PartySize(BaseModel):
    min: int
    max: int

class Conditions(BaseModel):
    party_size: Optional[PartySize] = None
    channel: Optional[List[str]] = None
    service: Optional[List[str]] = None
    user_tier: Optional[List[str]] = None

class Source(BaseModel):
    kind: str
    by: str
    url: Optional[str] = None

class Policy(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    restaurant_id: str
    scope: Scope
    effect: Effect
    window: Window
    conditions: Optional[Conditions] = None
    priority: int
    source: Source
    reason: str
    confidence: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[str] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
