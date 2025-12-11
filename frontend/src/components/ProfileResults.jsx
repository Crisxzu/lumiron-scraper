import { useState } from 'react';

const ProfileResults = ({ profile }) => {
  const [activeTab, setActiveTab] = useState('overview');

  if (!profile) return null;

  // Calculer le niveau de risque avec couleur
  const getRiskColor = (level) => {
    switch(level?.toLowerCase()) {
      case 'faible': return 'text-green-600 bg-green-50';
      case 'moyen': return 'text-yellow-600 bg-yellow-50';
      case 'élevé': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: '📊' },
    { id: 'experience', label: 'Expérience', icon: '💼' },
    { id: 'financial', label: 'Financier', icon: '💰' },
    { id: 'media', label: 'Médias & Réputation', icon: '📰' },
    { id: 'network', label: 'Réseau & Influence', icon: '🤝' },
    { id: 'linkedin', label: 'LinkedIn', icon: '💼' },
    { id: 'pappers', label: 'Pappers Premium', icon: '📋' },
    { id: 'analysis', label: 'Analyse', icon: '🔍' },
  ];

  return (
    <div className="w-full max-w-7xl mx-auto mt-8">
      {/* Header avec Risk Assessment */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-8 py-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-3xl font-bold text-white">{profile.full_name}</h2>
              {profile.current_position && (
                <p className="text-primary-100 mt-2 text-lg">
                  {profile.current_position}
                  {profile.company && ` chez ${profile.company}`}
                </p>
              )}
            </div>
            {profile.risk_assessment && (
              <div className="text-right">
                <div className={`inline-block px-4 py-2 rounded-lg font-semibold ${getRiskColor(profile.risk_assessment.risk_level)}`}>
                  Risque: {profile.risk_assessment.risk_level || 'Non évalué'}
                </div>
                {profile.risk_assessment.credibility_score && (
                  <div className="text-white mt-2 text-sm">
                    Score de crédibilité: {profile.risk_assessment.credibility_score}/100
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Summary */}
        {profile.summary && (
          <div className="px-8 py-6 border-b border-gray-200">
            <p className="text-gray-700 leading-relaxed">{profile.summary}</p>
          </div>
        )}

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <div className="flex overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-3 font-medium text-sm whitespace-nowrap transition-colors ${
                  activeTab === tab.id
                    ? 'border-b-2 border-primary-600 text-primary-600'
                    : 'text-gray-600 hover:text-gray-800 hover:border-b-2 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-8">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Risk Assessment */}
              {profile.risk_assessment && (
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">Évaluation des Risques</h3>
                  {profile.risk_assessment.overall_assessment && (
                    <p className="text-gray-700 mb-4">{profile.risk_assessment.overall_assessment}</p>
                  )}

                  {profile.risk_assessment.trust_indicators && profile.risk_assessment.trust_indicators.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium text-green-800 mb-2">✓ Indicateurs de confiance</h4>
                      <ul className="space-y-1">
                        {profile.risk_assessment.trust_indicators.map((indicator, idx) => (
                          <li key={idx} className="text-sm text-gray-700 flex items-start">
                            <span className="text-green-600 mr-2">•</span>
                            {indicator}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {profile.risk_assessment.risk_factors && profile.risk_assessment.risk_factors.length > 0 && (
                    <div>
                      <h4 className="font-medium text-yellow-800 mb-2">⚠️ Facteurs de risque</h4>
                      <ul className="space-y-1">
                        {profile.risk_assessment.risk_factors.map((factor, idx) => (
                          <li key={idx} className="text-sm text-gray-700 flex items-start">
                            <span className="text-yellow-600 mr-2">•</span>
                            {factor}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Red Flags */}
              {profile.red_flags && profile.red_flags.length > 0 && (
                <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded">
                  <h3 className="text-xl font-semibold text-red-800 mb-4">🚩 Signaux d'Alerte</h3>
                  <div className="space-y-4">
                    {profile.red_flags.map((flag, idx) => (
                      <div key={idx} className="bg-white p-4 rounded">
                        <div className="flex justify-between items-start mb-2">
                          <span className="font-medium text-red-800">{flag.type}</span>
                          <span className={`text-xs px-2 py-1 rounded ${
                            flag.severity === 'Critique' ? 'bg-red-200 text-red-800' :
                            flag.severity === 'Modéré' ? 'bg-yellow-200 text-yellow-800' :
                            'bg-gray-200 text-gray-800'
                          }`}>
                            {flag.severity}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 mb-2">{flag.description}</p>
                        {flag.source && <p className="text-xs text-gray-500">Source: {flag.source}</p>}
                        {flag.recommendation && (
                          <p className="text-sm text-red-700 mt-2">→ {flag.recommendation}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Strategic Recommendations */}
              {profile.strategic_recommendations && profile.strategic_recommendations.length > 0 && (
                <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded">
                  <h3 className="text-xl font-semibold text-blue-800 mb-4">💡 Recommandations Stratégiques</h3>
                  <ul className="space-y-2">
                    {profile.strategic_recommendations.map((rec, idx) => (
                      <li key={idx} className="text-gray-700 flex items-start">
                        <span className="text-blue-600 mr-2 font-bold">{idx + 1}.</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Business Ecosystem */}
              {profile.business_ecosystem && profile.business_ecosystem.companies_led && profile.business_ecosystem.companies_led.length > 0 && (
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">🏢 Entreprises Dirigées</h3>
                  <div className="grid gap-4">
                    {profile.business_ecosystem.companies_led.map((company, idx) => (
                      <div key={idx} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h4 className="font-semibold text-gray-800">{company.name}</h4>
                            <p className="text-sm text-gray-600">{company.role} {company.since && `depuis ${company.since}`}</p>
                          </div>
                          <span className={`text-xs px-2 py-1 rounded ${
                            company.status === 'Actif' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {company.status}
                          </span>
                        </div>
                        {company.siren && <p className="text-xs text-gray-500">SIREN: {company.siren}</p>}
                        {company.financial_health && (
                          <p className="text-sm text-gray-700 mt-2">{company.financial_health}</p>
                        )}
                        <div className="flex gap-4 mt-2 text-xs text-gray-600">
                          {company.revenue && <span>CA: {company.revenue}</span>}
                          {company.employees && <span>Effectif: {company.employees}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Experience Tab */}
          {activeTab === 'experience' && (
            <div className="space-y-6">
              {/* Career Timeline */}
              {profile.career_timeline && profile.career_timeline.length > 0 && (
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">📅 Timeline Carrière</h3>
                  <div className="relative border-l-2 border-gray-300 pl-6 space-y-6">
                    {profile.career_timeline.map((event, idx) => (
                      <div key={idx} className="relative">
                        <div className="absolute -left-8 w-4 h-4 bg-primary-600 rounded-full border-2 border-white"></div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <div className="flex justify-between items-start mb-2">
                            <span className="font-semibold text-primary-600">{event.year}</span>
                            <span className="text-xs px-2 py-1 bg-gray-200 rounded">{event.type}</span>
                          </div>
                          <p className="text-gray-800 font-medium">{event.event}</p>
                          {event.impact && <p className="text-sm text-gray-600 mt-1">{event.impact}</p>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Professional Experience */}
              {profile.professional_experience && profile.professional_experience.length > 0 && (
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">💼 Expérience Professionnelle</h3>
                  <div className="space-y-4">
                    {profile.professional_experience.map((exp, idx) => (
                      <div key={idx} className="border-l-2 border-gray-300 pl-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h4 className="font-semibold text-gray-800">{exp.position}</h4>
                            <p className="text-primary-600">{exp.company}</p>
                          </div>
                          {exp.verified && (
                            <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">✓ Vérifié</span>
                          )}
                        </div>
                        {exp.period && <p className="text-sm text-gray-500">{exp.period}</p>}
                        {exp.description && <p className="text-gray-600 mt-2">{exp.description}</p>}
                        {exp.achievements && <p className="text-sm text-gray-700 mt-2 italic">→ {exp.achievements}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Skills */}
              {profile.skills && profile.skills.length > 0 && (
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">🎯 Compétences</h3>
                  <div className="flex flex-wrap gap-2">
                    {profile.skills.map((skill, idx) => (
                      <span key={idx} className="bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm font-medium">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Psychology & Approach */}
              {profile.psychology_and_approach && (
                <div className="bg-purple-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">🧠 Psychologie & Approche</h3>

                  {profile.psychology_and_approach.personality_traits && profile.psychology_and_approach.personality_traits.length > 0 && (
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-700 mb-2">Traits de personnalité</h4>
                      <ul className="space-y-1">
                        {profile.psychology_and_approach.personality_traits.map((trait, idx) => (
                          <li key={idx} className="text-sm text-gray-700">• {trait}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {profile.psychology_and_approach.decision_making_style && (
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-700 mb-2">Style de décision</h4>
                      <p className="text-sm text-gray-700">{profile.psychology_and_approach.decision_making_style}</p>
                    </div>
                  )}

                  {profile.psychology_and_approach.ice_breakers && profile.psychology_and_approach.ice_breakers.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">💬 Ice breakers suggérés</h4>
                      <ul className="space-y-1">
                        {profile.psychology_and_approach.ice_breakers.map((icebreaker, idx) => (
                          <li key={idx} className="text-sm text-gray-700">→ {icebreaker}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Financial Tab */}
          {activeTab === 'financial' && (
            <div className="space-y-6">
              {profile.financial_intelligence && (
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">💰 Intelligence Financière</h3>
                  <div className="grid gap-4">
                    {profile.financial_intelligence.revenue_evolution && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">Évolution du CA</h4>
                        <p className="text-gray-700">{profile.financial_intelligence.revenue_evolution}</p>
                        {profile.financial_intelligence.revenue_evolution_source && (
                          <p className="text-xs text-gray-500 mt-2">Source: {profile.financial_intelligence.revenue_evolution_source}</p>
                        )}
                      </div>
                    )}

                    {profile.financial_intelligence.financial_stability && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">Stabilité Financière</h4>
                        <p className="text-gray-700">{profile.financial_intelligence.financial_stability}</p>
                        {profile.financial_intelligence.financial_stability_source && (
                          <p className="text-xs text-gray-500 mt-2">Source: {profile.financial_intelligence.financial_stability_source}</p>
                        )}
                      </div>
                    )}

                    {profile.financial_intelligence.capital_structure && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">Structure du Capital</h4>
                        <p className="text-gray-700">{profile.financial_intelligence.capital_structure}</p>
                        {profile.financial_intelligence.capital_structure_source && (
                          <p className="text-xs text-gray-500 mt-2">Source: {profile.financial_intelligence.capital_structure_source}</p>
                        )}
                      </div>
                    )}

                    {profile.financial_intelligence.investment_capacity && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">Capacité d'Investissement</h4>
                        <p className="text-gray-700">{profile.financial_intelligence.investment_capacity}</p>
                      </div>
                    )}

                    {profile.financial_intelligence.financial_red_flags && profile.financial_intelligence.financial_red_flags.length > 0 && (
                      <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                        <h4 className="font-medium text-red-700 mb-2">⚠️ Red Flags Financiers</h4>
                        <ul className="space-y-1">
                          {profile.financial_intelligence.financial_red_flags.map((flag, idx) => (
                            <li key={idx} className="text-sm text-red-700">• {flag}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {profile.business_ecosystem && (
                <div>
                  {profile.business_ecosystem.estimated_wealth && (
                    <div className="bg-green-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-700 mb-2">💎 Patrimoine Estimé</h4>
                      <p className="text-gray-700">{profile.business_ecosystem.estimated_wealth}</p>
                    </div>
                  )}

                  {profile.business_ecosystem.real_estate_assets && (
                    <div className="bg-blue-50 p-4 rounded-lg mt-4">
                      <h4 className="font-medium text-gray-700 mb-2">🏠 Patrimoine Immobilier</h4>
                      <p className="text-gray-700">{profile.business_ecosystem.real_estate_assets}</p>
                    </div>
                  )}
                </div>
              )}

              {profile.pappers_deep_analysis && (
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 my-4">Analyse Approfondie (Pappers)</h3>
                  <div className="bg-gray-100 p-6 rounded-lg space-y-4">
                    {profile.pappers_deep_analysis.credibility_indicators && (
                      <div>
                        <h4 className="font-medium text-gray-800 mb-2">Indicateurs de Crédibilité</h4>
                        <p className="text-sm text-gray-700">{profile.pappers_deep_analysis.credibility_indicators}</p>
                      </div>
                    )}

                    {profile.pappers_deep_analysis.mandate_history && profile.pappers_deep_analysis.mandate_history.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-800 mb-2">Historique des Mandats</h4>
                        <div className="space-y-2">
                          {profile.pappers_deep_analysis.mandate_history.map((mandate, idx) => (
                            <div key={idx} className="bg-white p-3 rounded-md border">
                              <p className="font-semibold">{mandate.company}</p>
                              <p className="text-sm text-gray-600">{mandate.role} (de {mandate.since} à {mandate.until || 'aujourd\'hui'})</p>
                              <span className={`text-xs px-2 py-1 mt-1 inline-block rounded ${mandate.status === 'Actif' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>{mandate.status}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {profile.pappers_deep_analysis.financial_history && profile.pappers_deep_analysis.financial_history.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-800 mb-2">Historique Financier</h4>
                        {/* Implémentation de l'affichage à prévoir */}
                      </div>
                    )}

                    {profile.pappers_deep_analysis.legal_issues && profile.pappers_deep_analysis.legal_issues.length > 0 && (
                      <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                        <h4 className="font-medium text-yellow-800 mb-2">Problèmes Légaux</h4>
                        <ul className="space-y-1 list-disc list-inside">
                          {profile.pappers_deep_analysis.legal_issues.map((issue, idx) => (
                            <li key={idx} className="text-sm text-gray-700">{issue}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {profile.pappers_deep_analysis.bodacc_complete && profile.pappers_deep_analysis.bodacc_complete.length > 0 && (
                      <div>
                        <h4 className="font-medium text-gray-800 mb-2">Publications BODACC complètes</h4>
                        <ul className="space-y-1 list-disc list-inside">
                          {profile.pappers_deep_analysis.bodacc_complete.map((item, idx) => (
                            <li key={idx} className="text-sm text-gray-700">{item}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Media Tab */}
          {activeTab === 'media' && (
            <div className="space-y-6">
              {profile.media_presence && (
                <>
                  {profile.media_presence.reputation_score !== undefined && (
                    <div className="bg-gradient-to-r from-purple-50 to-pink-50 p-6 rounded-lg">
                      <div className="flex justify-between items-center">
                        <h3 className="text-xl font-semibold text-gray-800">Score de Réputation</h3>
                        <div className="text-4xl font-bold text-primary-600">{profile.media_presence.reputation_score}/100</div>
                      </div>
                      {profile.media_presence.media_sentiment_analysis && (
                        <p className="text-gray-700 mt-2">{profile.media_presence.media_sentiment_analysis}</p>
                      )}
                    </div>
                  )}

                  {profile.media_presence.press_mentions && profile.media_presence.press_mentions.length > 0 && (
                    <div>
                      <h3 className="text-xl font-semibold text-gray-800 mb-4">📰 Mentions Presse</h3>
                      <div className="space-y-4">
                        {profile.media_presence.press_mentions.map((mention, idx) => (
                          <div key={idx} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex justify-between items-start mb-2">
                              <h4 className="font-semibold text-gray-800">{mention.title}</h4>
                              {mention.sentiment && (
                                <span className={`text-xs px-2 py-1 rounded ${
                                  mention.sentiment === 'Positif' ? 'bg-green-100 text-green-800' :
                                  mention.sentiment === 'Négatif' ? 'bg-red-100 text-red-800' :
                                  'bg-gray-100 text-gray-800'
                                }`}>
                                  {mention.sentiment}
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600">{mention.source} {mention.date && `• ${mention.date}`}</p>
                            {mention.summary && <p className="text-gray-700 mt-2">{mention.summary}</p>}
                            {mention.url && (
                              <a href={mention.url} target="_blank" rel="noopener noreferrer" className="text-xs text-primary-600 hover:underline mt-2 inline-block">
                                Lire l'article →
                              </a>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {profile.media_presence.thought_leadership && (
                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-700 mb-2">🎓 Leadership d'Opinion</h4>
                      <p className="text-gray-700">{profile.media_presence.thought_leadership}</p>
                    </div>
                  )}
                </>
              )}

              {/* LinkedIn Activity Analysis */}
              {profile.linkedin_activity_analysis && (
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">🎤 Activité LinkedIn</h3>
                  <div className="bg-gray-50 p-6 rounded-lg">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-medium text-gray-700 mb-2">Statistiques</h4>
                        <p className="text-sm text-gray-700">Posts analysés: {profile.linkedin_activity_analysis.posts_analyzed}</p>
                        {profile.linkedin_activity_analysis.expertise_level && <p className="text-sm text-gray-700">Niveau d'expertise: {profile.linkedin_activity_analysis.expertise_level}</p>}
                        {profile.linkedin_activity_analysis.thought_leadership_score && <p className="text-sm text-gray-700">Score de leadership: {profile.linkedin_activity_analysis.thought_leadership_score}/100</p>}
                      </div>
                      {profile.linkedin_activity_analysis.recurring_themes && profile.linkedin_activity_analysis.recurring_themes.length > 0 && (
                        <div>
                          <h4 className="font-medium text-gray-700 mb-2">Thèmes récurrents</h4>
                          <div className="flex flex-wrap gap-2">
                            {profile.linkedin_activity_analysis.recurring_themes.map((theme, idx) => (
                              <span key={idx} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                                {theme}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    {profile.linkedin_activity_analysis.professional_reputation_assessment && (
                      <div className="mt-4">
                        <h4 className="font-medium text-gray-700 mb-2">Réputation professionnelle</h4>
                        <p className="text-sm text-gray-700">{profile.linkedin_activity_analysis.professional_reputation_assessment}</p>
                      </div>
                    )}
                    {profile.linkedin_activity_analysis.recent_posts && profile.linkedin_activity_analysis.recent_posts.length > 0 && (
                      <div className="mt-6">
                        <h4 className="font-medium text-gray-700 mb-2">Posts récents</h4>
                        <div className="space-y-4">
                          {profile.linkedin_activity_analysis.recent_posts.map((post, idx) => (
                            <div key={idx} className="border border-gray-200 bg-white rounded-lg p-4">
                              <p className="text-sm text-gray-700">{post.content_summary}</p>
                              {post.date && <p className="text-xs text-gray-500 mt-2">{post.date}</p>}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {profile.linkedin_activity_analysis.linkedin_urls_analyzed && profile.linkedin_activity_analysis.linkedin_urls_analyzed.length > 0 && (
                      <div className="mt-6">
                        <h4 className="font-medium text-gray-700 mb-2">URLs LinkedIn Analysées</h4>
                        <ul className="space-y-2">
                          {profile.linkedin_activity_analysis.linkedin_urls_analyzed.map((url, idx) => (
                            <li key={idx} className="text-sm">
                              <a href={url} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline break-all">
                                {url}
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {profile.competitive_intelligence && (
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">🎯 Intelligence Concurrentielle</h3>
                  <div className="grid gap-4">
                    {profile.competitive_intelligence.market_position && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">Position Marché</h4>
                        <p className="text-gray-700">{profile.competitive_intelligence.market_position}</p>
                      </div>
                    )}

                    {profile.competitive_intelligence.innovation_signals && profile.competitive_intelligence.innovation_signals.length > 0 && (
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">💡 Signaux d'Innovation</h4>
                        <ul className="space-y-1">
                          {profile.competitive_intelligence.innovation_signals.map((signal, idx) => (
                            <li key={idx} className="text-sm text-gray-700">• {signal}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {profile.competitive_intelligence.strategic_moves && profile.competitive_intelligence.strategic_moves.length > 0 && (
                      <div className="bg-green-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">♟️ Mouvements Stratégiques</h4>
                        <ul className="space-y-1">
                          {profile.competitive_intelligence.strategic_moves.map((move, idx) => (
                            <li key={idx} className="text-sm text-gray-700">• {move}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Network Tab */}
          {activeTab === 'network' && (
            <div className="space-y-6">
              {profile.network_and_influence && (
                <>
                  {profile.network_and_influence.influence_score !== undefined && (
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg">
                      <div className="flex justify-between items-center">
                        <h3 className="text-xl font-semibold text-gray-800">Score d'Influence</h3>
                        <div className="text-4xl font-bold text-primary-600">{profile.network_and_influence.influence_score}/100</div>
                      </div>
                      {profile.network_and_influence.influence_analysis && (
                        <p className="text-gray-700 mt-2">{profile.network_and_influence.influence_analysis}</p>
                      )}
                    </div>
                  )}

                  <div className="grid gap-4">
                    {profile.network_and_influence.key_connections && profile.network_and_influence.key_connections.length > 0 && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">🤝 Connexions Clés</h4>
                        <ul className="space-y-1">
                          {profile.network_and_influence.key_connections.map((connection, idx) => (
                            <li key={idx} className="text-sm text-gray-700">• {connection}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {profile.network_and_influence.board_positions && profile.network_and_influence.board_positions.length > 0 && (
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">🏛️ Postes au Conseil</h4>
                        <ul className="space-y-1">
                          {profile.network_and_influence.board_positions.map((position, idx) => (
                            <li key={idx} className="text-sm text-gray-700">• {position}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {profile.network_and_influence.associations_memberships && profile.network_and_influence.associations_memberships.length > 0 && (
                      <div className="bg-green-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">🎓 Associations & Memberships</h4>
                        <ul className="space-y-1">
                          {profile.network_and_influence.associations_memberships.map((assoc, idx) => (
                            <li key={idx} className="text-sm text-gray-700">• {assoc}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </>
              )}

              {profile.public_contact && (
                <div className="border-t pt-6">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">📧 Contact Public</h3>
                  <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                    {profile.public_contact.linkedin && (
                      <a href={profile.public_contact.linkedin} target="_blank" rel="noopener noreferrer" className="flex items-center text-primary-600 hover:underline">
                        <span className="mr-2">🔗</span> LinkedIn
                      </a>
                    )}
                    {profile.public_contact.website && (
                      <a href={profile.public_contact.website} target="_blank" rel="noopener noreferrer" className="flex items-center text-primary-600 hover:underline">
                        <span className="mr-2">🌐</span> {profile.public_contact.website}
                      </a>
                    )}
                    {profile.public_contact.email && (
                      <a href={`mailto:${profile.public_contact.email}`} className="flex items-center text-primary-600 hover:underline">
                        <span className="mr-2">✉️</span> {profile.public_contact.email}
                      </a>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Analysis Tab */}
          {/* LinkedIn Activity Tab (v3.1) */}
          {activeTab === 'linkedin' && profile.linkedin_activity_analysis && (
            <div className="space-y-6">
              <h3 className="text-2xl font-semibold text-gray-800 mb-4">💼 Activité LinkedIn</h3>

              {/* Thought Leadership Score */}
              {profile.linkedin_activity_analysis.thought_leadership_score !== undefined && (
                <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg">
                  <div className="flex justify-between items-center mb-4">
                    <div>
                      <h4 className="text-lg font-semibold text-gray-800">Score de Leadership d'Opinion</h4>
                      <p className="text-sm text-gray-600 mt-1">
                        Niveau: <span className="font-medium">{profile.linkedin_activity_analysis.expertise_level || 'Non déterminé'}</span>
                      </p>
                    </div>
                    <div className="text-4xl font-bold text-primary-600">
                      {profile.linkedin_activity_analysis.thought_leadership_score}/100
                    </div>
                  </div>

                  {/* Score interpretation */}
                  <div className="mt-4 pt-4 border-t border-indigo-200">
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-primary-600 h-3 rounded-full transition-all"
                        style={{ width: `${profile.linkedin_activity_analysis.thought_leadership_score}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-2">
                      <span>0 - Faible</span>
                      <span>40 - Modéré</span>
                      <span>60 - Avancé</span>
                      <span>80+ - Expert</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Posts Analyzed & Recent Posts */}
              {profile.linkedin_activity_analysis.recent_posts && profile.linkedin_activity_analysis.recent_posts.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-4">
                    📝 Posts Analysés ({profile.linkedin_activity_analysis.posts_analyzed || 0})
                  </h4>
                  <div className="space-y-4">
                    {profile.linkedin_activity_analysis.recent_posts.map((post, idx) => (
                      <div key={idx} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <p className="text-sm text-gray-700 mb-3">{post.content_summary}</p>
                        <div className="flex flex-wrap gap-2 mb-2">
                          {post.themes && post.themes.map((theme, i) => (
                            <span key={i} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                              {theme}
                            </span>
                          ))}
                        </div>
                        {post.date && (
                          <p className="text-xs text-gray-500 mt-2">📅 {post.date}</p>
                        )}
                        {post.engagement_quality && (
                          <p className="text-xs text-gray-600 mt-1">💬 {post.engagement_quality}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recurring Themes */}
              {profile.linkedin_activity_analysis.recurring_themes && profile.linkedin_activity_analysis.recurring_themes.length > 0 && (
                <div className="bg-white p-4 rounded-lg border border-gray-200">
                  <h4 className="font-semibold text-gray-800 mb-3">🎯 Thématiques Récurrentes</h4>
                  <div className="flex flex-wrap gap-2">
                    {profile.linkedin_activity_analysis.recurring_themes.map((theme, idx) => (
                      <span key={idx} className="px-3 py-1 bg-primary-100 text-primary-700 text-sm rounded-full font-medium">
                        {theme}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Authority Signals */}
              {profile.linkedin_activity_analysis.authority_signals && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-700 mb-2">⭐ Signaux d'Autorité</h4>
                  <p className="text-sm text-gray-700">{profile.linkedin_activity_analysis.authority_signals}</p>
                </div>
              )}

              {/* Engagement Analysis */}
              {profile.linkedin_activity_analysis.engagement_analysis && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-700 mb-2">📊 Analyse d'Engagement</h4>
                  <p className="text-sm text-gray-700">{profile.linkedin_activity_analysis.engagement_analysis}</p>
                </div>
              )}

              {/* Professional Reputation */}
              {profile.linkedin_activity_analysis.professional_reputation_assessment && (
                <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg border border-green-200">
                  <h4 className="font-medium text-gray-800 mb-2">✨ Réputation Professionnelle</h4>
                  <p className="text-sm text-gray-700">{profile.linkedin_activity_analysis.professional_reputation_assessment}</p>
                </div>
              )}

              {/* LinkedIn URLs Analyzed */}
              {profile.linkedin_activity_analysis.linkedin_urls_analyzed && profile.linkedin_activity_analysis.linkedin_urls_analyzed.length > 0 && (
                <div className="border-t pt-4">
                  <details className="cursor-pointer">
                    <summary className="text-sm font-medium text-gray-700 mb-2">
                      🔗 URLs LinkedIn Consultées ({profile.linkedin_activity_analysis.linkedin_urls_analyzed.length})
                    </summary>
                    <ul className="mt-3 space-y-1">
                      {profile.linkedin_activity_analysis.linkedin_urls_analyzed.map((url, idx) => (
                        <li key={idx} className="text-xs">
                          <a href={url} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline break-all">
                            {url}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </details>
                </div>
              )}
            </div>
          )}

          {/* Pappers Deep Analysis Tab (v3.1) */}
          {activeTab === 'pappers' && profile.pappers_deep_analysis && (
            <div className="space-y-6">
              <h3 className="text-2xl font-semibold text-gray-800 mb-4">📋 Analyse Pappers Premium</h3>

              {/* Mandate History */}
              {profile.pappers_deep_analysis.mandate_history && profile.pappers_deep_analysis.mandate_history.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">👔 Historique des Mandats</h4>
                  <div className="space-y-3">
                    {profile.pappers_deep_analysis.mandate_history.map((mandate, idx) => (
                      <div key={idx} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium text-gray-800">{mandate.company || mandate.company_name}</p>
                            <p className="text-sm text-gray-600 mt-1">{mandate.role}</p>
                            {mandate.siren && (
                              <p className="text-xs text-gray-500 mt-1">SIREN: {mandate.siren}</p>
                            )}
                          </div>
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            mandate.status === 'Actif' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                          }`}>
                            {mandate.status || 'Statut inconnu'}
                          </span>
                        </div>
                        <div className="mt-2 text-sm text-gray-600">
                          {mandate.start_date || mandate.since} → {mandate.end_date || mandate.until || 'En cours'}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Financial History */}
              {profile.pappers_deep_analysis.financial_history && profile.pappers_deep_analysis.financial_history.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">💰 Historique Financier (5 ans)</h4>
                  <div className="overflow-x-auto">
                    <table className="min-w-full bg-white border border-gray-200 rounded-lg">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Année</th>
                          <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">CA</th>
                          <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Résultat</th>
                          <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Capitaux Propres</th>
                          <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Effectif</th>
                        </tr>
                      </thead>
                      <tbody>
                        {profile.pappers_deep_analysis.financial_history.map((year, idx) => (
                          <tr key={idx} className="border-t border-gray-200">
                            <td className="px-4 py-2 text-sm text-gray-800 font-medium">{year.year}</td>
                            <td className="px-4 py-2 text-sm text-gray-700">{year.revenue || 'N/A'}</td>
                            <td className="px-4 py-2 text-sm text-gray-700">{year.result || 'N/A'}</td>
                            <td className="px-4 py-2 text-sm text-gray-700">{year.equity || 'N/A'}</td>
                            <td className="px-4 py-2 text-sm text-gray-700">{year.employees !== undefined ? year.employees : 'N/A'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Legal Issues */}
              {profile.pappers_deep_analysis.legal_issues && profile.pappers_deep_analysis.legal_issues.length > 0 && (
                <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                  <h4 className="font-semibold text-red-800 mb-3">⚠️ Questions Juridiques</h4>
                  <ul className="space-y-2">
                    {profile.pappers_deep_analysis.legal_issues.map((issue, idx) => (
                      <li key={idx} className="text-sm text-gray-700">• {issue}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Real Estate Assets */}
              {profile.pappers_deep_analysis.real_estate_assets && profile.pappers_deep_analysis.real_estate_assets.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-800 mb-3">🏠 Patrimoine Immobilier</h4>
                  <div className="space-y-3">
                    {profile.pappers_deep_analysis.real_estate_assets.map((asset, idx) => (
                      <div key={idx} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <p className="font-medium text-gray-800">{asset.type}</p>
                        {asset.location && (
                          <p className="text-sm text-gray-600 mt-1">📍 {asset.location}</p>
                        )}
                        {asset.value && (
                          <p className="text-sm text-gray-600 mt-1">💵 {asset.value}</p>
                        )}
                        {asset.date && (
                          <p className="text-xs text-gray-500 mt-1">📅 {asset.date}</p>
                        )}
                        {asset.details && (
                          <p className="text-sm text-gray-700 mt-2">{asset.details}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* BODACC Complete */}
              {profile.pappers_deep_analysis.bodacc_complete && profile.pappers_deep_analysis.bodacc_complete.length > 0 && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium text-gray-700 mb-2">📰 Publications BODACC Complètes</h4>
                  <ul className="space-y-1">
                    {profile.pappers_deep_analysis.bodacc_complete.map((pub, idx) => (
                      <li key={idx} className="text-sm text-gray-700">• {pub}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* RCS Observations */}
              {profile.pappers_deep_analysis.rcs_observations && profile.pappers_deep_analysis.rcs_observations.length > 0 && (
                <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                  <h4 className="font-medium text-yellow-800 mb-2">📌 Observations RCS</h4>
                  <ul className="space-y-1">
                    {profile.pappers_deep_analysis.rcs_observations.map((obs, idx) => (
                      <li key={idx} className="text-sm text-gray-700">• {obs}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Credibility Indicators */}
              {profile.pappers_deep_analysis.credibility_indicators && (
                <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-4 rounded-lg border border-green-200">
                  <h4 className="font-medium text-gray-800 mb-2">✅ Indicateurs de Crédibilité</h4>
                  <p className="text-sm text-gray-700">{profile.pappers_deep_analysis.credibility_indicators}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'analysis' && (
            <div className="space-y-6">
              {profile.coherence_analysis && (
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">🔍 Analyse de Cohérence</h3>

                  {profile.coherence_analysis.reliability_score !== undefined && (
                    <div className="bg-gradient-to-r from-green-50 to-teal-50 p-6 rounded-lg mb-4">
                      <div className="flex justify-between items-center mb-4">
                        <h4 className="text-lg font-semibold text-gray-800">Score de Fiabilité</h4>
                        <div className="text-4xl font-bold text-primary-600">{profile.coherence_analysis.reliability_score}/100</div>
                      </div>
                      {profile.coherence_analysis.reliability_justification && (
                        <div className="mt-4 pt-4 border-t border-teal-200">
                          <h5 className="text-sm font-medium text-gray-700 mb-2">Justification</h5>
                          <p className="text-sm text-gray-600 leading-relaxed">{profile.coherence_analysis.reliability_justification}</p>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="grid gap-4">
                    {profile.coherence_analysis.data_consistency && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">Cohérence des Données</h4>
                        <p className="text-sm text-gray-700">{profile.coherence_analysis.data_consistency}</p>
                      </div>
                    )}

                    {profile.coherence_analysis.timeline_verification && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">Vérification Timeline</h4>
                        <p className="text-sm text-gray-700">{profile.coherence_analysis.timeline_verification}</p>
                      </div>
                    )}

                    {profile.coherence_analysis.cross_source_validation && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">Validation Croisée</h4>
                        <p className="text-sm text-gray-700">{profile.coherence_analysis.cross_source_validation}</p>
                      </div>
                    )}

                    {profile.coherence_analysis.discrepancies && profile.coherence_analysis.discrepancies.length > 0 && (
                      <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                        <h4 className="font-medium text-yellow-800 mb-2">⚠️ Incohérences Détectées</h4>
                        <ul className="space-y-1">
                          {profile.coherence_analysis.discrepancies.map((disc, idx) => (
                            <li key={idx} className="text-sm text-gray-700">• {disc}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {profile.official_records && (
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">📋 Registres Officiels</h3>
                  <div className="grid gap-4">
                    {profile.official_records.compliance_status && (
                      <div className={`p-4 rounded-lg ${
                        profile.official_records.compliance_status === 'Conforme' ? 'bg-green-50' :
                        profile.official_records.compliance_status === 'Attention' ? 'bg-yellow-50' :
                        'bg-red-50'
                      }`}>
                        <h4 className="font-medium text-gray-700 mb-2">Statut de Conformité</h4>
                        <p className="text-sm font-semibold">{profile.official_records.compliance_status}</p>
                      </div>
                    )}

                    {profile.official_records.trade_registry_status && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">Statut RCS</h4>
                        <p className="text-sm text-gray-700">{profile.official_records.trade_registry_status}</p>
                      </div>
                    )}

                    {profile.official_records.bodacc_publications && profile.official_records.bodacc_publications.length > 0 && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="font-medium text-gray-700 mb-2">Publications BODACC</h4>
                        <ul className="space-y-1">
                          {profile.official_records.bodacc_publications.map((pub, idx) => (
                            <li key={idx} className="text-sm text-gray-700">• {pub}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Sources */}
              {profile.sources && profile.sources.length > 0 && (
                <div className="border-t pt-6">
                  <details className="cursor-pointer">
                    <summary className="text-lg font-semibold text-gray-800 mb-4">
                      📚 Sources Utilisées ({profile.sources.length})
                    </summary>
                    <div className="mt-4 bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
                      <ul className="space-y-2">
                        {profile.sources.map((source, idx) => (
                          <li key={idx} className="text-sm">
                            <a href={source} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline break-all">
                              {source}
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </details>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileResults;
