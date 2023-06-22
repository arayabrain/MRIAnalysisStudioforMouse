import { Box, Button, styled, Typography } from '@mui/material'
import { Input } from 'components/common/Input'
import ModalChangePassword from 'components/ModalChangePassword'
import ModalDeleteAccount from 'components/ModalDeleteAccount'
import { useUser } from 'providers'
import { useState } from 'react'
import { isAdmin, optionsRole } from "utils/auth";
import {deleteAccountProfile, editNameProfile, editPassProfile} from "api/auth";
import { useNavigate } from "react-router-dom";
import Loading from "components/common/Loading";

const Account = () => {
  const { user, setUser } = useUser()
  const navigate = useNavigate()
  const [isEditName, setIsEditName] = useState(false)
  const [openDelete, setOpenDelete] = useState(false)
  const [openChangePw, setOpenChangePw] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const onEditName = async (e: any) => {
    const { value } = e.target
    if(!value) {
      alert('This field is required')
      setIsEditName(false)
      return
    }
    setIsLoading(true)
    try {
      setUser({...user, display_name: value})
      await editNameProfile({...user, display_name: value})
    }
    catch {}
    finally {
      setIsLoading(false)
      setIsEditName(false)
    }
  }
  const handleCloseDelete = () => {
    setOpenDelete(false)
  }

  const onConfirmDelete = () => {
    setOpenDelete(true)
  }

  const onDelete = async () => {
    //todo call api
    if(!user) return
    setIsLoading(true)
    try {
      await deleteAccountProfile()
      navigate('/login')
    }
    catch {}
    finally {
      setIsLoading(false)
    }
    handleCloseDelete()
  }

  const handleCloseChangePw = () => {
    setOpenChangePw(false)
  }

  const onConfirmChangePw = () => {
    setOpenChangePw(true)
  }

  const onChangePw = async (oldPass: string, newPass: string) => {
    //todo call api
    setIsLoading(true)
    try {
      await editPassProfile({old_password: oldPass, new_password: newPass})
      alert('Your password has been successfully changed.')
      handleCloseChangePw()
    }
    catch {
      alert('Failed to Change Password!')
    }
    finally {
      setIsLoading(false)
    }
  }

  return (
    <AccountWrapper>
      <ModalDeleteAccount
        titleSubmit="Delete My Account"
        onClose={handleCloseDelete}
        open={openDelete}
        onSubmit={onDelete}
      />
      <ModalChangePassword
        onSubmit={onChangePw}
        open={openChangePw}
        onClose={handleCloseChangePw}
      />
      <Title>Account Profile</Title>
      <BoxFlex>
        <TitleData>Account ID</TitleData>
        <BoxData>{user?.uid}</BoxData>
      </BoxFlex>
      <BoxFlex>
        <TitleData sx={{ marginTop: isEditName ? -2 : 0 }}>Full name</TitleData>
        <BoxData>
          {isEditName ? (
            <Input
              autoFocus
              defaultValue={user?.display_name || ''}
              onBlur={(e) => onEditName(e)}
              placeholder="Full name"
            />
          ) : (
            <>
              {user?.display_name || "--"}
              <Button sx={{ ml: 1 }} onClick={() => setIsEditName(true)}>
                Edit
              </Button>
            </>
          )}
        </BoxData>
      </BoxFlex>
      <BoxFlex>
        <TitleData>Email</TitleData>
        <BoxData>{user?.email}</BoxData>
      </BoxFlex>
      <BoxFlex>
        <TitleData>Role</TitleData>
        <BoxData>{optionsRole.find(role => String(role.code) === String(user?.role))?.name}</BoxData>
      </BoxFlex>
      <BoxFlex sx={{ justifyContent: 'space-between', mt: 10 }}>
        <ButtonSubmit onClick={onConfirmChangePw}>Change Password</ButtonSubmit>
        {
          !isAdmin(user?.role) &&
          <ButtonSubmit onClick={onConfirmDelete}>Delete Account</ButtonSubmit>
        }
      </BoxFlex>
      {
        isLoading && <Loading />
      }
    </AccountWrapper>
  )
}

const AccountWrapper = styled(Box)({
  padding: '0 20px',
})

const BoxFlex = styled(Box)({
  display: 'flex',
  margin: '20px 0 10px 0',
  alignItems: 'center',
  maxWidth: 1000,
})

const Title = styled('h2')({
  marginBottom: 40,
})

const BoxData = styled(Typography)({
  fontWeight: 700,
  minWidth: 272,
})

const TitleData = styled(Typography)({
  width: 250,
})

const ButtonSubmit = styled('button')({
  backgroundColor: '#283237',
  color: '#ffffff',
  borderRadius: 4,
  border: 'none',
  outline: 'none',
  padding: '10px 20px',
  cursor: 'pointer',
})

export default Account
