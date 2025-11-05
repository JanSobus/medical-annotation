import type { Entity, Relation, RelationType } from '../../types/annotation'
import { RELATION_TYPES } from '../../constants/relationTypes'

interface EditRelationModalProps {
  relation: Relation
  entities: Entity[]
  sourceEntityId: number | null
  targetEntityId: number | null
  relationType: RelationType
  onSourceChange: (entityId: number | null) => void
  onTargetChange: (entityId: number | null) => void
  onTypeChange: (type: RelationType) => void
  onDelete: () => void
  onCancel: () => void
  onSave: () => void
}

export function EditRelationModal({
  relation: _relation,
  entities,
  sourceEntityId,
  targetEntityId,
  relationType,
  onSourceChange,
  onTargetChange,
  onTypeChange,
  onDelete,
  onCancel,
  onSave
}: EditRelationModalProps) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Edit Relation</h3>

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Source Entity</label>
            <select
              value={sourceEntityId || ''}
              onChange={(e) => onSourceChange(e.target.value ? parseInt(e.target.value) : null)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Select source entity...</option>
              {entities.map(entity => (
                <option key={entity.id} value={entity.id}>
                  {entity.text} ({entity.entity_type})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Relation Type</label>
            <div className="grid grid-cols-2 gap-2">
              {RELATION_TYPES.map(type => (
                <button
                  key={type}
                  onClick={() => onTypeChange(type)}
                  className={`py-2 px-3 rounded font-semibold text-xs transition-all cursor-pointer border ${
                    relationType === type
                      ? 'bg-indigo-600 text-white border-indigo-700'
                      : 'bg-gray-100 text-gray-900 border-gray-300 hover:bg-gray-200'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Target Entity</label>
            <select
              value={targetEntityId || ''}
              onChange={(e) => onTargetChange(e.target.value ? parseInt(e.target.value) : null)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Select target entity...</option>
              {entities.map(entity => (
                <option key={entity.id} value={entity.id}>
                  {entity.text} ({entity.entity_type})
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onDelete}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors"
          >
            Delete
          </button>
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-900 font-medium rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onSave}
            className="flex-1 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  )
}

