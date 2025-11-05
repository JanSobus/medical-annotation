export interface Document {
  id: number
  title: string
  text: string
  created_at: string
  updated_at: string
}

export interface Annotation {
  id: number
  document_id: number
  annotator_id: string
  status: string
  created_at: string
  updated_at: string
}

export interface Entity {
  id: number
  text: string
  entity_type: string
  start_char: number
  end_char: number
  confidence: number
  annotation_id: number
  created_at: string
  updated_at: string
}

export interface Relation {
  id: number
  relation_type: string
  source_entity_id: number
  target_entity_id: number
  confidence: number
  annotation_id: number
  created_at: string
  updated_at: string
}

export type EntityType = 'DISEASE' | 'MEDICATION' | 'SYMPTOM' | 'PROCEDURE' | 'ANATOMY' | 'LAB_VALUE' | 'DOSAGE' | 'OTHER'

export type RelationType = 'TREATS' | 'CAUSES' | 'HAS_SYMPTOM' | 'INDICATES' | 'CONTRAINDICATES' | 'DOSAGE_FOR' | 'LOCATED_IN' | 'TEMPORAL' | 'OTHER'

