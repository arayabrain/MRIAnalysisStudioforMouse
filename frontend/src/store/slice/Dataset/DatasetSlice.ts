import { createSlice } from '@reduxjs/toolkit'
import { PROJECT_SLICE_NAME, Dataset } from './DatasetType'
import { getDatasetList } from './DatasetAction'

const initialState: Dataset = {
  dataset: undefined,
  project_id: null,
  last_updated_time: null,
}

export const datasetSlice = createSlice({
  name: PROJECT_SLICE_NAME,
  initialState,
  reducers: {
    reset: (state) => {
      state.project_id = null
      state.dataset = undefined
    },
  },
  extraReducers: (builder) => {
    builder.addCase(getDatasetList.fulfilled, (state, action) => {
      state.dataset = action.payload.dataset
      state.project_id = action.payload.project_id
    })
  },
})

export const { reset } = datasetSlice.actions
export default datasetSlice.reducer
