export const PROJECT_SLICE_NAME = 'project'

export type Project = {
  projects: ProjectType[]
  currentProject?: {
    id: string
  }
}

export type ProjectType = {
  id: number | string
  uid?: number | string
  name: string
  project_type: number
  image_count: number
  created_time: string
  updated_time: string
  role?: string | number
}
