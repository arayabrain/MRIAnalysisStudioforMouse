import { createAsyncThunk } from '@reduxjs/toolkit'
import {
  PROJECT_SLICE_NAME,
  Dataset,
  DatasetPostType,
  SubFolder,
} from './DatasetType'
import { createDatasetApi, getDatasetListApi } from 'api/dataset'

export const getDatasetList = createAsyncThunk<Dataset, { project_id: string }>(
  `${PROJECT_SLICE_NAME}/getDatasets`,
  async (param, thunkAPI) => {
    const { rejectWithValue } = thunkAPI
    try {
      const response = await getDatasetListApi(param.project_id)
      return {
        dataset: response?.records as SubFolder[],
        project_id: param.project_id,
        last_updated_time: response?.last_updated_time,
      }
    } catch (e) {
      return rejectWithValue(e)
    }
  },
)

export const createDataset = createAsyncThunk<
  Dataset,
  {
    dataset: DatasetPostType[]
    project_id: number
    callback?: (isSuccess: boolean) => void
  }
>(`${PROJECT_SLICE_NAME}/createDataset`, async (param, thunkAPI) => {
  const { rejectWithValue } = thunkAPI
  try {
    const response = await createDatasetApi(param.dataset, param.project_id)
    param.callback?.(true)
    return response
  } catch (e) {
    param.callback?.(false)
    return rejectWithValue(e)
  }
})
