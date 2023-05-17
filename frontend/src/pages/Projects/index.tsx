import { Box, Button, styled } from '@mui/material'
import { useCallback, useMemo, useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import TableComponent, { Column } from '../../components/Table'
import { useNavigate } from 'react-router-dom'
import ModalDeleteAccount from 'components/ModalDeleteAccount'
import { selectProjectList } from 'store/slice/Project/ProjectSelector'
import { deleteProject } from 'store/slice/Project/ProjectSlice'

const Projects = () => {
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const projects = useSelector(selectProjectList)
  const [idDelete, setIdDelete] = useState<number | string | undefined>()

  const onEdit = useCallback((id: number | string) => {
    navigate(`/projects/new-project?id=${id}`)
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const onWorkflow = useCallback((id: number | string) => {
    console.log('Workflow: ', id)
    navigate(`/projects/workflow?tab=0&id=${id}`)
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const onResults = useCallback((id: number | string) => {
    console.log('Results: ', id)
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

  const onDeleteSubmit = () => {
    const id = idDelete
    setIdDelete(undefined)
    dispatch(deleteProject(id))
  }

  const handleCloseDelete = () => {
    setIdDelete(undefined)
  }

  const columns = useMemo(
    (): Column[] => [
      { title: 'Project Name', name: 'name' },
      { title: 'Created', name: 'created_time' },
      { title: 'Updated', name: 'updated_time' },
      { title: 'Images', name: 'image_count', align: 'center' },
      {
        title: '',
        name: 'action',
        width: 400,
        render: (data) => {
          return (
            <BoxButton>
              <ButtonAdd variant="contained" onClick={() => onEdit(data.id)}>
                Edit
              </ButtonAdd>
              <ButtonAdd
                variant="contained"
                onClick={() => onWorkflow(data.id)}
              >
                Workflow
              </ButtonAdd>
              <ButtonAdd variant="contained" onClick={() => onResults(data.id)}>
                Results
              </ButtonAdd>
              <ButtonAdd
                variant="contained"
                onClick={() => onDelete(data.id)}
                sx={{ backgroundColor: 'red !important' }}
              >
                Del
              </ButtonAdd>
            </BoxButton>
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
        paginate={{ total: 100, page: 1, page_size: 10 }}
        data={projects}
        columns={columns}
      />
    </ProjectsWrapper>
  )
}

const ProjectsWrapper = styled(Box)(({ theme }) => ({
  width: '100%',
  padding: theme.spacing(2),
}))

const ProjectsTitle = styled('h1')(({ theme }) => ({}))

const BoxButton = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'flex-end',
  gap: theme.spacing(1),
}))

const ButtonAdd = styled(Button)(({ theme }) => ({
  minWidth: 80,
  letterSpacing: 'unset',
  paddingLeft: theme.spacing(2),
  paddingRight: theme.spacing(2),
  backgroundColor: '#283237 !important',
  color: '#ffffff',
}))

export default Projects
