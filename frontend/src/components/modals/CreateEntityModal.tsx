import type { EntityType } from '../../types/annotation'
import { ENTITY_TYPES, getEntityColor } from '../../constants/entityColors'

interface CreateEntityModalProps {
  selectedText: string
  entityType: EntityType
  onTypeChange: (type: EntityType) => void
  onCancel: () => void
  onCreate: () => void
}

export function CreateEntityModal({
  selectedText,
  entityType,
  onTypeChange,
  onCancel,
  onCreate
}: CreateEntityModalProps) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Create Entity</h3>
        <p className="text-sm text-gray-600 mb-4">
          Selected text: <span className="font-semibold">"{selectedText}"</span>
        </p>

        <div className="space-y-3 mb-6">
          <label className="block text-sm font-medium text-gray-700">Entity Type</label>
          <div className="grid grid-cols-2 gap-2">
            {ENTITY_TYPES.map(type => {
              const isSelected = entityType === type
              const colorClasses = getEntityColor(type).legend
              return (
                <button
                  key={type}
                  onClick={() => onTypeChange(type)}
                  className={`py-3 px-3 rounded font-semibold text-sm transition-all cursor-pointer ${
                    isSelected
                      ? `${colorClasses} ring-2 ring-offset-2 ring-gray-900`
                      : `${colorClasses} opacity-60 hover:opacity-100`
                  }`}
                >
                  {type}
                </button>
              )
            })}
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-900 font-medium rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onCreate}
            className="flex-1 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors"
          >
            Create Entity
          </button>
        </div>
      </div>
    </div>
  )
}

