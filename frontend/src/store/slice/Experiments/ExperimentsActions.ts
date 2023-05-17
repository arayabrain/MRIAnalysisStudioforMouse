import { createAsyncThunk } from '@reduxjs/toolkit'
import {
  ExperimentsDTO,
  getExperimentsApi,
  deleteExperimentByUidApi,
  importExperimentByUidApi,
  deleteExperimentByListApi,
  ExperimentDTO,
  fetchExperimentApi,
} from 'api/experiments/Experiments'
import { RunPostData } from 'api/run/Run'
import { EXPERIMENTS_SLICE_NAME } from './ExperimentsType'
import { selectCurrentProjectId } from '../Project/ProjectSelector'
import { ThunkApiConfig } from 'store/store'

export const getExperiments = createAsyncThunk<
  ExperimentsDTO,
  undefined,
  ThunkApiConfig
>(`${EXPERIMENTS_SLICE_NAME}/getExperiments`, async (_, thunkAPI) => {
  const projectId = selectCurrentProjectId(thunkAPI.getState())
  if (projectId) {
    try {
      const response = await getExperimentsApi(projectId)
      return response
    } catch (e) {
      return thunkAPI.rejectWithValue(e)
    }
  } else {
    return thunkAPI.rejectWithValue('project id does not exist.')
  }
})

export const fetchExperiment = createAsyncThunk<ExperimentDTO, string>(
  `${EXPERIMENTS_SLICE_NAME}/fetchExperiment`,
  async (projectId, thunkAPI) => {
    try {
      const response = await fetchExperimentApi(projectId)
      return response ?? thunkAPI.rejectWithValue('no project exist.')
    } catch (e) {
      return thunkAPI.rejectWithValue(e)
    }
  },
)

export const deleteExperimentByUid = createAsyncThunk<boolean, string>(
  `${EXPERIMENTS_SLICE_NAME}/deleteExperimentByUid`,
  async (uid, thunkAPI) => {
    try {
      const response = await deleteExperimentByUidApi(uid)
      return response
    } catch (e) {
      return thunkAPI.rejectWithValue(e)
    }
  },
)

export const deleteExperimentByList = createAsyncThunk<boolean, string[]>(
  `${EXPERIMENTS_SLICE_NAME}/deleteExperimentByList`,
  async (uid, thunkAPI) => {
    try {
      const response = await deleteExperimentByListApi(uid)
      return response
    } catch (e) {
      return thunkAPI.rejectWithValue(e)
    }
  },
)

export const importExperimentByUid = createAsyncThunk<RunPostData, string>(
  `${EXPERIMENTS_SLICE_NAME}/importExperimentByUid`,
  async (uid, thunkAPI) => {
    try {
      const response = await importExperimentByUidApi(uid)
      return response
    } catch (e) {
      return thunkAPI.rejectWithValue(e)
    }
  },
)
