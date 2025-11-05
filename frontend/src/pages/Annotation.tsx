import { useContext, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { AnnotatorContext } from '../App'
import type { Document, Annotation, Entity, Relation, EntityType, RelationType } from '../types/annotation'
import { getStatusColor, getStatusLabel } from '../utils/statusHelpers'
import { EntityLegend } from '../components/EntityLegend'
import { DocumentTextWithEntities } from '../components/DocumentTextWithEntities'
import { CreateEntityModal } from '../components/modals/CreateEntityModal'
import { EditEntityModal } from '../components/modals/EditEntityModal'
import { CreateRelationModal } from '../components/modals/CreateRelationModal'
import { EditRelationModal } from '../components/modals/EditRelationModal'
import { EntityList } from '../components/EntityList'
import { RelationList } from '../components/RelationList'

export default function Annotation() {
  const { documentId } = useParams<{ documentId: string }>()
  const context = useContext(AnnotatorContext)
  const navigate = useNavigate()
  const [document, setDocument] = useState<Document | null>(null)
  const [annotation, setAnnotation] = useState<Annotation | null>(null)
  const [entities, setEntities] = useState<Entity[]>([])
  const [relations, setRelations] = useState<Relation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedText, setSelectedText] = useState<{ start: number; end: number; text: string } | null>(null)
  const [showCreateMenu, setShowCreateMenu] = useState(false)
  const [editingEntity, setEditingEntity] = useState<Entity | null>(null)
  const [showEditMenu, setShowEditMenu] = useState(false)
  const [newEntityType, setNewEntityType] = useState<EntityType>('DISEASE')
  const [showCreateRelationMenu, setShowCreateRelationMenu] = useState(false)
  const [editingRelation, setEditingRelation] = useState<Relation | null>(null)
  const [showEditRelationMenu, setShowEditRelationMenu] = useState(false)
  const [newRelationType, setNewRelationType] = useState<RelationType>('TREATS')
  const [selectedSourceEntity, setSelectedSourceEntity] = useState<number | null>(null)
  const [selectedTargetEntity, setSelectedTargetEntity] = useState<number | null>(null)
  const [editSourceEntity, setEditSourceEntity] = useState<number | null>(null)
  const [editTargetEntity, setEditTargetEntity] = useState<number | null>(null)
  const [aiExtracting, setAiExtracting] = useState(false)
  const [aiExtractingRelations, setAiExtractingRelations] = useState(false)

  useEffect(() => {
    if (!documentId) return
    fetchDocument()
  }, [documentId])

  useEffect(() => {
    if (annotation?.id) {
      fetchEntities()
      fetchRelations()
    }
  }, [annotation?.id])

  const fetchDocument = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(`/api/v1/documents/${documentId}`)
      if (!response.ok) throw new Error('Failed to fetch document')
      const data = await response.json()
      setDocument(data)

      // Fetch the annotation for this document and user
      if (context?.annotatorId) {
        const annResponse = await fetch(`/api/v1/annotations/?document_id=${documentId}&annotator_id=${context.annotatorId}`)
        if (annResponse.ok) {
          const annotations: Annotation[] = await annResponse.json()
          const userAnnotation = annotations.find(a => a.annotator_id === context.annotatorId)
          if (userAnnotation) {
            // If annotation status is NOT_STARTED, update it to IN_PROGRESS
            if (userAnnotation.status === 'not_started') {
              try {
                const updateResponse = await fetch(`/api/v1/annotations/${userAnnotation.id}`, {
                  method: 'PUT',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ status: 'in_progress' }),
                })
                if (updateResponse.ok) {
                  const updatedAnnotation: Annotation = await updateResponse.json()
                  setAnnotation(updatedAnnotation)
                } else {
                  setAnnotation(userAnnotation)
                }
              } catch (err) {
                console.error('Error updating annotation status:', err)
                setAnnotation(userAnnotation)
              }
            } else {
              setAnnotation(userAnnotation)
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      console.error('Error fetching document:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchEntities = async () => {
    if (!annotation?.id) return
    try {
      const response = await fetch(`/api/v1/entities/?annotation_id=${annotation.id}`)
      if (response.ok) {
        const data = await response.json()
        setEntities(data)
      }
    } catch (err) {
      console.error('Error fetching entities:', err)
    }
  }

  const fetchRelations = async () => {
    if (!annotation?.id) return
    try {
      const response = await fetch(`/api/v1/relations/?annotation_id=${annotation.id}`)
      if (response.ok) {
        const data = await response.json()
        setRelations(data)
      }
    } catch (err) {
      console.error('Error fetching relations:', err)
    }
  }

  const handleTextSelection = () => {
    const selection = window.getSelection()
    if (!selection || selection.toString().length === 0) return
    if (!document || !document.text) return

    const selectedText = selection.toString()
    const range = selection.getRangeAt(0)
    
    // Count characters from the startContainer's beginning to the selection start
    let charCountInNode = 0
    
    // If selection is in a text node, use startOffset directly
    if (range.startContainer.nodeType === Node.TEXT_NODE) {
      charCountInNode = range.startOffset
    }
    
    // Now find all occurrences of selectedText in the full document
    let startIndices: number[] = []
    let searchPos = 0
    
    while (true) {
      const idx = document.text.indexOf(selectedText, searchPos)
      if (idx === -1) break
      startIndices.push(idx)
      searchPos = idx + 1
    }
    
    if (startIndices.length === 0) {
      console.warn('Selected text not found in document:', selectedText)
      return
    }
    
    // If there's only one occurrence, use it
    if (startIndices.length === 1) {
      const start = startIndices[0]
      const end = start + selectedText.length
      setSelectedText({ start, end, text: selectedText })
      setShowCreateMenu(true)
      return
    }
    
    // For multiple occurrences, find which one is closest to the selection offset
    // The key insight: the selection's offset within its text node should match
    // the offset pattern in the full document text
    let bestIdx = startIndices[0]
    let closestDistance = Math.abs(startIndices[0] - charCountInNode)
    
    for (let idx of startIndices) {
      const distance = Math.abs(idx - charCountInNode)
      if (distance < closestDistance) {
        closestDistance = distance
        bestIdx = idx
      }
    }
    
    const start = bestIdx
    const end = start + selectedText.length

    console.log('Text selected:', { start, end, text: selectedText, charCountInNode, allOccurrences: startIndices })
    setSelectedText({ start, end, text: selectedText })
    setShowCreateMenu(true)
  }

  const updateEntity = async (entity: Entity, newType: EntityType) => {
    try {
      const url = `/api/v1/entities/${entity.id}`
      const body = {
        ...entity,
        entity_type: newType,
      }
      console.log('Updating entity:', { url, body })
      
      const response = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      console.log('Response status:', response.status)
      console.log('Response headers:', response.headers)
      
      if (response.ok) {
        const updated = await response.json()
        console.log('Updated entity:', updated)
        setEntities(entities.map(e => e.id === entity.id ? updated : e))
        
        // Refetch annotation to get updated timestamp
        if (annotation?.id) {
          const annResponse = await fetch(`/api/v1/annotations/${annotation.id}`)
          if (annResponse.ok) {
            const updatedAnnotation = await annResponse.json()
            setAnnotation(updatedAnnotation)
          }
        }
        
        setEditingEntity(null)
        setShowEditMenu(false)
      } else {
        console.error(`Update failed with status ${response.status}:`, await response.text())
      }
    } catch (err) {
      console.error('Error updating entity:', err)
    }
  }

  const createEntity = async (type: EntityType) => {
    if (!annotation || !selectedText || !document) return

    try {
      const response = await fetch('/api/v1/entities/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: selectedText.text,
          entity_type: type,
          start_char: selectedText.start,
          end_char: selectedText.end,
          confidence: 1.0,
          annotation_id: annotation.id,
        }),
      })

      if (response.ok) {
        const newEntity = await response.json()
        setEntities([...entities, newEntity])
        setSelectedText(null)
        setShowCreateMenu(false)
        
        // Refetch annotation to get updated timestamp
        if (annotation?.id) {
          const annResponse = await fetch(`/api/v1/annotations/${annotation.id}`)
          if (annResponse.ok) {
            const updatedAnnotation = await annResponse.json()
            setAnnotation(updatedAnnotation)
          }
        }
      }
    } catch (err) {
      console.error('Error creating entity:', err)
    }
  }

  const deleteEntity = async (entity: Entity) => {
    try {
      const response = await fetch(`/api/v1/entities/${entity.id}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        setEntities(entities.filter(e => e.id !== entity.id))
        setEditingEntity(null)
        setShowEditMenu(false)
        
        // Refetch annotation to get updated timestamp
        if (annotation?.id) {
          const annResponse = await fetch(`/api/v1/annotations/${annotation.id}`)
          if (annResponse.ok) {
            const updatedAnnotation = await annResponse.json()
            setAnnotation(updatedAnnotation)
          }
        }
      }
    } catch (err) {
      console.error('Error deleting entity:', err)
    }
  }

  const extractEntitiesWithAI = async () => {
    if (!document || !annotation) return

    setAiExtracting(true)
    try {
      // Call the AI extraction endpoint
      const response = await fetch(`/api/v1/documents/${document.id}/extract-entities`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error(`AI extraction failed: ${response.statusText}`)
      }

      const result = await response.json()
      const extractedEntities = result.entities || []

      console.log(`AI extracted ${extractedEntities.length} entities`)

      // Filter out entities that overlap with existing entities
      const nonOverlappingEntities = extractedEntities.filter((extracted: any) => {
        return !entities.some(existing => {
          // Check if there's any overlap
          const overlaps = 
            (extracted.start_char >= existing.start_char && extracted.start_char < existing.end_char) ||
            (extracted.end_char > existing.start_char && extracted.end_char <= existing.end_char) ||
            (extracted.start_char <= existing.start_char && extracted.end_char >= existing.end_char)
          return overlaps
        })
      })

      console.log(`${nonOverlappingEntities.length} non-overlapping entities to save`)

      // Save non-overlapping entities to the database
      const savedEntities: Entity[] = []
      for (const entity of nonOverlappingEntities) {
        try {
          const saveResponse = await fetch('/api/v1/entities/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              text: entity.text,
              entity_type: entity.entity_type,
              start_char: entity.start_char,
              end_char: entity.end_char,
              confidence: entity.confidence,
              annotation_id: annotation.id,
            }),
          })

          if (saveResponse.ok) {
            const savedEntity = await saveResponse.json()
            savedEntities.push(savedEntity)
          }
        } catch (err) {
          console.error('Error saving extracted entity:', err)
        }
      }

      // Update entities list with newly saved entities
      if (savedEntities.length > 0) {
        setEntities([...entities, ...savedEntities])
        
        // Refetch annotation to get updated timestamp
        if (annotation?.id) {
          const annResponse = await fetch(`/api/v1/annotations/${annotation.id}`)
          if (annResponse.ok) {
            const updatedAnnotation = await annResponse.json()
            setAnnotation(updatedAnnotation)
          }
        }

        console.log(`Successfully saved ${savedEntities.length} new entities`)
      }

      if (extractedEntities.length === 0) {
        alert('AI did not extract any entities from this document.')
      } else if (savedEntities.length === 0) {
        alert('All AI-extracted entities overlap with existing entities.')
      } else {
        alert(`Successfully added ${savedEntities.length} new entities from AI extraction!`)
      }
    } catch (err) {
      console.error('Error during AI extraction:', err)
      alert(`AI extraction failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setAiExtracting(false)
    }
  }

  const extractRelationsWithAI = async () => {
    if (!annotation || entities.length === 0) {
      alert('Need at least some entities to extract relations.')
      return
    }

    setAiExtractingRelations(true)
    try {
      // Call the AI relation extraction endpoint
      const response = await fetch(`/api/v1/annotations/${annotation.id}/extract-relations`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error(`AI relation extraction failed: ${response.statusText}`)
      }

      const result = await response.json()
      const extractedRelations = result.relations || []

      console.log(`AI extracted ${extractedRelations.length} relations`)

      // Filter out relations that already exist
      const newRelations = extractedRelations.filter((extracted: any) => {
        return !relations.some(existing => 
          existing.source_entity_id === extracted.source_entity_id &&
          existing.target_entity_id === extracted.target_entity_id &&
          existing.relation_type === extracted.relation_type
        )
      })

      console.log(`${newRelations.length} new relations to save`)

      // Save new relations to the database
      const savedRelations: Relation[] = []
      for (const relation of newRelations) {
        try {
          const saveResponse = await fetch('/api/v1/relations/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              relation_type: relation.relation_type,
              source_entity_id: relation.source_entity_id,
              target_entity_id: relation.target_entity_id,
              confidence: relation.confidence,
              annotation_id: annotation.id,
            }),
          })

          if (saveResponse.ok) {
            const savedRelation = await saveResponse.json()
            savedRelations.push(savedRelation)
          }
        } catch (err) {
          console.error('Error saving extracted relation:', err)
        }
      }

      // Update relations list with newly saved relations
      if (savedRelations.length > 0) {
        setRelations([...relations, ...savedRelations])
        
        // Refetch annotation to get updated timestamp
        if (annotation?.id) {
          const annResponse = await fetch(`/api/v1/annotations/${annotation.id}`)
          if (annResponse.ok) {
            const updatedAnnotation = await annResponse.json()
            setAnnotation(updatedAnnotation)
          }
        }

        console.log(`Successfully saved ${savedRelations.length} new relations`)
      }

      if (extractedRelations.length === 0) {
        alert('AI did not extract any relations from this annotation.')
      } else if (savedRelations.length === 0) {
        alert('All AI-extracted relations already exist.')
      } else {
        alert(`Successfully added ${savedRelations.length} new relations from AI extraction!`)
      }
    } catch (err) {
      console.error('Error during AI relation extraction:', err)
      alert(`AI relation extraction failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setAiExtractingRelations(false)
    }
  }

  const createRelation = async () => {
    if (!annotation || selectedSourceEntity === null || selectedTargetEntity === null) return

    try {
      const response = await fetch('/api/v1/relations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          relation_type: newRelationType,
          source_entity_id: selectedSourceEntity,
          target_entity_id: selectedTargetEntity,
          confidence: 1.0,
          annotation_id: annotation.id,
        }),
      })

      if (response.ok) {
        const newRelation = await response.json()
        setRelations([...relations, newRelation])
        setShowCreateRelationMenu(false)
        setSelectedSourceEntity(null)
        setSelectedTargetEntity(null)
        setNewRelationType('TREATS')

        // Refetch annotation to get updated timestamp
        if (annotation?.id) {
          const annResponse = await fetch(`/api/v1/annotations/${annotation.id}`)
          if (annResponse.ok) {
            const updatedAnnotation = await annResponse.json()
            setAnnotation(updatedAnnotation)
          }
        }
      }
    } catch (err) {
      console.error('Error creating relation:', err)
    }
  }

  const updateRelation = async (relation: Relation | null, newType: RelationType) => {
    if (!relation) {
      console.error('No relation to update')
      return
    }

    try {
      const url = `/api/v1/relations/${relation.id}`
      const body = {
        relation_type: newType,
        source_entity_id: editSourceEntity !== null ? editSourceEntity : relation.source_entity_id,
        target_entity_id: editTargetEntity !== null ? editTargetEntity : relation.target_entity_id,
        confidence: relation.confidence,
        annotation_id: relation.annotation_id,
      }

      console.log('Updating relation:', { url, body })

      const response = await fetch(url, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      console.log('Response status:', response.status)

      if (response.ok) {
        const updated = await response.json()
        console.log('Updated relation:', updated)
        setRelations(relations.map(r => r.id === relation.id ? updated : r))

        // Refetch annotation to get updated timestamp
        if (annotation?.id) {
          const annResponse = await fetch(`/api/v1/annotations/${annotation.id}`)
          if (annResponse.ok) {
            const updatedAnnotation = await annResponse.json()
            setAnnotation(updatedAnnotation)
          }
        }

        setEditingRelation(null)
        setShowEditRelationMenu(false)
      } else {
        console.error(`Update failed with status ${response.status}:`, await response.text())
      }
    } catch (err) {
      console.error('Error updating relation:', err)
    }
  }

  const deleteRelation = async (relation: Relation) => {
    try {
      const response = await fetch(`/api/v1/relations/${relation.id}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        setRelations(relations.filter(r => r.id !== relation.id))
        setEditingRelation(null)
        setShowEditRelationMenu(false)

        // Refetch annotation to get updated timestamp
        if (annotation?.id) {
          const annResponse = await fetch(`/api/v1/annotations/${annotation.id}`)
          if (annResponse.ok) {
            const updatedAnnotation = await annResponse.json()
            setAnnotation(updatedAnnotation)
          }
        }
      }
    } catch (err) {
      console.error('Error deleting relation:', err)
    }
  }

  const getEntityText = (entityId: number): string => {
    const entity = entities.find(e => e.id === entityId)
    return entity ? entity.text : 'Unknown'
  }



  const handleMarkCompleted = async () => {
    if (annotation) {
      try {
        const response = await fetch(`/api/v1/annotations/${annotation.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'completed' }),
        })
        if (response.ok) {
          const updatedAnnotation: Annotation = await response.json()
          setAnnotation(updatedAnnotation)
        }
      } catch (err) {
        console.error('Error marking annotation as completed:', err)
      }
    }
  }

  if (loading) {
    return (
      <div className="w-full min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <div className="space-y-4 text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-indigo-100 animate-pulse">
            <svg className="w-6 h-6 text-indigo-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 2v20m0-20c4.418 0 8 3.582 8 8s-3.582 8-8 8-8-3.582-8-8 3.582-8 8-8z" />
            </svg>
          </div>
          <p className="text-gray-600 font-medium">Loading document...</p>
        </div>
      </div>
    )
  }

  if (error || !document) {
    return (
      <div className="w-full min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md text-center">
          <svg className="w-16 h-16 text-red-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Error Loading Document</h2>
          <p className="text-gray-600 mb-6">{error || 'Document not found'}</p>
          <button
            onClick={() => navigate('/documents')}
            className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors"
          >
            Back to Documents
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto py-8 px-4">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200 mb-6">
          <div className="flex justify-between items-start gap-6">
            <div className="flex-1">
              <button
                onClick={() => navigate('/documents')}
                className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-700 mb-3 font-medium"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Back to Documents
              </button>
              <h1 className="text-3xl font-bold text-gray-900">{document.title}</h1>
              {context?.annotatorId && (
                <div className="mt-3 inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 px-4 py-2 rounded-lg text-sm font-medium border border-indigo-200">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" />
                  </svg>
                  {context.annotatorId}
                </div>
              )}
            </div>

            {/* Right side: Status and Mark Completed Button */}
            <div className="flex items-center gap-4">
              {/* Status Info */}
              {annotation && (
                <div>
                  <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold ${getStatusColor(annotation.status)}`}>
                    <div className={`w-2 h-2 rounded-full ${annotation.status === 'completed' ? 'bg-green-600' : annotation.status === 'in_progress' ? 'bg-blue-600' : 'bg-gray-600'}`}></div>
                    {getStatusLabel(annotation.status)}
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    Updated: {new Date(annotation.updated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              )}

              {/* Mark Completed Button */}
              {annotation && annotation.status !== 'completed' && (
                <button
                  onClick={handleMarkCompleted}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-all duration-200 flex-shrink-0"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Mark Completed
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Document Content with Entities */}
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
          <EntityLegend />

          {document && (
            <DocumentTextWithEntities
              document={document}
              entities={entities}
              onEntityClick={(entity) => {
                setEditingEntity(entity)
                setNewEntityType(entity.entity_type as EntityType)
                setShowEditMenu(true)
              }}
              onTextSelect={handleTextSelection}
            />
          )}

          {/* Two-column layout: Entities and Relations */}
          <div className="grid grid-cols-2 gap-8">
            {/* Entity List */}
            <EntityList
              entities={entities}
              aiExtracting={aiExtracting}
              onExtractWithAI={extractEntitiesWithAI}
              onEditEntity={(entity, type) => {
                setEditingEntity(entity)
                setNewEntityType(type)
                setShowEditMenu(true)
              }}
            />

            {/* Relations List */}
            <RelationList
              relations={relations}
              entities_length={entities.length}
              aiExtractingRelations={aiExtractingRelations}
              onExtractWithAI={extractRelationsWithAI}
              onAddRelation={() => {
                setSelectedSourceEntity(null)
                setSelectedTargetEntity(null)
                setNewRelationType('TREATS')
                setShowCreateRelationMenu(true)
              }}
              onEditRelation={(relation, type, sourceId, targetId) => {
                setEditingRelation(relation)
                setNewRelationType(type)
                setEditSourceEntity(sourceId)
                setEditTargetEntity(targetId)
                setShowEditRelationMenu(true)
              }}
              getEntityText={getEntityText}
            />
          </div>
        </div>
      </div>

      {/* Create Entity Menu */}
      {showCreateMenu && selectedText && (
        <CreateEntityModal
          selectedText={selectedText.text}
          entityType={newEntityType}
          onTypeChange={setNewEntityType}
          onCancel={() => {
            setShowCreateMenu(false)
            setSelectedText(null)
          }}
          onCreate={() => createEntity(newEntityType)}
        />
      )}

      {/* Edit Entity Menu */}
      {showEditMenu && editingEntity && (
        <EditEntityModal
          entity={editingEntity}
          entityType={newEntityType}
          onTypeChange={setNewEntityType}
          onDelete={() => deleteEntity(editingEntity)}
          onCancel={() => {
            setShowEditMenu(false)
            setEditingEntity(null)
          }}
          onSave={() => updateEntity(editingEntity, newEntityType)}
        />
      )}

      {/* Create Relation Menu */}
      {showCreateRelationMenu && (
        <CreateRelationModal
          entities={entities}
          sourceEntityId={selectedSourceEntity}
          targetEntityId={selectedTargetEntity}
          relationType={newRelationType}
          onSourceChange={setSelectedSourceEntity}
          onTargetChange={setSelectedTargetEntity}
          onTypeChange={setNewRelationType}
          onCancel={() => {
            setShowCreateRelationMenu(false)
            setSelectedSourceEntity(null)
            setSelectedTargetEntity(null)
          }}
          onSave={() => createRelation()}
        />
      )}

      {/* Edit Relation Menu */}
      {showEditRelationMenu && editingRelation && (
        <EditRelationModal
          relation={editingRelation}
          entities={entities}
          sourceEntityId={editSourceEntity}
          targetEntityId={editTargetEntity}
          relationType={newRelationType}
          onSourceChange={setEditSourceEntity}
          onTargetChange={setEditTargetEntity}
          onTypeChange={setNewRelationType}
          onDelete={() => deleteRelation(editingRelation)}
          onCancel={() => {
            setShowEditRelationMenu(false)
            setEditingRelation(null)
            setEditSourceEntity(null)
            setEditTargetEntity(null)
          }}
          onSave={() => updateRelation(editingRelation, newRelationType)}
        />
      )}
    </div>
  )
}
