import { PayloadAction, createSlice } from '@reduxjs/toolkit'
import { PROJECT_SLICE_NAME, Project } from './ProjectType'
import { fetchExperiment } from '../Experiments/ExperimentsActions'

const initialState: Project = {
  projects: [
    {
      id: '1',
      name: 'prj name 1',
      created_time: '2023-03-10 09:19:38',
      updated_time: '2023-03-10 09:19:38',
      image_count: 3,
      project_type: 0,
    },
    {
      id: '2',
      name: 'prj name 2',
      created_time: '2023-03-10 09:19:38',
      updated_time: '2023-03-10 09:19:38',
      image_count: 3,
      project_type: 1,
    },
  ],
  currentProject: {
    id: '1',
  },
}

export const projectSlice = createSlice({
  name: PROJECT_SLICE_NAME,
  initialState,
  reducers: {
    deleteProject: (
      state,
      action: PayloadAction<string | number | undefined>,
    ) => {
      state.projects = state.projects.filter(
        (project) => project.id !== action.payload,
      )
    },
  },
  extraReducers: (builder) => {
    builder.addCase(fetchExperiment.pending, (state, action) => {
      state.currentProject = {
        id: action.meta.arg,
      }
    })
  },
})

export const { deleteProject } = projectSlice.actions
export default projectSlice.reducer
