# schemas/empresa.py
from pydantic import BaseModel
from typing import Optional

class Name(BaseModel):
    name: str
    organization_id: int

class Color(BaseModel):
    color: str

class Description(BaseModel):
    description: str

class Title(BaseModel):
    title: str

class Logo(BaseModel):
    image: str

class UpdateOrganization(BaseModel):
    name: Optional[Name] = None
    color: Optional[Color] = None
    description: Optional[Description] = None
    title: Optional[Title] = None
    logo: Optional[Logo] = None