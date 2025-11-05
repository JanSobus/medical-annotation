import type { Entity, EntityType } from '../types/annotation'
import { getEntityColor } from '../constants/entityColors'

interface EntityListProps {
  entities: Entity[]
  aiExtracting: boolean
  onExtractWithAI: () => void
  onEditEntity: (entity: Entity, type: EntityType) => void
}

export function EntityList({ 
  entities, 
  aiExtracting, 
  onExtractWithAI, 
  onEditEntity 
}: EntityListProps) {
  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700">Entities ({entities.length})</h3>
        <button
          onClick={onExtractWithAI}
          disabled={aiExtracting}
          className={`text-xs px-3 py-1.5 rounded font-medium transition-colors ${
            aiExtracting
              ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
              : 'bg-purple-500 hover:bg-purple-600 text-white'
          }`}
        >
          {aiExtracting ? 'Extracting...' : '🤖 AI Extract'}
        </button>
      </div>
      <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
        {entities.length === 0 ? (
          <p className="text-xs text-gray-500 italic">No entities yet</p>
        ) : (
          entities.sort((a, b) => a.start_char - b.start_char).map(entity => {
            const type = entity.entity_type as EntityType
            const createdDate = new Date(entity.created_at).toLocaleDateString('en-US', { 
              month: 'short', 
              day: 'numeric', 
              hour: '2-digit', 
              minute: '2-digit'
            })
            const updatedDate = new Date(entity.updated_at).toLocaleDateString('en-US', { 
              month: 'short', 
              day: 'numeric', 
              hour: '2-digit', 
              minute: '2-digit'
            })
            return (
              <div key={entity.id} className={`p-3 rounded border ${getEntityColor(type).legend}`}>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className="font-semibold text-gray-900">{entity.text}</p>
                    <p className="text-xs text-gray-600">Type: {type} • Position: {entity.start_char}-{entity.end_char}</p>
                    <p className="text-xs text-gray-500 mt-2">
                      Created: {createdDate}
                    </p>
                    {entity.updated_at !== entity.created_at && (
                      <p className="text-xs text-gray-500">
                        Updated: {updatedDate}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() => onEditEntity(entity, type)}
                    className="text-xs px-2 py-1 bg-gray-300 hover:bg-gray-400 rounded transition-colors flex-shrink-0 ml-2"
                  >
                    Edit
                  </button>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

