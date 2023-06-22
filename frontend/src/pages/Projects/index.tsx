import { Box, Button, styled } from '@mui/material'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import TableComponent, { Column } from 'components/Table'
import { useNavigate } from 'react-router-dom'
import ModalDeleteAccount from 'components/ModalDeleteAccount'
import {selectLoadingProject, selectProjectList} from 'store/slice/Project/ProjectSelector'
import {
  deleteProject,
  getProjectList,
} from 'store/slice/Project/ProjectAction'
import Loading from "../../components/common/Loading";

export type DataProject = {
  id: number | string
  uid?: number | string
  name: string
  project_type: number
  image_count: number
  created_time: string
  updated_time: string
  role?: string | number
}

const Projects = () => {
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const projects = useSelector(selectProjectList)
  const loading = useSelector(selectLoadingProject)
  const [idDelete, setIdDelete] = useState<number | string | undefined>()

  useEffect(() => {
    dispatch(getProjectList())
    //eslint-disable-next-line
  }, [])

  const onEdit = useCallback((id: number | string) => {
    navigate(`/projects/new-project?id=${id}`)
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const onWorkflow = useCallback((id: number | string) => {
    navigate(`/projects/workflow?tab=0&id=${id}`)
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const onResults = useCallback((id: number | string) => {
    navigate(`/projects/workflow?tab=1&id=${id}`)
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const addNewProject = useCallback(() => {
    navigate('/projects/new-project')
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const onDelete = (id: number | string) => {
    setIdDelete(id)
  }

  const onDeleteSubmit = async () => {
    const id = idDelete
    if (!id) return
      await dispatch(deleteProject({ project_id: Number(id) }))
      setIdDelete(undefined)
  }

  const handleCloseDelete = () => {
    setIdDelete(undefined)
  }

  const columns = useMemo(
    (): Column[] => [
      { title: 'Project Name', name: 'project_name' },
      { title: 'Created', name: 'created_time' },
      { title: 'Updated', name: 'updated_time' },
      { title: 'Images', name: 'image_count', align: 'center' },
      {
        title: '',
        name: 'action',
        width: 400,
        render: (data) => {
          return (
            <BoxAction>
              <ButtonAdd variant="contained" onClick={() => onEdit(data.id)}>
                Edit
              </ButtonAdd>
              <ButtonAdd
                variant="contained"
                onClick={() => onWorkflow(data.id)}
                sx={{ backgroundColor: '#1976D2 !important' }}
              >
                Workflow
              </ButtonAdd>
              <ButtonAdd
                variant="contained"
                onClick={() => onResults(data.id)}
                sx={{ backgroundColor: '#1976D2 !important' }}
              >
                Result
              </ButtonAdd>
              <ButtonAdd
                variant="contained"
                onClick={() => onDelete(data.id)}
                sx={{ backgroundColor: 'red !important' }}
              >
                Del
              </ButtonAdd>
            </BoxAction>
          )
        },
      },
    ],
    [onWorkflow, onResults, onEdit],
  )
  return (
    <ProjectsWrapper>
      <ModalDeleteAccount
        titleSubmit="Delete Project"
        description="Delete My Project"
        onClose={handleCloseDelete}
        open={!!idDelete}
        onSubmit={onDeleteSubmit}
      />
      <ProjectsTitle>Projects</ProjectsTitle>
      <BoxButton>
        <ButtonAdd
          variant="contained"
          onClick={addNewProject}
          sx={{ marginBottom: 2 }}
        >
          Add Project
        </ButtonAdd>
      </BoxButton>
      <TableComponent
        data={projects}
        columns={columns}
      />
      {
        loading ? <Loading /> : null
      }
    </ProjectsWrapper>
  )
}

const ProjectsWrapper = styled(Box)(({ theme }) => ({
  width: '100%',
  padding: theme.spacing(2),
  height: 'calc(100% - 90px)',
  overflow: 'auto'
}))

const ProjectsTitle = styled('h1')(({ theme }) => ({}))

const BoxButton = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'flex-end',
  gap: theme.spacing(1),
}))

const BoxAction = styled(BoxButton)({
  justifyContent: 'flex-start',
})

const ButtonAdd = styled(Button)(({ theme }) => ({
  minWidth: 80,
  letterSpacing: 'unset',
  paddingLeft: theme.spacing(2),
  paddingRight: theme.spacing(2),
  backgroundColor: '#283237 !important',
  color: '#ffffff',
}))

export default Projects
