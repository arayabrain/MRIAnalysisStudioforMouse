import { createSlice } from '@reduxjs/toolkit'
import { PROJECT_SLICE_NAME, Project } from './ProjectType'
import {getProjectList, getProjectId, deleteProject} from './ProjectAction'

const initialState: Project = {
  projects: [],
  loading: true,
  currentProject: undefined,
}

export const projectSlice = createSlice({
  name: PROJECT_SLICE_NAME,
  initialState,
  reducers: {
    resetCurrentProject: (state) => {
      state.currentProject = undefined
    },
  },
  extraReducers: (builder) => {
    builder
        .addCase(getProjectList.fulfilled, (state, action) => {
          state.projects = action.payload.projects
          state.loading = false
        })
        .addCase(getProjectList.pending, (state) => {
          if(!state.loading) state.loading = true
        })
        .addCase(getProjectId.fulfilled, (state, action) => {
          state.currentProject = action.payload
        })
        .addCase(getProjectId.rejected, (state, action) => {
          state.loading = false
        })
        .addCase(deleteProject.fulfilled, (state, action) => {
          state.loading = false
        })
        .addCase(deleteProject.pending, (state) => {
          if(!state.loading) state.loading = true
        })
  },
})

export const { resetCurrentProject } = projectSlice.actions
export default projectSlice.reducer
