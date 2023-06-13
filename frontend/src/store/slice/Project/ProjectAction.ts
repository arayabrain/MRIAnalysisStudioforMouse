import { createAsyncThunk } from '@reduxjs/toolkit'
import {
  CurrentProject,
  PROJECT_SLICE_NAME,
  Project,
  ProjectCreate,
  ProjectType,
} from './ProjectType'
import {
  createProjectApi,
  deleteProjectApi,
  getProjectApi,
  getProjectListApi,
  updateProjectApi,
} from 'api/project'
import { DatasetPostType } from '../Dataset/DatasetType'
import { createDataset } from '../Dataset/DatasetAction'

export const getProjectList = createAsyncThunk<
  Project,
  { callback?: (isSuccess: boolean) => void } | undefined
>(`${PROJECT_SLICE_NAME}/getProjects`, async (param, thunkAPI) => {
  const { rejectWithValue } = thunkAPI
  try {
    const response = await getProjectListApi()
    param?.callback?.(true)
    return response
  } catch (e) {
    param?.callback?.(false)
    return rejectWithValue(e)
  }
})

export const getProjectId = createAsyncThunk<
  CurrentProject,
  { project_id: string; callback?: (isSuccess: boolean) => void } | undefined
>(`${PROJECT_SLICE_NAME}/getProjectId`, async (param, thunkAPI) => {
  const { rejectWithValue } = thunkAPI
  try {
    if (!param?.project_id) return undefined
    const response = await getProjectApi(param.project_id)
    param?.callback?.(true)
    return response
  } catch (e) {
    param?.callback?.(false)
    return rejectWithValue(e)
  }
})

export const createProject = createAsyncThunk<
  ProjectType,
  {
    project: ProjectCreate
    dataset: DatasetPostType[]
    callback?: (isSuccess: boolean) => void
  }
>(`${PROJECT_SLICE_NAME}/createProject`, async (param, thunkAPI) => {
  const { rejectWithValue } = thunkAPI
  try {
    const response = await createProjectApi(param.project)
    thunkAPI.dispatch(
      createDataset({
        project_id: response.id,
        dataset: param.dataset,
        callback: param.callback,
      }),
    )
    return response
  } catch (e) {
    param.callback?.(false)
    return rejectWithValue(e)
  }
})

export const editProject = createAsyncThunk<
  ProjectType,
  {
    project: ProjectCreate
    project_id: string
    dataset: DatasetPostType[]
    callback?: (isSuccess: boolean) => void
  }
>(`${PROJECT_SLICE_NAME}/editProject`, async (param, thunkAPI) => {
  const { rejectWithValue } = thunkAPI
  try {
    const response = await updateProjectApi(param.project_id, param.project)
    await thunkAPI.dispatch(
      createDataset({
        project_id: Number(param.project_id),
        dataset: param.dataset,
        callback: param.callback,
      }),
    )
    param.callback?.(true)
    return response
  } catch (e) {
    param.callback?.(false)
    return rejectWithValue(e)
  }
})

export const deleteProject = createAsyncThunk<
  null,
  {
    project_id: number
    callback?: (isSuccess: boolean) => void
  }
>(`${PROJECT_SLICE_NAME}/deleteProject`, async (param, thunkAPI) => {
  const { rejectWithValue } = thunkAPI
  try {
    await deleteProjectApi(param.project_id)
    thunkAPI.dispatch(getProjectList({ callback: param.callback }))
    return null
  } catch (e) {
    param.callback?.(false)
    return rejectWithValue(e)
  }
})
