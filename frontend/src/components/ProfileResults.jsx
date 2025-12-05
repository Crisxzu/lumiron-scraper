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
          {activeTab === 'analysis' && (
            <div className="space-y-6">
              {profile.coherence_analysis && (
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">🔍 Analyse de Cohérence</h3>

                  {profile.coherence_analysis.reliability_score !== undefined && (
                    <div className="bg-gradient-to-r from-green-50 to-teal-50 p-6 rounded-lg mb-4">
                      <div className="flex justify-between items-center">
                        <h4 className="text-lg font-semibold text-gray-800">Score de Fiabilité</h4>
                        <div className="text-4xl font-bold text-primary-600">{profile.coherence_analysis.reliability_score}/100</div>
                      </div>
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
