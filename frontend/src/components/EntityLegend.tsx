import { ENTITY_TYPES, ENTITY_COLORS_LEGEND } from '../constants/entityColors'

export function EntityLegend() {
  return (
    <div className="mb-6">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">Entity Legend</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-8 gap-2">
        {ENTITY_TYPES.map(type => (
          <div key={type} className={`px-3 py-2 rounded text-sm font-medium text-center text-gray-900 ${ENTITY_COLORS_LEGEND[type]}`}>
            {type}
          </div>
        ))}
      </div>
    </div>
  )
}

