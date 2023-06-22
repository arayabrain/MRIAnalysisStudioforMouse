import { Box, Button, IconButton, styled, TextField } from '@mui/material'
import { ChangeEvent, useCallback, useEffect, useMemo, useState } from 'react'
import DatabaseTableComponent, { Column } from 'components/DatabaseTable'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import CloseIcon from '@mui/icons-material/Close'
import ImageView from 'components/ImageView'
import ModalDeleteAccount from 'components/ModalDeleteAccount'
import {
  onFilterValue,
  onGet,
  onRowClick,
  onSort,
  OrderKey,
} from 'utils/database'
import { User, useUser } from 'providers'
import { isReseacher } from 'utils/auth'
import { deleteRawDb, getDataBaseList, getDataBaseTree } from 'api/rawdb'
import { DATABASE_URL_HOST } from 'const/API'
import Loading from 'components/common/Loading'
import { useSearchParams } from 'react-router-dom'

type PopupSearchProps = {
  onClose?: () => any
  onFilter?: (values: { [key: string]: string }) => any
  defaultValue?: { [key: string]: string }
}

export const PopupSearch = ({
  onClose,
  defaultValue = {},
  onFilter,
}: PopupSearchProps) => {
  const [values, setValues] = useState(defaultValue)

  const handleFilter = () => {
    onFilter?.(values)
    onClose?.()
  }

  const onChange = (
    event: ChangeEvent<HTMLTextAreaElement | HTMLInputElement>,
  ) => {
    setValues({ ...values, [event.target.name]: event.target.value })
  }

  return (
    <Popup>
      <PopupInner>
        <HeaderTitle>
          <span>Filter</span>
          <ButtonControl onClick={onClose}>
            <CloseIcon />
          </ButtonControl>
        </HeaderTitle>
        <InputSearch
          onChange={onChange}
          name={'session_label'}
          label="Session"
          variant="outlined"
          value={values.session_label}
        />
        <InputSearch
          onChange={onChange}
          name={'datatypes_label'}
          label="Datatype"
          variant="outlined"
          value={values.datatypes_label}
        />
        <InputSearch
          onChange={onChange}
          name={'type'}
          label="Type"
          variant="outlined"
          value={values.type}
        />
        <InputSearch
          onChange={onChange}
          name={'protocol'}
          label="Protocol"
          variant="outlined"
          value={values.protocol}
        />
        <Button variant="contained" onClick={handleFilter}>
          Filter
        </Button>
      </PopupInner>
    </Popup>
  )
}

export type ObjectType = {
  [key: string]: ObjectType | string | number | number[]
}

export type Image = {
  id: number
  parent_id: number
  session_id: number
  label: string
  image: {
    id: number
    parent_id: number
    image_url: string
    image_attributes: ObjectType
  }
}

export type Viewer = {
  open: boolean
  url: string
  jsonData?: ObjectType
  id?: number | string
  session_id?: number
  parent_id?: string
  image?: ImagesDatabase | RecordList
}

export type ImagesDatabase = {
  id: number
  parent_id: string
  image_url: string
  datatype_label?: string
  type?: string
  image_attributes: ObjectType
  session_id?: number
  record_index?: number
  subject_index?: number
  session_index?: number
  datatype_index?: number
  image_index?: number
}

export type DatatypesDatabase = {
  id: string
  parent_id: string
  label: string
  images: ImagesDatabase[]
}

export type SessionsDatabase = {
  id: string
  parent_id: string
  session_index?: number
  label: string
  datatypes: DatatypesDatabase[]
  subject_index?: number
}

export type SubjectDatabase = {
  id: string
  parent_id: string
  label: string
  sessions: SessionsDatabase[]
  subject_index?: number
}

export type RecordDatabase = {
  id: number
  lab_name: string
  user_name: string
  recording_time: string
  created_time: string
  updated_time: string
  subjects: SubjectDatabase[]
}

export type DatabaseData = {
  pagenation: {
    page: number
    limit: number
    total: number
    total_pages: number
  }
  records: RecordDatabase[]
}

export type RecordList = {
  id: number
  lab_name: string
  user_name: string
  recording_time: string
  subject_label: string
  session_label: string
  datatypes_label: string
  image_id: number
  image_url: string
  image_attributes: {
    size: number[]
    type: string
    protocol: string
    voxel_size: number[]
  }
  created_time: string
  updated_time: string
}

export type DatabaseListData = {
  pagenation: {
    page: number
    limit: number
    total: number
    total_pages: number
  }
  records: RecordList[]
}

export const defaultDatabase: DatabaseData = {
  pagenation: {
    page: 0,
    limit: 0,
    total: 0,
    total_pages: 0,
  },
  records: [],
}

export const columns = (
  rowClick: Function,
  setOpenDelete: Function,
  type: 'tree' | 'list' = 'tree',
  user?: User,
): Column[] => [
  { title: 'Lab', name: 'lab_name', filter: true, width: 100 },
  { title: 'User', name: 'user_name', filter: true },
  { title: 'Date', name: 'recording_time', filter: true, width: 110 },
  {
    title: 'Subject',
    name: type === 'tree' ? 'subject' : 'subject_label',
    filter: true,
  },
  {
    title: 'Session',
    name: type === 'tree' ? 'session' : 'session_label',
    child: 'label',
    filter: true,
    width: 100,
  },
  {
    title: 'Datatype',
    name: type === 'tree' ? 'datatype' : 'datatypes_label',
    filter: true,
    width: 100,
    styleTitle: { fontWeight: 400 },
  },
  {
    title: 'Image ID',
    name: 'id',
    styleTitle: { fontWeight: 400 },
    width: 100,
    render: (record) => {
      if (!(record as ImagesDatabase).image_attributes) return
      return (
        <div style={{ textAlign: 'center' }}>
          {(record as ImagesDatabase).id}
        </div>
      )
    },
  },
  {
    title: 'Type',
    name: 'image_attributes.image_type',
    filter: true,
    width: 70,
    styleTitle: { fontWeight: 400 },
  },
  {
    title: 'Protocol',
    name: 'image_attributes.protocol',
    filter: true,
    styleTitle: { fontWeight: 400 },
  },
  {
    title: 'Size',
    name: 'image_attributes.scale',
    filter: true,
    styleTitle: { fontWeight: 400 },
    render: (_, v) => JSON.stringify(v),
  },
  {
    title: 'Voxel size',
    name: 'image_attributes.voxel',
    filter: true,
    styleTitle: { fontWeight: 400 },
    width: 130,
    render: (_, v) => JSON.stringify(v),
  },
  {
    title: '',
    name: 'action',
    render: (data) => {
      if (isReseacher(user?.role)) return null
      return (
        <BoxButton>
          <ButtonControl
            aria-label="Example"
            onClick={(event) => {
              event.preventDefault()
              event.stopPropagation()
              rowClick?.(data)
            }}
          >
            <EditIcon fontSize="small" color={'inherit'} />
          </ButtonControl>
          <ButtonControl
            aria-label="Example"
            onClick={(event) => {
              event.preventDefault()
              event.stopPropagation()
              setOpenDelete?.(true, data?.id)
            }}
          >
            <DeleteIcon fontSize="small" sx={{ color: 'red' }} />
          </ButtonControl>
        </BoxButton>
      )
    },
  },
]

const Database = () => {
  const [openPopup, setOpenPopup] = useState(false)
  const [viewer, setViewer] = useState<Viewer>({ open: false, url: '', id: '' })
  const [databases, setDatabases] = useState<DatabaseData | DatabaseListData>()
  const [{ openDelete, idDelete }, setOpenDelete] = useState<{
    openDelete: boolean
    idDelete: number | string
  }>({
    openDelete: false,
    idDelete: '',
  })
  const [{ orderBy, type, columnSort }, setOrderByAndTypeAndSort] = useState<{
    orderBy: 'ASC' | 'DESC' | ''
    type: 'tree' | 'list'
    columnSort: string
  }>({ orderBy: '', type: 'tree', columnSort: '' })

  // const [columnSort, setColumnSort] = useState<string>('')
  const [initDatabases, setInitDatabases] =
    useState<DatabaseData>(defaultDatabase)
  const [disabled, setDisabled] = useState({ left: false, right: false })
  const [isLoading, setIsLoading] = useState(false)
  const { user } = useUser()
  const [searchParams, setParams] = useSearchParams()
  const onCloseImageView = () => {
    setViewer({ open: false, url: '', id: '' })
  }

  const queryFilter: {[key: string]: string } = useMemo(() => {
    return {
      session_label: searchParams.get('session_label') || '',
      datatypes_label: searchParams.get('datatypes_label') || '',
      type: searchParams.get('type') || '',
      protocol: searchParams.get('protocol') || '',
    }
  }, [searchParams])

  const fetchData = useCallback(async () => {
    setIsLoading(true)
    let data
    try {
      let api = getDataBaseList
      if (type === 'tree') {
        api = getDataBaseTree
      }
      data = await api()
      const records = onFilterValue(queryFilter, data, type)
      setDatabases({ ...data, records })
      setInitDatabases(data)
    } finally {
      setIsLoading(false)
    }
    //eslint-disable-next-line
  }, [type])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const rowClick = async (row: ImagesDatabase | RecordList) => {
    if (!databases) return
    const { view, checkNext, checkPre } = await onRowClick(databases, row, type)
    setViewer(view)
    setDisabled({
      left: type === 'list' || !checkPre,
      right: type === 'list' || !checkNext,
    })
  }

  const handleCloseDelete = () => {
    setOpenDelete({ openDelete: false, idDelete: '' })
  }

  const onDelete = async () => {
    handleCloseDelete()
    setIsLoading(true)
    try {
      await deleteRawDb(idDelete)
      fetchData()
    } catch {
      setIsLoading(false)
    }
  }

  const handleSort = (orderKey: string, orderByValue: 'DESC' | 'ASC' | '') => {
    if (!initDatabases) return
    const records = onFilterValue(queryFilter, initDatabases, type)
    const data = onSort(
      JSON.parse(JSON.stringify(records)),
      orderByValue,
      orderKey as OrderKey,
      type,
    )
    setDatabases({ ...initDatabases, records: data as RecordDatabase[] })
    setOrderByAndTypeAndSort((pre) => ({
      ...pre,
      orderBy: orderByValue,
      columnSort: orderKey,
    }))
  }

  const onNext = async () => {
    if (!viewer.image) return
    const imageNext = onGet(databases as any, viewer.image, false, type)
    if (imageNext) await rowClick(imageNext)
  }

  const onPrevious = async () => {
    if (!viewer.image || !databases) return
    const imagePre = onGet(databases, viewer.image, true, type)
    if (imagePre) await rowClick(imagePre)
  }

  const onFilter = (value: { [key: string]: string }) => {
    if (!databases) return
    if (!Object.keys(value).length) return
    const records = onFilterValue(value, initDatabases, type)
    const data = onSort(
      JSON.parse(JSON.stringify(records)),
      orderBy,
      columnSort as OrderKey,
      type,
    )
    setDatabases({ ...databases, records: data as RecordDatabase[] })
    const newParams = Object.keys(value)
      .map((key) => value[key] && `${key}=${value[key]}`)
      .join('&')
    setParams(newParams)
  }

  const setType = (type: 'tree' | 'list') => {
    setOrderByAndTypeAndSort({ type, orderBy: '', columnSort: '' })
  }

  const handleClear = () => {
    setParams('')
    const data = onSort(
      JSON.parse(JSON.stringify(initDatabases.records)),
      orderBy,
      columnSort as OrderKey,
      type,
    )
    setDatabases({ ...initDatabases, records: data as RecordDatabase[] })
  }

  const onDeleteImage = (flag: boolean, idRemove: string | number) => {
    setOpenDelete({ openDelete: flag, idDelete: idRemove })
  }

  return (
    <DatabaseWrapper>
      <ModalDeleteAccount
        titleSubmit="Delete Image"
        description={`Are you sure delete?\n`}
        onClose={handleCloseDelete}
        open={openDelete}
        onSubmit={onDelete}
      />
      <ProjectsTitle>
        <span>Database</span>
        <Box sx={{ display: 'flex', gap: 5 }}>
          {
            Object.keys(queryFilter).some((key) => !!queryFilter[key]) &&
              <Button variant="contained" onClick={handleClear}>
                  Clear Filter
              </Button>
          }
          <ButtonFilter
            onClick={() => setOpenPopup(true)}
            style={{ margin: '0 26px 0 0' }}
          >
            Filter
          </ButtonFilter>
        </Box>
      </ProjectsTitle>
      <BoxSelectTypeView>
        <Box
          onClick={() => {
            if (type === 'tree') return
            setType('tree')
            setParams('')
          }}
          style={{
            marginRight: 4,
            fontWeight: type === 'tree' ? 700 : 500,
            cursor: 'pointer',
            color: type === 'tree' ? '' : '#4687f4',
          }}
        >
          Tree
        </Box>
        /
        <Box
          onClick={() => {
            if (type === 'list') return
            setType('list')
            setParams('')
          }}
          style={{
            marginLeft: 4,
            fontWeight: type === 'list' ? 700 : 500,
            cursor: 'pointer',
            color: type === 'list' ? '' : '#4687f4',
          }}
        >
          List
        </Box>
      </BoxSelectTypeView>
      {openPopup && (
        <PopupSearch
          onClose={() => setOpenPopup(false)}
          defaultValue={queryFilter}
          onFilter={onFilter}
        />
      )}
      <DatabaseTableComponent
        addProject={false}
        defaultExpand
        onSort={handleSort}
        rowClick={rowClick}
        orderKey={columnSort}
        orderBy={orderBy}
        data={databases && databases.records}
        columns={columns(rowClick, onDeleteImage, type, user)}
      />
      {viewer.url && viewer.open && (
        <ImageView
          disabled={disabled}
          url={`${DATABASE_URL_HOST}${viewer.url}`}
          open={viewer.open}
          jsonData={viewer.jsonData}
          onClose={onCloseImageView}
          onNext={onNext}
          onPrevious={onPrevious}
          id={Number(viewer.id)}
        />
      )}
      {isLoading && <Loading />}
    </DatabaseWrapper>
  )
}

const DatabaseWrapper = styled(Box)(({ theme }) => ({
  width: '100%',
  padding: theme.spacing(2),
  overflow: 'auto',
}))

const HeaderTitle = styled('h1')(() => ({
  width: '100%',
  display: 'flex',
  justifyContent: 'space-between',
}))

const Popup = styled(Box)(() => ({
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100%',
  height: '100vh',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  backgroundColor: '#cccccc80',
  zIndex: 9999,
}))

const PopupInner = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2, 3),
  backgroundColor: '#fff',
  borderRadius: theme.spacing(1),
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(2),
}))

const InputSearch = styled(TextField)(() => ({
  minWidth: 250,
}))

const BoxButton = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'flex-end',
  gap: theme.spacing(1),
}))

const ButtonFilter = styled(Button)(({ theme }) => ({
  margin: theme.spacing(2, 0),
  minWidth: 80,
  paddingLeft: theme.spacing(2),
  paddingRight: theme.spacing(2),
  backgroundColor: '#283237 !important',
  color: '#ffffff',
}))

const ButtonControl = styled(IconButton)(({ theme }) => ({
  padding: theme.spacing(0, 1),
  width: 30,
  height: 30,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}))

const ProjectsTitle = styled('h1')(() => ({
  width: '100%',
  display: 'flex',
  justifyContent: 'space-between',
}))

const BoxSelectTypeView = styled(Box)({
  display: 'flex',
  alignItems: 'center',
  marginBottom: 16,
})

export default Database
