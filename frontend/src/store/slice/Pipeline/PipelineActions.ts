import { createAsyncThunk } from '@reduxjs/toolkit'

import { ThunkApiConfig } from 'store/store'
import { PIPELINE_SLICE_NAME } from './PipelineType'
import {
  runApi,
  runByUidApi,
  runResult,
  RunResultDTO,
  RunPostData,
} from 'api/run/Run'
import {
  selectPipelineLatestUid,
  selectRunResultPendingNodeIdList,
} from './PipelineSelectors'
import { selectCurrentProjectId } from '../Project/ProjectSelector'

export const run = createAsyncThunk<
  string,
  { runPostData: RunPostData },
  ThunkApiConfig
>(`${PIPELINE_SLICE_NAME}/run`, async ({ runPostData }, thunkAPI) => {
  const projectId = selectCurrentProjectId(thunkAPI.getState())
  if (projectId) {
    try {
      const responseData = await runApi(projectId, runPostData)
      return responseData
    } catch (e) {
      return thunkAPI.rejectWithValue(e)
    }
  } else {
    return thunkAPI.rejectWithValue('projectId does not exist.')
  }
})

export const runByCurrentUid = createAsyncThunk<
  string,
  { runPostData: Omit<RunPostData, 'name'> },
  ThunkApiConfig
>(
  `${PIPELINE_SLICE_NAME}/runByCurrentUid`,
  async ({ runPostData }, thunkAPI) => {
    const projectId = selectCurrentProjectId(thunkAPI.getState())
    const currentUid = selectPipelineLatestUid(thunkAPI.getState())
    if (projectId && currentUid != null) {
      try {
        const responseData = await runByUidApi(
          projectId,
          currentUid,
          runPostData,
        )
        return responseData
      } catch (e) {
        return thunkAPI.rejectWithValue(e)
      }
    } else {
      return thunkAPI.rejectWithValue('projectId or currentUid dose not exist.')
    }
  },
)

export const pollRunResult = createAsyncThunk<
  RunResultDTO,
  {
    uid: string
  },
  ThunkApiConfig
>(`${PIPELINE_SLICE_NAME}/pollRunResult`, async ({ uid }, thunkAPI) => {
  const projectId = selectCurrentProjectId(thunkAPI.getState())
  const pendingNodeIdList = selectRunResultPendingNodeIdList(
    thunkAPI.getState(),
  )
  if (projectId) {
    try {
      const responseData = await runResult({
        projectId,
        uid,
        pendingNodeIdList,
      })
      return responseData
    } catch (e) {
      return thunkAPI.rejectWithValue(e)
    }
  } else {
    return thunkAPI.rejectWithValue('projectId does not exist.')
  }
})
