import type { Relation, RelationType } from '../types/annotation'

interface RelationListProps {
  relations: Relation[]
  entities_length: number
  aiExtractingRelations: boolean
  onExtractWithAI: () => void
  onAddRelation: () => void
  onEditRelation: (relation: Relation, type: RelationType, sourceId: number, targetId: number) => void
  getEntityText: (entityId: number) => string
}

export function RelationList({ 
  relations, 
  entities_length,
  aiExtractingRelations, 
  onExtractWithAI, 
  onAddRelation,
  onEditRelation,
  getEntityText
}: RelationListProps) {
  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700">Relations ({relations.length})</h3>
        <div className="flex gap-2">
          <button
            onClick={onExtractWithAI}
            disabled={aiExtractingRelations || entities_length === 0}
            className={`text-xs px-3 py-1.5 rounded font-medium transition-colors ${
              aiExtractingRelations || entities_length === 0
                ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                : 'bg-purple-500 hover:bg-purple-600 text-white'
            }`}
            title={entities_length === 0 ? 'Add some entities first' : 'Extract relations using AI'}
          >
            {aiExtractingRelations ? 'Extracting...' : '🤖 AI Extract'}
          </button>
          <button
            onClick={onAddRelation}
            className="text-xs px-2 py-1 bg-blue-500 hover:bg-blue-600 text-white rounded transition-colors"
          >
            + Add Relation
          </button>
        </div>
      </div>
      <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
        {relations.length === 0 ? (
          <p className="text-xs text-gray-500 italic">No relations yet</p>
        ) : (
          relations.map(relation => (
            <div key={relation.id} className="p-3 rounded border border-gray-300 bg-gray-50">
              <div className="flex justify-between items-start">
                <div className="flex-1 text-xs">
                  <p className="font-semibold text-gray-900">
                    {getEntityText(relation.source_entity_id)} → {relation.relation_type} → {getEntityText(relation.target_entity_id)}
                  </p>
                  <p className="text-gray-600 mt-1">
                    Confidence: {(relation.confidence * 100).toFixed(0)}%
                  </p>
                  <p className="text-gray-600">
                    Created: {new Date(relation.created_at).toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric', 
                      hour: '2-digit', 
                      minute: '2-digit'
                    })}
                  </p>
                  {relation.updated_at !== relation.created_at && (
                    <p className="text-gray-600">
                      Updated: {new Date(relation.updated_at).toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        hour: '2-digit', 
                        minute: '2-digit'
                      })}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => onEditRelation(
                    relation, 
                    relation.relation_type as RelationType,
                    relation.source_entity_id,
                    relation.target_entity_id
                  )}
                  className="text-xs px-2 py-1 bg-gray-300 hover:bg-gray-400 rounded transition-colors flex-shrink-0 ml-2"
                >
                  Edit
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

