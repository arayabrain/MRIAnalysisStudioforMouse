import { Box, Typography } from '@mui/material'
import { styled } from '@mui/material/styles'
import { FC, useRef, useState } from 'react'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import PortraitIcon from '@mui/icons-material/Portrait'
import AccountCircleIcon from '@mui/icons-material/AccountCircle'
import LogoutIcon from '@mui/icons-material/Logout'
import { useUser } from 'providers'

const Header: FC = () => {
  const [open, setOpen] = useState(false)
  const { user } = useUser()

  const refMenu = useRef<HTMLDivElement | null>(null)

  const closeMenu = () => {
    setTimeout(() => {
      setOpen(false)
    }, 100)
  }

  const onClick = () => {
    if (open) {
      return refMenu.current?.blur?.()
    }
    setOpen(true)
  }

  return (
    <HeaderWrapper>
      <BoxWrapper>
        <Image src="/static/favicon.ico" alt="logo" />
        <TitleLogo>Studio</TitleLogo>
      </BoxWrapper>
      <BoxMenu ref={refMenu} tabIndex={1} onClick={onClick} onBlur={closeMenu}>
        <Typography>
          {user?.display_name || `${user?.email.substring(0, 7)}...`}
        </Typography>
        <ExpandMoreIcon />
        {open && (
          <BoxDropdown>
            <BoxInfo>
              <AccountCircleIcon />
              <Box>
                <Typography>{user?.display_name}</Typography>
                <Typography>{user?.email}</Typography>
              </Box>
            </BoxInfo>
            <BoxMenuItem>
              <PortraitIcon /> Profile
            </BoxMenuItem>
            <BoxMenuItem
              style={{ color: 'red', fontWeight: 600, marginTop: 30 }}
            >
              <LogoutIcon />
              SIGN OUT
            </BoxMenuItem>
          </BoxDropdown>
        )}
      </BoxMenu>
    </HeaderWrapper>
  )
}

const BoxDropdown = styled(Box)({
  position: 'absolute',
  backgroundColor: '#ffffff',
  padding: '8px 16px 0',
  top: 30,
  right: 0,
  listStyleType: 'none',
  backgroundClip: 'padding-box',
  borderRadius: 3,
  outline: 'none',
  boxShadow:
    '0 6px 16px 0 rgb(0 0 0 / 8%), 0 3px 6px -4px rgb(0 0 0 / 12%), 0 9px 28px 8px rgb(0 0 0 / 5%)',
  cursor: 'default',
  zIndex: 1,
  minWidth: 250,
})

const Image = styled('img')({
  height: 46,
})

const BoxWrapper = styled(Box)({
  display: 'flex',
  alignItems: 'center',
  gap: 8,
})

const BoxMenu = styled(BoxWrapper)({
  cursor: 'pointer',
  position: 'relative',
  userSelect: 'none',
})

const BoxInfo = styled(BoxWrapper)({
  borderBottom: `1px solid #e7e7e7`,
  padding: '8px 0',
  cursor: 'default',
})

const BoxMenuItem = styled(BoxWrapper)({
  padding: '8px 0',
  cursor: 'pointer',
  transition: 'all 0.3s',
  '&:hover': {
    transform: 'scale(1.05) translateX(5px)',
  },
})

const TitleLogo = styled(Typography)({
  fontWeight: 600,
  fontSize: 22,
})

const HeaderWrapper = styled(Box)({
  height: 48,
  backgroundColor: '#E1DEDB',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  color: 'rgba(0, 0, 0, 0.87)',
  boxShadow:
    '0px 2px 4px -1px rgb(0 0 0 / 20%), 0px 4px 5px 0px rgb(0 0 0 / 14%), 0px 1px 10px 0px rgb(0 0 0 / 12%)',
  position: 'fixed',
  width: 'calc(100% - 32px)',
  padding: '0 16px',
  zIndex: 9999,
})

export default Header
