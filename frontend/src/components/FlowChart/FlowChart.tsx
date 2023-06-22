import React from 'react'
import { useSelector } from 'react-redux'
import { drawerClasses } from '@mui/material/Drawer'
import { styled } from '@mui/material/styles'
import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'

import { AlgorithmTreeView } from './TreeView'
import { ReactFlowComponent } from './ReactFlowComponent'
import RightDrawer, { rightDrawerWidth } from './RightDrawer'
import { selectRightDrawerIsOpen } from 'store/slice/RightDrawer/RightDrawerSelectors'
import { UseRunPipelineReturnType } from 'store/slice/Pipeline/PipelineHook'
import { Box } from '@mui/material'

const FlowChart = React.memo<UseRunPipelineReturnType>((props) => {
  const open = useSelector(selectRightDrawerIsOpen)
  return (
    <RootDiv>
      <DndProvider backend={HTML5Backend}>
        <StyledDrawer>
          <DrawerContents>
            <AlgorithmTreeView />
          </DrawerContents>
        </StyledDrawer>
        <MainContents open={open}>
          <ReactFlowComponent {...props} />
        </MainContents>
      </DndProvider>
      <RightDrawer />
    </RootDiv>
  )
})

export const drawerWidth = 240

const RootDiv = styled('div')({
  display: 'flex',
  position: 'relative',
  alignItems: 'stretch',
  height: '100%',
})

const StyledDrawer = styled(Box)(({ theme }) => ({
  width: drawerWidth,
  flexShrink: 0,
  backgroundColor: '#fff',
  color: 'rgba(0, 0, 0, 0.87)',
  borderRight: '1px solid rgba(0, 0, 0, 0.12)',
  paddingTop: theme.spacing(1.125),
  overflow: 'auto',
  [`& .${drawerClasses.paper}`]: {
    width: drawerWidth,
  },
}))

const DrawerContents = styled('div')({
  overflow: 'auto',
  height: '100%',
})

const MainContents = styled('main')<{ open: boolean }>(
  ({ theme }) => ({
    height: '100%',
    width: '100%',
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    marginRight: -rightDrawerWidth,
    paddingTop: theme.spacing(1.125),
  }),
  ({ open, theme }) =>
    open
      ? {
          transition: theme.transitions.create('margin', {
            easing: theme.transitions.easing.easeOut,
            duration: theme.transitions.duration.enteringScreen,
          }),
          marginRight: 0,
        }
      : undefined,
)

export default FlowChart
