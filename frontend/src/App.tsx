import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, createContext } from 'react'
import Landing from './pages/Landing'
import Documents from './pages/Documents'
import Annotation from './pages/Annotation'
import AddDocument from './pages/AddDocument'

export const AnnotatorContext = createContext<{
  annotatorId: string | null
  setAnnotatorId: (id: string) => void
} | null>(null)

export default function App() {
  const [annotatorId, setAnnotatorId] = useState<string | null>(
    localStorage.getItem('annotatorId')
  )

  const handleSetAnnotatorId = (id: string) => {
    setAnnotatorId(id)
    localStorage.setItem('annotatorId', id)
  }

  return (
    <AnnotatorContext.Provider value={{ annotatorId, setAnnotatorId: handleSetAnnotatorId }}>
      <Router>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route
            path="/documents"
            element={annotatorId ? <Documents /> : <Navigate to="/" />}
          />
          <Route
            path="/annotate/:documentId"
            element={annotatorId ? <Annotation /> : <Navigate to="/" />}
          />
          <Route
            path="/add-document"
            element={annotatorId ? <AddDocument /> : <Navigate to="/" />}
          />
        </Routes>
      </Router>
    </AnnotatorContext.Provider>
  )
}
