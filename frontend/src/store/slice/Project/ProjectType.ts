export const PROJECT_SLICE_NAME = 'project'

export enum ProjectTypeValue {
  FACTOR = 0,
  WITHIN_FACTOR = 1,
}

export type CurrentProject = {
  id: string
  created_time: string
  image_count: number
  project_name: string
  project_type: ProjectTypeValue
  updated_time: string
}

export type Project = {
  projects: ProjectType[]
  loading: boolean
  currentProject?: CurrentProject
}

export type ProjectCreate = {
  project_name: string
  project_type: ProjectTypeValue
}

export type ProjectType = {
  id: number | string
  uid?: number | string
  created_time: string
  updated_time: string
  role?: string | number
  image_count: number
} & ProjectCreate
