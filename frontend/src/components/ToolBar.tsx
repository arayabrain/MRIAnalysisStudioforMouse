import React from 'react'
import Box from '@mui/material/Box'

import { UseRunPipelineReturnType } from 'store/slice/Pipeline/PipelineHook'
// import { NWBSettingButton } from './FlowChart/NWB'
import { SnakemakeButton } from './FlowChart/Snakemake'
import { RunButtons } from './RunButtons'
import { Button } from '@mui/material'
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos'
import { useNavigate } from 'react-router-dom'

export const ToolBar = React.memo<UseRunPipelineReturnType>((props) => {
  const navigate = useNavigate()
  return (
    <Box
      style={{
        position: 'absolute',
        float: 'right',
        textAlign: 'right',
        top: -7,
        right: 10,
        zIndex: 4,
        textTransform: 'none',
        fontSize: '1rem',
      }}
    >
      <Button onClick={() => navigate('/projects')}>
        <ArrowBackIosIcon />
        Projects
      </Button>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
      <SnakemakeButton />
      {/*<NWBSettingButton />*/}
      <RunButtons {...props} />
    </Box>
  )
})
