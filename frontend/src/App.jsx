import { useState } from 'react';
import SearchForm from './components/SearchForm';
import ProfileResults from './components/ProfileResults';
import { searchPerson } from './services/api';

function App() {
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  const [cacheInfo, setCacheInfo] = useState(null);

  const handleSearch = async (formData) => {
    setLoading(true);
    setError(null);
    setProfile(null);
    setCacheInfo(null);

    try {
      const result = await searchPerson(
        formData.firstName,
        formData.lastName,
        formData.company,
        formData.forceRefresh
      );

      if (result.success) {
        setProfile(result.data);
        setCacheInfo({
          cached: result.cached || false,
          cacheAge: result.cache_age_seconds,
          cacheCreatedAt: result.cache_created_at
        });
      } else {
        setError(result.message || 'Une erreur est survenue');
      }
    } catch (err) {
      setError(err.message || 'Impossible de contacter le serveur');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-8 lg:py-12">
        {/* Header */}
        <div className="text-center mb-8 lg:mb-12">
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-3">
            LumironScraper
          </h1>
          <p className="text-base md:text-lg text-gray-600 max-w-2xl mx-auto">
            Intelligence de profils professionnels pour accompagner vos démarches commerciales
          </p>
        </div>

        <div className={`flex flex-col lg:flex-row lg:items-start lg:gap-8 mx-auto transition-all duration-300 ${
          profile || loading ? 'max-w-7xl' : 'max-w-2xl'
        }`}>
          <div className={`w-full transition-all duration-300 ${
            profile || loading ? 'lg:w-1/2 lg:sticky lg:top-8' : 'lg:w-full'
          }`}>
            <SearchForm onSubmit={handleSearch} loading={loading} />

            {error && (
              <div className="mt-6 animate-fadeIn">
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm text-red-700">{error}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {!loading && !profile && !error && (
              <div className="mt-8 lg:mt-12 animate-fadeIn">
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">
                    Comment ça fonctionne ?
                  </h3>
                  <ol className="space-y-3 text-gray-600 text-sm">
                    <li className="flex items-start">
                      <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-primary-100 text-primary-700 rounded-full mr-3 font-semibold text-xs">
                        1
                      </span>
                      <span>Saisissez le prénom, nom et entreprise de la personne recherchée</span>
                    </li>
                    <li className="flex items-start">
                      <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-primary-100 text-primary-700 rounded-full mr-3 font-semibold text-xs">
                        2
                      </span>
                      <span>Notre système collecte des informations publiques sur plusieurs sources web</span>
                    </li>
                    <li className="flex items-start">
                      <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-primary-100 text-primary-700 rounded-full mr-3 font-semibold text-xs">
                        3
                      </span>
                      <span>L'intelligence artificielle analyse et structure les données en un profil cohérent</span>
                    </li>
                    <li className="flex items-start">
                      <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-primary-100 text-primary-700 rounded-full mr-3 font-semibold text-xs">
                        4
                      </span>
                      <span>Vous recevez un résumé professionnel complet et exploitable</span>
                    </li>
                  </ol>
                </div>
              </div>
            )}
          </div>

          {(loading || profile) && (
            <div className="w-full lg:w-1/2 mt-8 lg:mt-0">
              {loading && (
                <div className="animate-slideInRight">
                  <div className="bg-white rounded-lg shadow-md p-8">
                    <div className="flex flex-col items-center justify-center space-y-4">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                      <p className="text-gray-600 text-center text-sm">
                        Analyse en cours... Nous collectons et analysons les informations disponibles.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {profile && !loading && (
                <div className="animate-slideInRight">
                  {cacheInfo && (
                    <div className="mb-4">
                      <div className={`${cacheInfo.cached ? 'bg-green-50 border-green-200' : 'bg-blue-50 border-blue-200'} border rounded-lg p-3`}>
                        <div className="flex items-center text-sm">
                          {cacheInfo.cached ? (
                            <>
                              <svg className="w-5 h-5 text-green-600 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                              </svg>
                              <span className="text-green-800">
                                Données du cache ({Math.floor(cacheInfo.cacheAge / 60)} min)
                              </span>
                            </>
                          ) : (
                            <>
                              <svg className="w-5 h-5 text-blue-600 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                              </svg>
                              <span className="text-blue-800">Données fraîches (nouvellement scrapées)</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                  <ProfileResults profile={profile} />
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <footer className="mt-16 pb-8 text-center text-gray-500 text-sm">
        <p>LumironScraper - Intelligence de profils professionnels</p>
      </footer>
    </div>
  );
}

export default App;
