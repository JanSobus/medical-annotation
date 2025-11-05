import { useContext, useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { AnnotatorContext } from '../App'

interface Document {
  id: number
  title: string
  text: string
  created_at: string
  updated_at: string
}

interface Annotation {
  id: number
  document_id: number
  annotator_id: string
  status: string
  created_at: string
  updated_at: string
}

interface DocumentWithAnnotation extends Document {
  annotation?: Annotation
}

export default function Documents() {
  const context = useContext(AnnotatorContext)
  const navigate = useNavigate()
  const location = useLocation()
  const [documents, setDocuments] = useState<DocumentWithAnnotation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDocuments()
  }, [location.pathname])

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch('/api/v1/documents/')
      if (!response.ok) throw new Error('Failed to fetch documents')
      const docsData: Document[] = await response.json()
      
      // Fetch annotations for each document
      const docsWithAnnotations = await Promise.all(
        docsData.map(async (doc) => {
          try {
            // Try to fetch existing annotations for this document and user
            const annResponse = await fetch(`/api/v1/annotations/?document_id=${doc.id}&annotator_id=${context?.annotatorId || ''}`)
            
            if (annResponse.ok) {
              const annotations: Annotation[] = await annResponse.json()
              const userAnnotation = annotations.find(a => a.annotator_id === context?.annotatorId)
              
              if (userAnnotation) {
                return { ...doc, annotation: userAnnotation }
              }
            }
            
            // If no annotation exists, create one with NOT_STARTED status
            if (context?.annotatorId) {
              const createResponse = await fetch('/api/v1/annotations/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  document_id: doc.id,
                  annotator_id: context.annotatorId,
                  status: 'not_started',
                }),
              })
              
              if (createResponse.ok) {
                const newAnnotation: Annotation = await createResponse.json()
                return { ...doc, annotation: newAnnotation }
              }
            }
            
            return doc
          } catch (err) {
            console.error(`Error processing annotations for document ${doc.id}:`, err)
            return doc
          }
        })
      )
      
      setDocuments(docsWithAnnotations)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      console.error('Error fetching documents:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDocumentClick = (doc: DocumentWithAnnotation) => {
    // Update annotation status to IN_PROGRESS when clicking (fire and forget)
    if (doc.annotation && doc.annotation.status === 'not_started') {
      fetch(`/api/v1/annotations/${doc.annotation.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'in_progress' }),
      }).catch(err => console.error('Error updating annotation status:', err))
    }
    navigate(`/annotate/${doc.id}`)
  }

  const handleLogout = () => {
    if (context) {
      context.setAnnotatorId('')
      localStorage.removeItem('annotatorId')
      navigate('/')
    }
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    } catch {
      return 'Unknown'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'not_started':
        return 'bg-gray-100 text-gray-700'
      case 'in_progress':
        return 'bg-blue-100 text-blue-700'
      case 'completed':
        return 'bg-green-100 text-green-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'not_started':
        return 'Not Started'
      case 'in_progress':
        return 'In Progress'
      case 'completed':
        return 'Completed'
      default:
        return status
    }
  }

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto py-8 px-4">
        <div className="space-y-6">
          {/* Header */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
            <div className="flex justify-between items-start gap-6">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h1 className="text-3xl font-bold text-gray-900">Medical Annotation</h1>
                </div>
                <p className="text-gray-600 ml-13">
                  Annotate medical documents with entities and relationships
                </p>
                {context?.annotatorId && (
                  <div className="mt-3 inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 px-4 py-2 rounded-lg text-sm font-medium border border-indigo-200">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
                    </svg>
                    {context.annotatorId}
                  </div>
                )}
              </div>
              <button
                onClick={handleLogout}
                className="px-6 py-2 bg-gray-200 hover:bg-gray-300 text-gray-900 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 hover:shadow-md"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Logout
              </button>
            </div>
          </div>

          {/* Error State */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-2xl p-4 flex items-start gap-3">
              <svg className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="font-medium text-red-900">Error loading documents</p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Documents Grid */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Documents
            </h2>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="space-y-4 text-center">
                  <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-indigo-100 animate-pulse">
                    <svg className="w-6 h-6 text-indigo-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 2v20m0-20c4.418 0 8 3.582 8 8s-3.582 8-8 8-8-3.582-8-8 3.582-8 8-8z" />
                    </svg>
                  </div>
                  <p className="text-gray-600 font-medium">Loading documents...</p>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Add Document Tile */}
                <button
                  onClick={() => navigate('/add-document')}
                  className="group bg-white rounded-2xl shadow-lg border-2 border-dashed border-gray-300 hover:border-indigo-500 p-8 transition-all duration-300 hover:shadow-xl hover:scale-105 flex flex-col items-center justify-center min-h-[250px]"
                >
                  <div className="w-16 h-16 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-bold text-gray-900">Add Document</h3>
                  <p className="text-sm text-gray-600 mt-2">Create a new document</p>
                </button>

                {/* Document Tiles */}
                {documents.length > 0 ? (
                  documents.map((doc) => (
                    <button
                      key={doc.id}
                      onClick={() => handleDocumentClick(doc)}
                      className="group bg-white rounded-2xl shadow-lg border border-gray-200 hover:border-indigo-500 p-6 transition-all duration-300 hover:shadow-xl hover:scale-105 text-left flex flex-col min-h-[250px]"
                    >
                      {/* Status Badge */}
                      {doc.annotation && (
                        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-lg text-xs font-semibold mb-3 w-fit ${getStatusColor(doc.annotation.status)}`}>
                          <div className={`w-2 h-2 rounded-full ${doc.annotation.status === 'completed' ? 'bg-green-600' : doc.annotation.status === 'in_progress' ? 'bg-blue-600' : 'bg-gray-600'}`}></div>
                          {getStatusLabel(doc.annotation.status)}
                        </div>
                      )}

                      {/* Title */}
                      <h3 className="text-lg font-bold text-gray-900 group-hover:text-indigo-600 transition-colors line-clamp-3 mb-4">
                        {doc.title}
                      </h3>

                      {/* Preview Text */}
                      <p className="text-sm text-gray-600 line-clamp-4 mb-6 flex-grow">
                        {doc.text}
                      </p>

                      {/* Updated Date */}
                      <div className="flex items-center gap-2 pt-4 border-t border-gray-200">
                        <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="text-xs text-gray-500">
                          Updated {formatDate(doc.annotation?.updated_at || doc.updated_at)}
                        </span>
                      </div>
                    </button>
                  ))
                ) : (
                  <div className="col-span-full bg-gray-50 rounded-2xl border-2 border-dashed border-gray-300 p-12 text-center">
                    <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No documents yet</h3>
                    <p className="text-gray-600">Start by creating your first document using the Add Document tile above</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
