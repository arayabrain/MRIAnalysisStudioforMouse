import React from 'react'
import { drawerClasses } from '@mui/material/Drawer'
import { styled } from '@mui/material/styles'
import { drawerWidth } from 'components/FlowChart/FlowChart'
import { FlexItemList } from './FlexItemList'
import { VisualizeItemEditor } from './VisualizeItemEditor'
import { Box } from '@mui/material'

const Visualize: React.FC = () => {
  return (
    <RootDiv>
      <StyledDrawer>
        <StyledDrawerContents>
          <VisualizeItemEditor />
        </StyledDrawerContents>
      </StyledDrawer>
      <MainContents>
        <FlexItemList />
      </MainContents>
    </RootDiv>
  )
}

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

const StyledDrawerContents = styled('div')({
  overflow: 'auto',
})

const MainContents = styled('main')(({ theme }) => ({
  height: '100%',
  width: '100%',
}))

export default Visualize
