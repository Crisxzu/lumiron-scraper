from typing import Optional, List
from pydantic import BaseModel, Field

class PersonInput(BaseModel):
    first_name: str = Field(min_length=1, description="First name of the person")
    last_name: str = Field(min_length=1, description="Last name of the person")
    company: str = Field(min_length=1, description="Company name")

class ProfessionalExperience(BaseModel):
    position: Optional[str] = None
    company: Optional[str] = None
    period: Optional[str] = None
    description: Optional[str] = None

class PersonProfile(BaseModel):
    full_name: str
    current_position: Optional[str] = None
    company: Optional[str] = None
    professional_experience: List[ProfessionalExperience] = []
    skills: List[str] = []
    publications: List[str] = []
    public_contact: Optional[dict] = None
    linkedin_url: Optional[str] = None
    summary: Optional[str] = None
    sources: List[str] = []
