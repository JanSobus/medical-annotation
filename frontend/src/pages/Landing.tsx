import { useState, useContext } from 'react'
import { useNavigate } from 'react-router-dom'
import { AnnotatorContext } from '../App'

export default function Landing() {
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  const context = useContext(AnnotatorContext)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!name.trim()) {
      setError('Please enter your name')
      return
    }

    setIsLoading(true)
    // Simulate loading for better UX
    setTimeout(() => {
      if (context) {
        context.setAnnotatorId(name.trim())
        navigate('/documents')
      }
    }, 500)
  }

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center px-4 py-12">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-0 w-96 h-96 bg-white/10 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl translate-x-1/2 translate-y-1/2"></div>
      </div>

      <div className="w-full max-w-md space-y-8 relative z-10">
        {/* Logo/Icon Area */}
        <div className="flex justify-center">
          <div className="w-20 h-20 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white/30 shadow-2xl">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>

        {/* Welcome Banner */}
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold text-white drop-shadow-lg leading-tight">
            Medical Annotation
          </h1>
          <h2 className="text-2xl font-semibold text-white/90 drop-shadow-md">
            Tool
          </h2>
          <div className="h-1 w-16 bg-white/60 mx-auto rounded-full"></div>
          <p className="text-lg text-white/80 font-medium">
            Annotate with precision
          </p>
          <p className="text-sm text-white/70">
            Build high-quality training data by annotating medical documents with entities and relationships
          </p>
        </div>

        {/* Form Card */}
        <form onSubmit={handleSubmit} className="bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl p-8 space-y-6 border border-white/20">
          <div>
            <label htmlFor="name" className="block text-sm font-semibold text-gray-800 mb-3 uppercase tracking-wide">
              Annotator Name
            </label>
            <div className="relative">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => {
                  setName(e.target.value)
                  setError('')
                }}
                placeholder="Your name"
                className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 bg-gray-50/50"
                disabled={isLoading}
              />
            </div>
            {error && (
              <div className="flex items-center gap-2 text-sm text-red-600 mt-3 p-2 bg-red-50 rounded-lg">
                <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                {error}
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-400 text-white font-bold py-3 px-4 rounded-lg transition-all duration-200 ease-in-out transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 2v20m0-20c-4.418 0-8 3.582-8 8s3.582 8 8 8 8-3.582 8-8-3.582-8-8-8z" />
                </svg>
                Starting...
              </>
            ) : (
              <>
                Start Annotating
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </>
            )}
          </button>
        </form>

        {/* Features */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20 text-center">
            <div className="text-2xl mb-2">📋</div>
            <p className="text-sm font-medium text-white">Multiple Documents</p>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20 text-center">
            <div className="text-2xl mb-2">🏷️</div>
            <p className="text-sm font-medium text-white">Entity Tagging</p>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20 text-center">
            <div className="text-2xl mb-2">🔗</div>
            <p className="text-sm font-medium text-white">Relations</p>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20 text-center">
            <div className="text-2xl mb-2">✨</div>
            <p className="text-sm font-medium text-white">High Quality</p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-white/70">
          <p>Your name will be stored as your unique annotator ID</p>
        </div>
      </div>
    </div>
  )
}
