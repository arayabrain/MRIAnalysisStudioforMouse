import { RootState } from 'store/store'

export const selectProject = (state: RootState) => state.project
export const selectCurrentProjectId = (state: RootState) =>
  state.project.currentProject?.id
export const selectProjectList = (state: RootState) => state.project.projects
