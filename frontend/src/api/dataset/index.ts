import axios from 'utils/axios'
import { DATABASE_URL_HOST } from '../../const/API'
import { DatasetPostType } from 'store/slice/Dataset/DatasetType'

export const getDatasetListApi = async (project_id: string) => {
  const response = await axios.get(
    `${DATABASE_URL_HOST}/workdb/dataset/${project_id}/search`,
  )
  return response.data
}

export const createDatasetApi = async (
  data: DatasetPostType[],
  project_id: number,
) => {
  const response = await axios.post(
    `${DATABASE_URL_HOST}/workdb/dataset/${project_id}`,
    data,
  )
  return response.data
}
