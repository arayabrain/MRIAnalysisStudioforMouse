import React from 'react'
import Button from '@mui/material/Button'
import Box from '@mui/material/Box'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell, { tableCellClasses } from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableRow from '@mui/material/TableRow'
import Paper from '@mui/material/Paper'
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown'
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp'
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos'
import Typography from '@mui/material/Typography'

import { CollapsibleTable } from './CollapsibleTable'
import { ExperimentStatusIcon } from './ExperimentStatusIcon'
import {useNavigate} from "react-router-dom";
import {Data} from "./Experiment";
import dayjs from "dayjs";
import {EXPERIMENTS_STATUS} from "../../store/slice/Experiments/ExperimentsType";

export const ExperimentUidContext = React.createContext<string>('')

type ExperimentTableProps = {
  data?: Data
}

export const ExperimentTable = ({data}: ExperimentTableProps) => {
  if(!data) return <></>
  return <TableImple data={data} />
}

const TableImple = React.memo(({data}: ExperimentTableProps) => {
  const navigate = useNavigate()
  const onClickBack = () => {
    navigate('/projects')
  }

  const dataView = data?.[Object.keys(data)[0]]

  return (
    <>
      { data ?
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
            <Button
              onClick={onClickBack}
              sx={{width: 'fit-content', textTransform: 'unset', fontSize: '1rem'}}
            >
              <ArrowBackIosIcon /> PROJECTS
            </Button>
            <Box sx={{
              display: 'flex',
              gap : 4,
              width: '90%',
              margin: 'auto',
              alignItems: 'flex-start'
            }}>
              <Typography>
                Status:
              </Typography>
              <Box>
                <ExperimentStatusIcon status={dataView?.status as EXPERIMENTS_STATUS}/>
              </Box>
              <Box>
                <Typography>Start time: {dayjs(dataView?.started_at).format('YYYY-MM-DD HH:mm')}</Typography>
                <Typography>Finish time: {dayjs(dataView?.finished_at).format('YYYY-MM-DD HH:mm')}</Typography>
              </Box>
            </Box>
            <Paper
                elevation={0}
                variant="outlined"
                sx={{
                  flexGlow: 1,
                  height: '100%',
                  width: '90%',
                  margin: 'auto'
                }}
            >
              {
                dataView?.results?.map((item) => {
                  const { name, subject_id } = item
                  return (
                      <TableContainer key={subject_id} component={Paper} elevation={0}>
                        <Table aria-label="collapsible table">
                          <TableBody>
                            <ExperimentUidContext.Provider
                                value={subject_id}
                                key={subject_id}
                            >
                              <RowItem
                                  data={item.function}
                                  name={name}
                              />
                            </ExperimentUidContext.Provider>
                          </TableBody>
                        </Table>
                      </TableContainer>
                  )
                })
              }
            </Paper>
          </Box> :
        <TableRow>
          <TableCell colSpan={10}>
            <Typography
                sx={{
                  color: (theme) => theme.palette.text.secondary,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  height: '300px',
                  textAlign: 'center',
                }}
                variant="h6"
            >
              No Rows...
            </Typography>
          </TableCell>
        </TableRow>}
    </>
  )
})

const RowItem = React.memo<{
  name: string
  data: object
}>(({ name, data }) => {
  const [open, setOpen] = React.useState(false)
  return (
    <React.Fragment>
      <TableRow
        onClick={() => Object.keys(data).length && setOpen((prevOpen) => !prevOpen)}
        sx={{
          '& > *': {
            borderBottom: 'unset',
          },
          [`& .${tableCellClasses.root}`]: {
            borderBottomWidth: 0,
          },
        }}
      >
        <TableCell
          sx={{padding: '20px',
               display: 'flex',
               alignItems: 'center'
          }}
        >
          {name} {Object.keys(data).length ? (!open ? <KeyboardArrowDownIcon /> : <KeyboardArrowUpIcon />) : null}
        </TableCell>
      </TableRow>
      <CollapsibleTable data={data} open={open} />
    </React.Fragment>
  )
})
