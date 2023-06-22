import { ObjectType } from 'pages/Database'

export const PROJECT_SLICE_NAME = 'project'

export type DatasetPostType = {
  folder_name: string
  sub_folders: { folder_name: string; source_image_ids: number[] }[]
  source_image_ids: number[]
}

export type DatasetType = {
  folder_name: string
  sub_folders: { folder_name: string; images: number[] }[]
  images: number[]
}

export type SubFolder = {
  folder_name: string
  id: string
  images?: {
    attributes: ObjectType
    id: number
    image_url: string
    parent_id: string
  }[]
  parent_id: string
  sub_folders?: SubFolder[]
}

export type Dataset = {
  dataset?: SubFolder[]
  project_id: string | null
  last_updated_time: string | null
}
