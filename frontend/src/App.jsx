import { useState, useRef } from 'react';
import SearchForm from './components/SearchForm';
import ProfileResults from './components/ProfileResults';
import { searchPerson, searchPersonStream } from './services/api';

function App() {
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  const [cacheInfo, setCacheInfo] = useState(null);
  const [progress, setProgress] = useState({ percent: 0, message: '', step: '' });
  const cancelRef = useRef(null);

  const handleSearch = async (formData) => {
    // Annuler toute recherche en cours
    if (cancelRef.current) {
      cancelRef.current();
    }

    setLoading(true);
    setError(null);
    setProfile(null);
    setCacheInfo(null);
    setProgress({ percent: 0, message: 'Initialisation...', step: 'init' });

    // Utiliser le streaming pour avoir la progression
    cancelRef.current = searchPersonStream(
      formData.firstName,
      formData.lastName,
      formData.company,
      formData.forceRefresh,
      // onProgress
      (percent, message, step) => {
        setProgress({ percent, message, step });
      },
      // onComplete
      (result) => {
        if (result.success) {
          setProfile(result.data);
          setCacheInfo({
            cached: result.cached || false,
            cacheAge: result.cache_age_seconds,
          });
          setProgress({ percent: 100, message: 'Terminé !', step: 'done' });
        }
        setLoading(false);
        cancelRef.current = null;
      },
      // onError
      (errorMsg) => {
        setError(errorMsg || 'Une erreur est survenue');
        setLoading(false);
        cancelRef.current = null;
      }
    );
  };

  const handleCancel = () => {
    if (cancelRef.current) {
      cancelRef.current();
      cancelRef.current = null;
      setLoading(false);
      setProgress({ percent: 0, message: '', step: '' });
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
                    <div className="flex flex-col space-y-6">
                      {/* En-tête progression */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">Analyse en cours</h3>
                            <p className="text-sm text-gray-500">{progress.message}</p>
                          </div>
                        </div>
                        <button
                          onClick={handleCancel}
                          className="text-sm text-gray-500 hover:text-red-600 transition-colors"
                        >
                          Annuler
                        </button>
                      </div>

                      {/* Barre de progression */}
                      <div className="w-full">
                        <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                          <span className="font-medium">{progress.percent}%</span>
                          <span className="text-xs text-gray-400">~2-3 minutes</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full transition-all duration-500 ease-out"
                            style={{ width: `${progress.percent}%` }}
                          ></div>
                        </div>
                      </div>

                      {/* Étapes de progression */}
                      <div className="space-y-2 text-sm">
                        <div className={`flex items-center space-x-2 ${progress.step === 'cache' || progress.step === 'cache_hit' ? 'text-primary-600 font-medium' : progress.percent > 5 ? 'text-green-600' : 'text-gray-400'}`}>
                          {progress.percent > 5 ? (
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                          ) : (
                            <div className="w-5 h-5 rounded-full border-2 border-current"></div>
                          )}
                          <span>Vérification du cache</span>
                        </div>

                        <div className={`flex items-center space-x-2 ${progress.step === 'pappers' ? 'text-primary-600 font-medium' : progress.percent > 20 ? 'text-green-600' : 'text-gray-400'}`}>
                          {progress.percent > 20 ? (
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                          ) : (
                            <div className="w-5 h-5 rounded-full border-2 border-current"></div>
                          )}
                          <span>Données légales (Pappers)</span>
                        </div>

                        <div className={`flex items-center space-x-2 ${progress.step === 'serper' ? 'text-primary-600 font-medium' : progress.percent > 30 ? 'text-green-600' : 'text-gray-400'}`}>
                          {progress.percent > 30 ? (
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                          ) : (
                            <div className="w-5 h-5 rounded-full border-2 border-current"></div>
                          )}
                          <span>Recherche Google (30+ URLs)</span>
                        </div>

                        <div className={`flex items-center space-x-2 ${progress.step === 'firecrawl' || progress.step === 'scraped' ? 'text-primary-600 font-medium' : progress.percent > 70 ? 'text-green-600' : 'text-gray-400'}`}>
                          {progress.percent > 70 ? (
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                          ) : (
                            <div className="w-5 h-5 rounded-full border-2 border-current"></div>
                          )}
                          <span>Scraping des pages (15 scrapes)</span>
                        </div>

                        <div className={`flex items-center space-x-2 ${progress.step === 'llm' ? 'text-primary-600 font-medium' : progress.percent > 95 ? 'text-green-600' : 'text-gray-400'}`}>
                          {progress.percent > 95 ? (
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                          ) : (
                            <div className="w-5 h-5 rounded-full border-2 border-current"></div>
                          )}
                          <span>Analyse IA (GPT-4o)</span>
                        </div>
                      </div>

                      {/* Info temps estimé */}
                      <div className="pt-4 border-t border-gray-100">
                        <p className="text-xs text-gray-500 text-center">
                          💡 L'analyse v3 enrichie collecte et analyse 3x plus de données que la v2
                        </p>
                      </div>
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
