from typing import Optional, List
from pydantic import BaseModel, Field

class PersonInput(BaseModel):
    first_name: str = Field(min_length=1, description="First name of the person")
    last_name: str = Field(min_length=1, description="Last name of the person")
    company: str = Field(min_length=1, description="Company name")

class RiskAssessment(BaseModel):
    risk_level: str = Field(description="Faible, Moyen, or Élevé")
    risk_factors: List[str] = []
    trust_indicators: List[str] = []
    credibility_score: int = Field(ge=0, le=100, description="Score from 0-100")

class CompanyLed(BaseModel):
    name: str
    role: Optional[str] = None
    siren: Optional[str] = None
    status: Optional[str] = None
    financial_health: Optional[str] = None
    since: Optional[str] = None

class BusinessEcosystem(BaseModel):
    companies_led: List[CompanyLed] = []
    power_network: Optional[str] = None
    business_longevity: Optional[str] = None
    real_estate_assets: Optional[str] = None
    politically_exposed: Optional[bool] = False

class ProfessionalExperience(BaseModel):
    position: Optional[str] = None
    company: Optional[str] = None
    period: Optional[str] = None
    description: Optional[str] = None
    verified: Optional[bool] = None

class PsychologyAndApproach(BaseModel):
    personality_traits: List[str] = []
    interests_and_hobbies: List[str] = []
    communication_style: Optional[str] = None
    ice_breakers: List[str] = []

class RedFlag(BaseModel):
    type: str
    description: str
    severity: str = Field(description="Critique, Modéré, or Mineur")
    source: Optional[str] = None

class Publication(BaseModel):
    type: str = Field(description="Article, Interview, Podcast, Conférence, or Tribune")
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    date: Optional[str] = None

class CoherenceAnalysis(BaseModel):
    data_consistency: Optional[str] = None
    timeline_verification: Optional[str] = None
    cross_source_validation: Optional[str] = None

class PersonProfile(BaseModel):
    full_name: str
    current_position: Optional[str] = None
    company: Optional[str] = None
    risk_assessment: Optional[RiskAssessment] = None
    business_ecosystem: Optional[BusinessEcosystem] = None
    professional_experience: List[ProfessionalExperience] = []
    psychology_and_approach: Optional[PsychologyAndApproach] = None
    red_flags: List[RedFlag] = []
    coherence_analysis: Optional[CoherenceAnalysis] = None
    skills: List[str] = []
    publications_and_visibility: List[Publication] = []
    public_contact: Optional[dict] = None
    summary: Optional[str] = None
    linkedin_url: Optional[str] = None
    sources: List[str] = []
