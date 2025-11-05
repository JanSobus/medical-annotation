import type { EntityType } from '../types/annotation'

export const ENTITY_TYPES: EntityType[] = ['DISEASE', 'MEDICATION', 'SYMPTOM', 'PROCEDURE', 'ANATOMY', 'LAB_VALUE', 'DOSAGE', 'OTHER']

export const ENTITY_COLORS: Record<EntityType, { bubble: string; legend: string }> = {
  DISEASE: { bubble: 'bg-red-300 text-red-950 border border-red-500', legend: 'bg-red-200 border-2 border-red-400' },
  MEDICATION: { bubble: 'bg-blue-300 text-blue-950 border border-blue-500', legend: 'bg-blue-200 border-2 border-blue-400' },
  SYMPTOM: { bubble: 'bg-yellow-300 text-yellow-950 border border-yellow-500', legend: 'bg-yellow-200 border-2 border-yellow-400' },
  PROCEDURE: { bubble: 'bg-green-300 text-green-950 border border-green-500', legend: 'bg-green-200 border-2 border-green-400' },
  ANATOMY: { bubble: 'bg-pink-300 text-pink-950 border border-pink-500', legend: 'bg-pink-200 border-2 border-pink-400' },
  LAB_VALUE: { bubble: 'bg-purple-300 text-purple-950 border border-purple-500', legend: 'bg-purple-200 border-2 border-purple-400' },
  DOSAGE: { bubble: 'bg-orange-300 text-orange-950 border border-orange-500', legend: 'bg-orange-200 border-2 border-orange-400' },
  OTHER: { bubble: 'bg-gray-300 text-gray-950 border border-gray-500', legend: 'bg-gray-200 border-2 border-gray-400' },
}

export const ENTITY_COLORS_LEGEND: Record<EntityType, string> = {
  DISEASE: 'bg-red-200 border-2 border-red-400',
  MEDICATION: 'bg-blue-200 border-2 border-blue-400',
  SYMPTOM: 'bg-yellow-200 border-2 border-yellow-400',
  PROCEDURE: 'bg-green-200 border-2 border-green-400',
  ANATOMY: 'bg-pink-200 border-2 border-pink-400',
  LAB_VALUE: 'bg-purple-200 border-2 border-purple-400',
  DOSAGE: 'bg-orange-200 border-2 border-orange-400',
  OTHER: 'bg-gray-200 border-2 border-gray-400',
}

export const getEntityColor = (type: string): { bubble: string; legend: string } => {
  const normalizedType = type.toUpperCase() as EntityType
  return ENTITY_COLORS[normalizedType] || { 
    bubble: 'bg-gray-300 text-gray-950 border border-gray-500', 
    legend: 'bg-gray-200 border-2 border-gray-400' 
  }
}

