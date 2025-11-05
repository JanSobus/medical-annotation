import { type ReactElement } from 'react'
import type { Document, Entity, EntityType } from '../types/annotation'
import { getEntityColor } from '../constants/entityColors'

interface DocumentTextWithEntitiesProps {
  document: Document
  entities: Entity[]
  onEntityClick: (entity: Entity) => void
  onTextSelect: () => void
}

export function DocumentTextWithEntities({ 
  document, 
  entities, 
  onEntityClick,
  onTextSelect 
}: DocumentTextWithEntitiesProps) {
  const renderTextWithEntities = () => {
    if (!document) return null

    const sortedEntities = [...entities].sort((a, b) => a.start_char - b.start_char)
    const fragments: ReactElement[] = []
    let lastIndex = 0

    sortedEntities.forEach((entity, idx) => {
      // Add text before entity (but not the entity text itself)
      if (lastIndex < entity.start_char) {
        fragments.push(
          <span key={`text-${idx}`}>
            {document.text.substring(lastIndex, entity.start_char)}
          </span>
        )
      }

      // Add entity bubble - the button text IS the entity, so we skip the underlying text
      const type = entity.entity_type as EntityType
      fragments.push(
        <button
          key={`entity-${entity.id}`}
          onClick={() => onEntityClick(entity)}
          className={`inline-block px-2 py-1 rounded border cursor-pointer hover:opacity-75 transition-opacity font-semibold text-sm ${getEntityColor(type).bubble}`}
          title={`${type} (${entity.start_char}-${entity.end_char})`}
        >
          {entity.text}
        </button>
      )

      // Move index past the entity text - this skips rendering the underlying text for this entity
      lastIndex = entity.end_char
    })

    // Add remaining text after last entity
    if (lastIndex < document.text.length) {
      fragments.push(
        <span key="text-end">
          {document.text.substring(lastIndex)}
        </span>
      )
    }

    return fragments
  }

  return (
    <div className="border-b-2 border-gray-200 mb-8 pb-6">
      <p className="text-xs text-gray-500 mb-3">Highlight text to create entity • Click entity bubble to edit/delete</p>
      <div
        className="prose prose-sm max-w-none leading-relaxed text-base font-serif text-gray-700 select-text"
        onMouseUp={onTextSelect}
        onTouchEnd={onTextSelect}
      >
        {renderTextWithEntities()}
      </div>
    </div>
  )
}

