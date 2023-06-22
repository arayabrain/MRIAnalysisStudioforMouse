import { Box, styled, Typography } from '@mui/material'
import SourceIcon from '@mui/icons-material/Source'
import StorageIcon from '@mui/icons-material/Storage'
import GroupIcon from '@mui/icons-material/Group'
import AccountCircleIcon from '@mui/icons-material/AccountCircle'
import { Link } from 'react-router-dom'
import { useUser } from 'providers'
import { isAdmin } from 'utils/auth'

const Dashboard = () => {
  const { user } = useUser()
  return (
    <BoxWrapper>
      <h1 style={{ paddingLeft: 16 }}>Dashboard</h1>
      <DashboardWrapper>
        <DashboardContent>
          <LinkWrapper to="/database">
            <BoxMenu>
              <Box>
                <SourceIcon fontSize="large" />
                <TitleMenu>Database</TitleMenu>
              </Box>
            </BoxMenu>
          </LinkWrapper>
          <LinkWrapper to="/projects">
            <BoxMenu>
              <Box>
                <StorageIcon fontSize="large" />
                <TitleMenu>Projects</TitleMenu>
              </Box>
            </BoxMenu>
          </LinkWrapper>
          <LinkWrapper to="/account">
            <BoxMenu>
              <Box>
                <AccountCircleIcon fontSize="large" />
                <TitleMenu>Account</TitleMenu>
              </Box>
            </BoxMenu>
          </LinkWrapper>
          {isAdmin(user?.role) ? (
            <LinkWrapper to="/account-manager">
              <BoxMenu>
                <Box>
                  <GroupIcon fontSize="large" />
                  <TitleMenu>Account Manager</TitleMenu>
                </Box>
              </BoxMenu>
            </LinkWrapper>
          ) : null}
        </DashboardContent>
      </DashboardWrapper>
    </BoxWrapper>
  )
}

const BoxWrapper = styled(Box)({
  width: '100%',
  height: '100%',
})

const LinkWrapper = styled(Link)(() => ({
  textDecoration: 'none',
}))

const DashboardWrapper = styled(Box)(() => ({
  width: '100%',
  height: 'calc(100% - 90px)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}))

const DashboardContent = styled(Box)(() => ({
  padding: 30,
  display: 'flex',
  justifyContent: 'center',
  flexWrap: 'wrap',
  gap: 32,
}))

const BoxMenu = styled(Box)(() => ({
  width: 170,
  height: 150,
  backgroundColor: '#283237',
  borderRadius: 4,
  padding: '40px 30px',
  color: '#fff',
  textAlign: 'center',
  fontSize: 24,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  transition: 'all 0.3s',
  '&:hover': {
    transform: 'scale(1.1)',
    backgroundColor: 'rgba(40,50,55,0.9)',
  },
}))

const TitleMenu = styled(Typography)(() => ({
  fontSize: 24,
  marginTop: 30,
}))

export default Dashboard
