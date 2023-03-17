import { Box, Button, styled } from '@mui/material'
import ModalDeleteAccount from 'components/ModalDeleteAccount'
import TableComponent from 'components/Table'
import { useCallback, useEffect, useMemo, useState } from 'react'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import InputError from '../../components/common/InputError'
import SelectError from '../../components/common/SelectError'
import { listUser } from 'api/auth'

const ModalComponent = ({
  data,
  setData,
  setIsOpenModal,
  type,
  dataEdit,
}: any) => {
  const regex = /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(.\w{2,3})+$/
  const regexPassword = /^(?=.*\d)(?=.*[@$!%*#?&])(?=.*[a-zA-Z]).{6,100}$/
  const [formData, setFormData] = useState(type !== 'Add' ? dataEdit : {})
  const [errors, setErrors] = useState<{ [key: string]: string }>({
    email: '',
    password: '',
    role: '',
    lab: '',
    name: '',
    confirmPassword: '',
  })
  const [values, setValues] = useState<{ [key: string]: string }>(
    dataEdit || {
      email: '',
      password: '',
      role: '',
      lab: '',
      name: '',
      confirmPassword: '',
    },
  )
  const validateEmail = (value: string): string => {
    if (!value) return 'This field is required'
    if (!regex.test(value)) {
      return 'Invalid email format'
    }
    return ''
  }

  const validatePassword = (value: string): string => {
    if (!value) return 'This field is required'
    if (!regexPassword.test(value)) {
      return 'Your password must be at least 6 characters long and must contain at least one letter, number, and special character'
    }
    return ''
  }

  const onChangeData = useCallback(
    (e: any, type: string) => {
      setFormData({ ...formData, [type]: e.target.value })
      const { value } = e.target
      setValues((pre) => ({ ...pre, [type]: value }))
    },
    [formData],
  )
  const onBlurData = useCallback(
    (e: any, type: string, validate?: Function) => {
      const { value } = e.target
      setValues((pre) => ({ ...pre, [type]: value }))
      setErrors((pre) => ({
        ...pre,
        [type]: value === '' ? 'This field is required' : validate?.(value),
      }))
    },
    [],
  )

  const onSubmit = (e: any) => {
    e.preventDefault()
    const errorEmail = validateEmail(values.email)
    const errorPassword = validatePassword(values.password)
    const errorConfirmPassword = validatePassword(values.confirmPassword)
    const errorNotMatch =
      formData.password === formData.confirmPassword
        ? ''
        : 'password is not match'
    if (errorEmail || errorPassword || errorConfirmPassword || errorNotMatch) {
      setErrors({
        email: errorEmail,
        password: errorPassword,
        confirmPassword:
          errorConfirmPassword === '' ? errorNotMatch : errorConfirmPassword,
        name:
          values.name === '' || !formData.hasOwnProperty('name')
            ? 'This field is required'
            : '',
        lab:
          values.lab === '' || !formData.hasOwnProperty('lab')
            ? 'This field is required'
            : '',
        role:
          values.role === '' || !formData.hasOwnProperty('role')
            ? 'This field is required'
            : '',
      })
      return
    }
    if (type === 'Add') {
      setData([...data, { ...formData, id: String(Math.random() * 100) }])
    } else {
      setData((pre: any) => {
        pre.splice(data.indexOf(dataEdit), 1, formData)
        return pre
      })
    }
    setIsOpenModal(false)
  }
  const onCancel = () => {
    setIsOpenModal(false)
  }
  return (
    <Modal>
      <ModalBox>
        <TitleModal>{type} Account</TitleModal>
        <BoxData>
          <LabelModal>Lab: </LabelModal>
          <InputError
            value={formData?.lab || ''}
            onChange={(e: any) => onChangeData(e, 'lab')}
            onBlur={(e: any) => onBlurData(e, 'lab')}
            errorMessage={errors.lab}
          />
          <LabelModal>Name: </LabelModal>
          <InputError
            value={formData?.name || ''}
            onChange={(e: any) => onChangeData(e, 'name')}
            onBlur={(e: any) => onBlurData(e, 'name')}
            errorMessage={errors.name}
          />
          <LabelModal>Role: </LabelModal>
          <SelectError
            value={formData?.role || ''}
            options={['Admin', 'Researcher', 'Manager']}
            onChange={(e: any) => onChangeData(e, 'role')}
            onBlur={(e: any) => onBlurData(e, 'role')}
            errorMessage={errors.role}
          />
          <LabelModal>e-mail: </LabelModal>
          <InputError
            value={formData?.email || ''}
            onChange={(e: any) => onChangeData(e, 'email')}
            onBlur={(e: any) => onBlurData(e, 'email', validateEmail)}
            errorMessage={errors.email}
          />
          <LabelModal>Password: </LabelModal>
          <InputError
            value={formData?.password || ''}
            onChange={(e: any) => onChangeData(e, 'password')}
            onBlur={(e: any) => onBlurData(e, 'password', validatePassword)}
            type={'password'}
            errorMessage={errors.password}
          />
          <LabelModal>Confirm Password: </LabelModal>
          <InputError
            value={formData?.confirmPassword || ''}
            onChange={(e: any) => onChangeData(e, 'confirmPassword')}
            onBlur={(e: any) =>
              onBlurData(e, 'confirmPassword', validatePassword)
            }
            type={'password'}
            errorMessage={errors.confirmPassword}
          />
        </BoxData>
        <ButtonModal>
          <Button onClick={(e) => onSubmit(e)}>Ok</Button>
          <Button onClick={() => onCancel()}>Cancel</Button>
        </ButtonModal>
      </ModalBox>
    </Modal>
  )
}
const AccountManager = () => {
  const [openDelete, setOpenDelete] = useState(false)
  const [isOpenModal, setIsOpenModal] = useState(false)
  const [type, setType] = useState<string>('')
  const [dataEdit, setDateEdit] = useState({})
  const [idDel, setIdDel] = useState<string | undefined>()
  const [data, setData] = useState([
    {
      id: '1',
      lab: 'Lab1',
      name: 'Mail Address',
      role: 'Admin',
      email: 'sfdsf@gmail.com',
      password: 'abcxyz',
      confirmPassword: 'abcxyz',
    },
  ])

  useEffect(() => {
    getList()
  }, [])

  const getList = async () => {
    const data = await listUser()
    console.log('data', data)
  }

  const onOpenModal = (type: string) => {
    setIsOpenModal(true)
    setType(type)
  }

  const handleCloseDelete = () => {
    setOpenDelete(false)
  }

  const onConfirmDelete = (id: string) => {
    setIdDel(id)
    setOpenDelete(true)
  }

  const onForgotPassword = (data: any) => {
    //todo call api
    setDateEdit(data)
    setIsOpenModal(true)
    setType('Edit')
  }

  const onDelete = () => {
    const index = data.findIndex((item) => item.id === idDel)
    data.splice(index, 1)
    //todo call api
    handleCloseDelete()
  }

  const columns = useMemo(
    () => [
      { title: 'Lab', name: 'lab' },
      { title: 'Name', name: 'name' },
      { title: 'Role', name: 'role' },
      { title: 'Mail', name: 'email' },
      {
        title: '',
        name: 'action',
        width: 185,
        render: (data: any) => (
          <>
            <ALink sx={{ color: 'red' }} onClick={() => onForgotPassword(data)}>
              <EditIcon sx={{ color: 'black' }} />
            </ALink>
            <ALink sx={{ ml: 1.25 }} onClick={() => onConfirmDelete(data.id)}>
              <DeleteIcon sx={{ color: 'red' }} />
            </ALink>
          </>
        ),
      },
    ],
    [],
  )

  return (
    <AccountManagerWrapper>
      <ModalDeleteAccount
        titleSubmit="Delete Account"
        onClose={handleCloseDelete}
        open={openDelete}
        onSubmit={onDelete}
      />
      <BoxButton>
        <ButtonAdd onClick={() => onOpenModal('Add')} variant="contained">
          Add
        </ButtonAdd>
      </BoxButton>
      <TableComponent
        paginate={{ total: 100, page: 1, page_size: 10 }}
        data={data}
        columns={columns}
      />
      {isOpenModal ? (
        <ModalComponent
          data={data}
          setData={setData}
          type={type}
          setIsOpenModal={setIsOpenModal}
          dataEdit={dataEdit}
        />
      ) : null}
    </AccountManagerWrapper>
  )
}

const AccountManagerWrapper = styled(Box)(({ theme }) => ({
  width: '100%',
  padding: theme.spacing(2),
}))

const BoxButton = styled(Box)({
  display: 'flex',
  justifyContent: 'flex-end',
})

const ButtonAdd = styled(Button)(({ theme }) => ({
  margin: theme.spacing(2, 0),
  width: 100,
  backgroundColor: '#283237 !important',
  color: '#ffffff'
}))

const ALink = styled('a')({
  color: '#1677ff',
  textDecoration: 'none',
  cursor: 'pointer',
  userSelect: 'none',
})

const Modal = styled(Box)(({ theme }) => ({
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100%',
  height: '100vh',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  backgroundColor: '#cccccc80',
}))

const ModalBox = styled(Box)(({ theme }) => ({
  width: 800,
  height: 550,
  backgroundColor: 'white',
  border: '1px solid black',
}))

const TitleModal = styled(Box)(({ theme }) => ({
  fontSize: 25,
  margin: theme.spacing(5),
}))

const BoxData = styled(Box)(({ theme }) => ({
  marginTop: 35,
}))

const LabelModal = styled(Box)(({ theme }) => ({
  width: 300,
  display: 'inline-block',
  textAlign: 'end',
  marginRight: theme.spacing(0.5),
}))

const ButtonModal = styled(Box)(({ theme }) => ({
  button: {
    fontSize: 20,
  },
  display: 'flex',
  justifyContent: 'end',
  margin: theme.spacing(5),
}))

export default AccountManager
