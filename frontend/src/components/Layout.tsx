import { Box, Typography } from '@mui/material'
import { styled } from '@mui/material/styles'
import { FC, useEffect, useState } from 'react'
import { drawerWidth } from './FlowChart/FlowChart'
import Header from './Header'
import { KeyboardBackspace } from '@mui/icons-material'
import HomeIcon from '@mui/icons-material/Home'
import SourceIcon from '@mui/icons-material/Source'
import StorageIcon from '@mui/icons-material/Storage'
import GroupIcon from '@mui/icons-material/Group'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { UserContext, useUser } from 'providers'
import { getToken } from 'utils/auth'
import { getMe } from 'api/auth'

const ignorePaths = ['/login', '/account-delete', '/reset-password']

const Layout: FC = ({ children }) => {
  const [user, setUser] = useState()
  const location = useLocation()
  const [width, setWidth] = useState(drawerWidth)
  const navigate = useNavigate()

  const onResize = () => {
    setWidth(width === drawerWidth ? 54 : drawerWidth)
  }

  useEffect(() => {
    checkkAuth()
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    checkkAuth()
    //eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname])

  const checkkAuth = async () => {
    if (user) return
    const token = getToken()
    try {
      if (token) {
        const data = await getMe()
        return setUser(data)
      }
      if (
        // !auth.currentUser &&
        !['/login', '/signup', '/reset-password'].includes(
          window.location.pathname,
        )
      ) {
        navigate('/login')
      }
    } catch {
      navigate('/login')
    }
  }

  return (
    <UserContext.Provider value={{ user, setUser }}>
      <LayoutWrapper>
        {ignorePaths.includes(location.pathname) ? null : <Header />}
        <ContentBodyWrapper>
          {ignorePaths.includes(location.pathname) ? null : (
            <MenuLeft onResize={onResize} width={width} />
          )}
          <ChildrenWrapper
            style={{
              width: `calc(100% - ${
                ignorePaths.includes(location.pathname) ? 0 : width + 10
              }px)`,
              height: '100%',
              overflow: 'auto',
            }}
          >
            {children}
          </ChildrenWrapper>
        </ContentBodyWrapper>
      </LayoutWrapper>
    </UserContext.Provider>
  )
}

const MenuLeft: FC<{ onResize: any; width: number }> = ({
  onResize,
  width,
}) => {
  const { user } = useUser()
  const { pathname } = useLocation()
  const isClose = width !== drawerWidth
  return (
    <MenuLeftWrapper style={{ width, minWidth: width }}>
      <BoxBack>
        <ButtonBack
          onClick={onResize}
          style={{ transform: `rotate(${width === drawerWidth ? 0 : 180}deg)` }}
        >
          <BoxDivider />
          <KeyboardBackspaceIcon />
        </ButtonBack>
      </BoxBack>
      <MenuList>
        <LinkWrapper to="/">
          <MenuItem isClose={isClose} active={pathname === '/'}>
            <HomeIcon />
            <TypographyMenu style={{ opacity: Number(width === drawerWidth) }}>
              Dashboard
            </TypographyMenu>
          </MenuItem>
        </LinkWrapper>
        <LinkWrapper to="/database">
          <MenuItem isClose={isClose} active={pathname === '/database'}>
            <StorageIcon />
            <TypographyMenu style={{ opacity: Number(width === drawerWidth) }}>
              Database
            </TypographyMenu>
          </MenuItem>
        </LinkWrapper>
        <LinkWrapper to="/projects">
          <MenuItem isClose={isClose} active={pathname === '/projects'}>
            <SourceIcon />
            <TypographyMenu style={{ opacity: Number(width === drawerWidth) }}>
              Projects
            </TypographyMenu>
          </MenuItem>
        </LinkWrapper>
        {user?.role === 'ADMIN' ? (
          <LinkWrapper to="/account-manager">
            <MenuItem
              isClose={isClose}
              active={pathname === '/account-manager'}
            >
              <GroupIcon />
              <TypographyMenu
                style={{ opacity: Number(width === drawerWidth) }}
              >
                Account Manager
              </TypographyMenu>
            </MenuItem>
          </LinkWrapper>
        ) : null}
      </MenuList>
    </MenuLeftWrapper>
  )
}

const LinkWrapper = styled(Link)(() => ({
  textDecoration: 'none',
}))

const LayoutWrapper = styled(Box)({
  height: '100%',
  width: '100%',
})

const ContentBodyWrapper = styled(Box)(() => ({
  backgroundColor: '#ffffff',
  display: 'flex',
  paddingTop: 48,
  height: 'calc(100% - 48px)',
  paddingRight: 10,
  overflow: 'hidden',
}))

const ChildrenWrapper = styled(Box)(() => ({
  height: 'calc(100% - 10px)',
  display: 'flex',
  paddingTop: 10,
  paddingLeft: 10,
}))

const MenuLeftWrapper = styled(Box)({
  height: '100%',
  backgroundColor: '#283237',
  overflow: 'auto',
  transition: 'all 0.3s',
})

const BoxBack = styled(Box)({
  width: '100%',
  height: 54,
  display: 'flex',
  justifyContent: 'flex-end',
})

const ButtonBack = styled(Box)({
  height: 54,
  width: 54,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  cursor: 'pointer',
})

const BoxDivider = styled(Box)({
  height: 15,
  width: 1,
  backgroundColor: '#ffffff',
  marginRight: -2,
})

const KeyboardBackspaceIcon = styled(KeyboardBackspace)({
  color: '#ffffff',
  fontSize: 20,
})

const MenuList = styled('ul')({
  margin: 0,
  padding: 0,
})

const MenuItem = styled('li', {
  shouldForwardProp: (props) => props !== 'isClose' && props !== 'active',
})<{ isClose: boolean; active: boolean }>(({ isClose, active }) => ({
  padding: '0 15px',
  color: '#ffffff',
  listStyle: 'none',
  height: 38,
  minHeight: 38,
  display: 'flex',
  alignItems: 'center',
  gap: 10,
  width: 'calc(100% - 30px)',
  minWidth: 'max-content',
  transition: 'all 0.3s',
  cursor: 'pointer',
  backgroundColor: active ? 'rgba(255,255,255,0.4) !important' : 'transparent',
  '&:hover': {
    transform: isClose
      ? 'scale(1.05) translateX(2px)'
      : 'scale(1.05) translateX(10px)',
    backgroundColor: 'rgba(255,255,255,0.2)',
  },
}))

const TypographyMenu = styled(Typography)({
  lineHeight: '20px',
  marginTop: 4,
  fontWeight: 500,
  transition: 'opacity 0.3s',
})

export default Layout
