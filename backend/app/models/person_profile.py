from typing import Optional, List
from pydantic import BaseModel, Field

class PersonInput(BaseModel):
    first_name: str = Field(min_length=1, description="First name of the person")
    last_name: str = Field(min_length=1, description="Last name of the person")
    company: str = Field(min_length=1, description="Company name")

# ========== RISK ASSESSMENT ==========
class RiskAssessment(BaseModel):
    risk_level: str = Field(description="Faible, Moyen, or Élevé")
    risk_factors: List[str] = []
    trust_indicators: List[str] = []
    credibility_score: int = Field(ge=0, le=100, description="Score from 0-100")
    overall_assessment: Optional[str] = None

# ========== BUSINESS ECOSYSTEM ==========
class CompanyLed(BaseModel):
    name: str
    role: Optional[str] = None
    siren: Optional[str] = None
    status: Optional[str] = None
    financial_health: Optional[str] = None
    since: Optional[str] = None
    revenue: Optional[str] = None
    employees: Optional[str] = None

class BusinessEcosystem(BaseModel):
    companies_led: List[CompanyLed] = []
    power_network: Optional[str] = None
    business_longevity: Optional[str] = None
    real_estate_assets: Optional[str] = None
    politically_exposed: Optional[bool] = False
    estimated_wealth: Optional[str] = None

# ========== FINANCIAL INTELLIGENCE (NEW) ==========
class FinancialIntelligence(BaseModel):
    revenue_evolution: Optional[str] = None
    revenue_evolution_source: Optional[str] = None
    financial_stability: Optional[str] = None
    financial_stability_source: Optional[str] = None
    investment_capacity: Optional[str] = None
    capital_structure: Optional[str] = None
    capital_structure_source: Optional[str] = None
    financial_red_flags: List[str] = []

# ========== PROFESSIONAL EXPERIENCE ==========
class ProfessionalExperience(BaseModel):
    position: Optional[str] = None
    company: Optional[str] = None
    period: Optional[str] = None
    description: Optional[str] = None
    verified: Optional[bool] = None
    achievements: Optional[str] = None

# ========== CAREER TIMELINE (NEW) ==========
class TimelineEvent(BaseModel):
    year: int
    event: str
    type: str = Field(description="Création entreprise, Nomination, Levée de fonds, etc.")
    impact: Optional[str] = None

# ========== MEDIA PRESENCE (NEW) ==========
class PressMention(BaseModel):
    title: str
    source: str
    date: Optional[str] = None
    sentiment: Optional[str] = Field(description="Positif, Neutre, or Négatif")
    summary: Optional[str] = None
    url: Optional[str] = None

class MediaPresence(BaseModel):
    press_mentions: List[PressMention] = []
    social_media_activity: Optional[str] = None
    public_statements: List[str] = []
    thought_leadership: Optional[str] = None
    reputation_score: Optional[int] = Field(ge=0, le=100, default=None)
    media_sentiment_analysis: Optional[str] = None

# ========== COMPETITIVE INTELLIGENCE (NEW) ==========
class CompetitiveIntelligence(BaseModel):
    market_position: Optional[str] = None
    competitors_mentioned: List[str] = []
    industry_trends: Optional[str] = None
    strategic_moves: List[str] = []
    innovation_signals: List[str] = []

# ========== OFFICIAL RECORDS (NEW) ==========
class OfficialRecords(BaseModel):
    legal_mentions: List[str] = []
    trade_registry_status: Optional[str] = None
    bodacc_publications: List[str] = []
    administrative_issues: Optional[List[str]] = None
    compliance_status: Optional[str] = Field(description="Conforme, Attention, or Problématique")

# ========== PSYCHOLOGY & APPROACH ==========
class PsychologyAndApproach(BaseModel):
    personality_traits: List[str] = []
    interests_and_hobbies: List[str] = []
    communication_style: Optional[str] = None
    values_and_beliefs: Optional[str] = None
    decision_making_style: Optional[str] = None
    ice_breakers: List[str] = []

# ========== RED FLAGS ==========
class RedFlag(BaseModel):
    type: str
    description: str
    severity: str = Field(description="Critique, Modéré, or Mineur")
    source: Optional[str] = None
    recommendation: Optional[str] = None

# ========== COHERENCE ANALYSIS ==========
class CoherenceAnalysis(BaseModel):
    data_consistency: Optional[str] = None
    timeline_verification: Optional[str] = None
    cross_source_validation: Optional[str] = None
    discrepancies: Optional[List[str]] = None
    reliability_score: Optional[int] = Field(ge=0, le=100, default=None)
    reliability_justification: Optional[str] = Field(
        description="Justification détaillée du score (3-6 lignes) basée sur cohérence, sources, vérifiabilité, complétude"
    )

# ========== NETWORK & INFLUENCE (NEW) ==========
class NetworkAndInfluence(BaseModel):
    key_connections: List[str] = []
    board_positions: List[str] = []
    associations_memberships: List[str] = []
    influence_score: Optional[int] = Field(ge=0, le=100, default=None)
    influence_analysis: Optional[str] = None

# ========== PUBLICATIONS ==========
class Publication(BaseModel):
    type: str = Field(description="Article, Interview, Podcast, etc.")
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    date: Optional[str] = None
    reach: Optional[str] = None

# ========== LINKEDIN ACTIVITY ANALYSIS (v3.1) ==========
class LinkedInPost(BaseModel):
    content_summary: str = Field(description="Résumé du post")
    date: Optional[str] = None
    themes: List[str] = Field(description="Thématiques abordées")
    expertise_signals: Optional[str] = Field(description="Signaux d'expertise détectés")
    engagement_quality: Optional[str] = Field(description="Qualité de l'engagement observé")

class LinkedInActivityAnalysis(BaseModel):
    posts_analyzed: int = Field(description="Nombre de posts analysés", default=0)
    linkedin_urls_analyzed: Optional[List[str]] = Field(
        description="URLs LinkedIn consultées pour l'analyse (snippets Serper)",
        default=None
    )
    recent_posts: List[LinkedInPost] = Field(description="Résumés des posts récents")
    recurring_themes: List[str] = Field(description="Thématiques récurrentes identifiées")
    expertise_level: Optional[str] = Field(description="Niveau d'expertise démontré")
    authority_signals: Optional[str] = Field(description="Signaux d'autorité (ton, crédibilité, qualité)")
    engagement_analysis: Optional[str] = Field(description="Analyse globale de l'engagement")
    thought_leadership_score: Optional[int] = Field(ge=0, le=100, default=None)
    professional_reputation_assessment: Optional[str] = Field(
        description="Évaluation qualitative basée sur interactions, commentaires, reconnaissance pairs"
    )

# ========== PAPPERS DEEP ANALYSIS (v3.1) ==========
class FinancialHistoryYear(BaseModel):
    year: int
    revenue: Optional[str] = None
    result: Optional[str] = None
    equity: Optional[str] = None
    employees: Optional[int] = None

class MandateHistory(BaseModel):
    company_name: str
    siren: Optional[str] = None
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = Field(description="Actif, Radié, etc.")
    company_status: Optional[str] = None

class RealEstateAsset(BaseModel):
    type: str = Field(description="Parcelle, Transaction DVF, etc.")
    location: Optional[str] = None
    date: Optional[str] = None
    value: Optional[str] = None
    details: Optional[str] = None

class PappersDeepAnalysis(BaseModel):
    financial_history: List[FinancialHistoryYear] = Field(description="Évolution financière 5 dernières années")
    mandate_history: List[MandateHistory] = Field(description="Historique complet des mandats")
    legal_issues: List[str] = Field(description="Décisions de justice, procédures en cours")
    real_estate_assets: List[RealEstateAsset] = Field(description="Patrimoine immobilier détecté")
    bodacc_complete: List[str] = Field(description="Publications BODACC complètes")
    rcs_observations: List[str] = Field(description="Observations RCS")
    credibility_indicators: Optional[str] = Field(
        description="Bilans déposés à temps, mandats actifs, conformité, etc."
    )

# ========== MAIN PROFILE ==========
class PersonProfileV3(BaseModel):
    full_name: str
    current_position: Optional[str] = None
    company: Optional[str] = None

    # Core assessments
    risk_assessment: Optional[RiskAssessment] = None
    business_ecosystem: Optional[BusinessEcosystem] = None
    financial_intelligence: Optional[FinancialIntelligence] = None

    # Experience & Timeline
    professional_experience: List[ProfessionalExperience] = []
    career_timeline: List[TimelineEvent] = []

    # Media & Reputation
    media_presence: Optional[MediaPresence] = None

    # Intelligence
    competitive_intelligence: Optional[CompetitiveIntelligence] = None
    official_records: Optional[OfficialRecords] = None

    # Psychology & Network
    psychology_and_approach: Optional[PsychologyAndApproach] = None
    network_and_influence: Optional[NetworkAndInfluence] = None

    # Flags & Analysis
    red_flags: List[RedFlag] = []
    coherence_analysis: Optional[CoherenceAnalysis] = None

    # v3.1 Deep Analysis
    linkedin_activity_analysis: Optional[LinkedInActivityAnalysis] = None
    pappers_deep_analysis: Optional[PappersDeepAnalysis] = None

    # Skills & Publications
    skills: List[str] = []
    publications_and_visibility: List[Publication] = []

    # Contact & Summary
    public_contact: Optional[dict] = None
    summary: Optional[str] = None
    strategic_recommendations: List[str] = []

    # Meta
    linkedin_url: Optional[str] = None
    sources: List[str] = []
