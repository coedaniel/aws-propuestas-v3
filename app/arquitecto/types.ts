import { ArquitectoResponse as BaseArquitectoResponse } from '@/lib/api'

export interface GeneratedDocument {
  name: string
  url: string
  type: string
  size?: number
}

export interface ProjectState {
  name?: string
  type?: 'integral' | 'rapido'
  phase: 'inicio' | 'tipo' | 'recopilacion' | 'generacion' | 'entrega'
  data: any
}

export interface ArquitectoResponse extends Omit<BaseArquitectoResponse, 'projectState'> {
  projectName?: string
  documentsGenerated?: GeneratedDocument[]
  projectState?: ProjectState
}

export interface GeneratedProject {
  projectId: string
  projectName: string
  documentsGenerated: GeneratedDocument[]
}
