const ProfileResults = ({ profile }) => {
  if (!profile) return null;

  return (
    <div className="w-full max-w-4xl mx-auto mt-8">
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-8 py-6">
          <h2 className="text-3xl font-bold text-white">{profile.full_name}</h2>
          {profile.current_position && (
            <p className="text-primary-100 mt-2 text-lg">
              {profile.current_position}
              {profile.company && ` chez ${profile.company}`}
            </p>
          )}
        </div>

        <div className="p-8 space-y-6">
          {profile.summary && (
            <div className="bg-blue-50 border-l-4 border-primary-500 p-4 rounded">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Résumé</h3>
              <p className="text-gray-700 leading-relaxed">{profile.summary}</p>
            </div>
          )}

          {profile.professional_experience && profile.professional_experience.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                <svg className="w-6 h-6 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                Expérience Professionnelle
              </h3>
              <div className="space-y-4">
                {profile.professional_experience.map((exp, index) => (
                  <div key={index} className="border-l-2 border-gray-300 pl-4 pb-4">
                    <h4 className="font-semibold text-gray-800">{exp.position}</h4>
                    <p className="text-primary-600">{exp.company}</p>
                    {exp.period && (
                      <p className="text-sm text-gray-500">{exp.period}</p>
                    )}
                    {exp.description && (
                      <p className="text-gray-600 mt-2">{exp.description}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {profile.skills && profile.skills.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                <svg className="w-6 h-6 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
                Compétences
              </h3>
              <div className="flex flex-wrap gap-2">
                {profile.skills.map((skill, index) => (
                  <span
                    key={index}
                    className="bg-primary-100 text-primary-800 px-3 py-1 rounded-full text-sm font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {profile.publications && profile.publications.length > 0 && (
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                <svg className="w-6 h-6 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
                Publications & Interventions
              </h3>
              <ul className="list-disc list-inside space-y-2 text-gray-700">
                {profile.publications.map((pub, index) => (
                  <li key={index}>{pub}</li>
                ))}
              </ul>
            </div>
          )}

          {profile.public_contact && (
            <div>
              <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
                <svg className="w-6 h-6 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                Contact Public
              </h3>
              <div className="space-y-2 text-gray-700">
                {profile.public_contact.email && (
                  <p>
                    <span className="font-medium">Email:</span>{' '}
                    <a href={`mailto:${profile.public_contact.email}`} className="text-primary-600 hover:underline">
                      {profile.public_contact.email}
                    </a>
                  </p>
                )}
                {profile.public_contact.phone && (
                  <p>
                    <span className="font-medium">Téléphone:</span> {profile.public_contact.phone}
                  </p>
                )}
                {profile.public_contact.linkedin && (
                  <p>
                    <span className="font-medium">LinkedIn:</span>{' '}
                    <a
                      href={profile.public_contact.linkedin}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary-600 hover:underline"
                    >
                      Voir le profil
                    </a>
                  </p>
                )}
              </div>
            </div>
          )}

          {profile.linkedin_url && !profile.public_contact?.linkedin && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <a
                href={profile.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center text-primary-600 hover:text-primary-700 font-medium"
              >
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                </svg>
                Voir le profil LinkedIn
              </a>
            </div>
          )}

          {profile.sources && profile.sources.length > 0 && (
            <div className="pt-6 border-t border-gray-200">
              <details className="cursor-pointer">
                <summary className="text-sm font-medium text-gray-600 hover:text-gray-800">
                  Sources utilisées ({profile.sources.length})
                </summary>
                <ul className="mt-3 space-y-1 text-sm text-gray-600">
                  {profile.sources.map((source, index) => (
                    <li key={index} className="truncate">
                      <a
                        href={source}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:underline"
                      >
                        {source}
                      </a>
                    </li>
                  ))}
                </ul>
              </details>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileResults;
