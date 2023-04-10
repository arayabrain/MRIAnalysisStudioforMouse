import {
  Box,
  Button,
  FormControlLabel,
  Input,
  Radio,
  RadioGroup,
  styled,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import DatabaseTableComponent from 'components/DatabaseTable'
import React, { useState, DragEvent, Fragment, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { getNanoId } from 'utils/nanoid/NanoIdUtils'
import { defaultDatabase, PopupSearch, Viewer } from '../Database'
import ImageView from 'components/ImageView'
import { onGet, onSort } from 'utils/database'

const columns = [
  { title: 'User', name: 'user_name', filter: true },
  { title: 'Date', name: 'recording_time', filter: true },
  { title: 'Session', name: 'sessions', child: 'label', filter: true },
  { title: 'Dataset', name: 'datatypes', child: 'label', filter: true },
  { title: 'Type', name: 'type', filter: true },
  { title: 'Protocol', name: 'protocol', filter: true },
]

type ProjectAdd = {
  project_name: string
  project_type: number
  image_count: number
  protocol: string
  id: string
}

type DataWithin = {
  id: string
  data: ProjectAdd[]
  name: string
}

type DataFactor = {
  within: DataWithin[]
} & DataWithin

type RowDrag = {
  label: string
  protocol: string
  type: string
  image?: {
    image_url: string
    attributes: { [key: string]: any }
  }
}

const nameDefault = 'DEFAULT'

const ProjectFormComponent = () => {
  const [searchParams] = useSearchParams()

  const idEdit = searchParams.get('id')
  const [viewer, setViewer] = useState<Viewer>({ open: false, url: '' })
  const [orderBy, setOrdeBy] = useState<'ASC' | 'DESC' | undefined>()
  const [columnSort, setColumnSort] = useState<string>('')
  const [datasTable, setDatasTable] = useState<any[]>(defaultDatabase)
  const [projectName, setProjectName] = useState('Prj Name 1')
  const [projectLevel, setProjectLevel] = useState<'factor' | 'within-factor'>(
    'factor',
  )
  const [disabled, setDisabled] = useState({ left: false, right: false })
  const [openFilter, setOpenFilter] = useState(false)
  const [rowDrag, setRowDrag] = useState<(RowDrag | undefined) | RowDrag[]>()
  const [dataFactors, setDataFactors] = useState<DataFactor[]>([
    { name: nameDefault, within: [], id: getNanoId(), data: [] },
  ])
  const timeoutClick = useRef<NodeJS.Timeout | undefined>()
  const navigate = useNavigate()

  const onChangeName = (e: any) => {
    setProjectName(e.target.value)
  }

  const handleChangeLevel = (event: React.ChangeEvent<HTMLInputElement>) => {
    const type = event.target.value as 'within-factor' | 'factor'
    setProjectLevel(type)
    let within: DataWithin[] = []
    if (type === 'within-factor') {
      within = [{ name: nameDefault, id: getNanoId(), data: [] }]
    }
    setDataFactors([{ name: nameDefault, within, id: getNanoId(), data: [] }])
  }

  const onAddBetween = () => {
    setDataFactors((pre) => [
      ...pre,
      { name: nameDefault, within: [], id: getNanoId(), data: [] },
    ])
  }

  const onAddWithin = (idFactor: string) => {
    setDataFactors((pre) =>
      pre.map((p) => {
        if (p.id === idFactor) {
          return {
            ...p,
            within: [
              ...p.within,
              { name: nameDefault, within: [], id: getNanoId(), data: [] },
            ],
          }
        }
        return p
      }),
    )
  }

  const onDeleteFactor = (row: DataFactor) => {
    setDataFactors((pre) => pre.filter((e) => e.id !== row.id))
  }

  const onDeleteWithin = (factor: DataFactor, row: DataWithin) => {
    setDataFactors((pre) =>
      pre.map((p) => {
        if (p.id === factor.id) {
          return { ...p, within: p.within.filter((w) => w.id !== row.id) }
        }
        return p
      }),
    )
  }

  const onDeleteDataWithin = (
    factor: DataFactor,
    within: DataWithin,
    row: ProjectAdd,
  ) => {
    setDataFactors((pre) =>
      pre.map((p) => {
        if (p.id === factor.id) {
          return {
            ...p,
            within: p.within.map((w) => {
              if (w.id === within.id) {
                return { ...w, data: w.data.filter((d) => d.id !== row.id) }
              }
              return w
            }),
          }
        }
        return p
      }),
    )
  }

  const onDeleteDataFactor = (factor: DataFactor, row: ProjectAdd) => {
    setDataFactors((pre) =>
      pre.map((p) => {
        if (p.id === factor.id) {
          return { ...p, data: p.data.filter((d) => d.id !== row.id) }
        }
        return p
      }),
    )
  }

  const onDragRow = (row: any) => {
    setRowDrag(row)
  }

  const onDragEnd = (row: any) => {
    setRowDrag(undefined)
  }

  const onMouseOver = (factor: DataFactor, within?: DataWithin) => {
    onDropData(factor, within)
    setRowDrag(undefined)
  }

  const onDropData = (factor: DataFactor, within?: DataWithin) => {
    if (!Array.isArray(rowDrag) && !rowDrag?.image) {
      return
    }
    let newData: any[] = []
    if (!Array.isArray(rowDrag)) {
      newData = [
        {
          id: getNanoId(),
          project_name: rowDrag.label,
          image_count: 1,
          project_type: rowDrag.type,
          protocol: rowDrag.protocol,
          image_url: rowDrag.image?.image_url,
          jsonData: rowDrag.image?.attributes,
        },
      ]
    } else if (Array.isArray(rowDrag)) {
      newData = rowDrag.map((row) => ({
        id: getNanoId(),
        project_name: row.label,
        image_count: 1,
        project_type: row.type,
        protocol: row.protocol,
        image_url: row.image?.image_url,
        jsonData: row.image?.attributes,
      }))
    }
    if (projectLevel !== 'within-factor') {
      setDataFactors((pre) =>
        pre.map((p) => {
          if (p.id === factor.id) {
            return { ...p, data: [...p.data, ...newData] }
          }
          return p
        }),
      )
      return
    }
    if (within) {
      setDataFactors((pre) =>
        pre.map((p) => {
          if (p.id === factor.id) {
            return {
              ...p,
              within: p.within.map((w) => {
                if (w.id === within.id) {
                  return { ...w, data: [...w.data, ...newData] }
                }
                return w
              }),
            }
          }
          return p
        }),
      )
    }
  }

  const onDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
  }

  const onDragLeave = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
  }

  const onChangeNameFactor = (factor: DataFactor, value: string) => {
    setDataFactors((pre) =>
      pre.map((p) => {
        if (p.id === factor.id) {
          return { ...p, name: value }
        }
        return p
      }),
    )
  }

  const onChangeNameWithinFactor = (
    factor: DataFactor,
    within: DataWithin,
    value: string,
  ) => {
    setDataFactors((pre) =>
      pre.map((p) => {
        if (p.id === factor.id) {
          return {
            ...p,
            within: p.within.map((w) => {
              if (w.id === within.id) {
                return { ...w, name: value }
              }
              return w
            }),
          }
        }
        return p
      }),
    )
  }

  const renderData = (
    data: ProjectAdd[],
    style: any,
    onDelete?: (row: ProjectAdd) => any,
  ) => {
    return data.map((e, index) => (
      <BoxItem
        key={`${e.id}_${index}`}
        style={style}
        onClick={() => rowDataClick(e)}
      >
        <TypographyBoxItem>{e.project_name}</TypographyBoxItem>
        <TypographyBoxItem>{e.project_type}</TypographyBoxItem>
        <TypographyBoxItem>{e.protocol}</TypographyBoxItem>
        <Box
          style={{ display: 'flex', justifyContent: 'flex-end', width: '100%' }}
        >
          <Button
            onClick={(event) => {
              event.preventDefault()
              event.stopPropagation()
              onDelete?.(e)
            }}
          >
            <DeleteIcon fontSize="small" sx={{ color: 'red' }} />
          </Button>
        </Box>
      </BoxItem>
    ))
  }

  const onCloseImageView = () => {
    setViewer({ open: false, url: '' })
  }

  const rowClick = (row: any) => {
    if (!row?.image?.image_url) return
    const view = {
      open: true,
      url: row.image.image_url,
      id: row.id,
      session_id: row.session_id,
      parent_id: row.parent_id,
      jsonData: row.image.attributes,
    }
    const checkNext = onGet(defaultDatabase as any, view)
    const checkPre = onGet(
      JSON.parse(JSON.stringify(defaultDatabase)).reverse() as any,
      view,
      true,
    )
    setDisabled({ left: !checkPre, right: !checkNext })
    setViewer(view)
  }

  const rowDataClick = (row: any) => {
    if (!row?.image_url || !timeoutClick.current) {
      timeoutClick.current = setTimeout(() => {
        timeoutClick.current = undefined
      }, 300)
      return
    }
    setViewer({
      open: true,
      url: row.image_url,
      jsonData: row.jsonData,
    })
    setDisabled({ left: true, right: true })
  }

  const handleSort = (orderKey: string) => {
    setColumnSort(orderKey)
    let typeOrder: 'ASC' | 'DESC' | undefined = undefined
    if (!orderBy || orderKey !== columnSort) {
      typeOrder = 'ASC'
    } else if (orderBy === 'ASC') {
      typeOrder = 'DESC'
    }
    setOrdeBy(typeOrder)
    if (!typeOrder) {
      setDatasTable(defaultDatabase)
      return
    }
    const { data } = onSort(datasTable, typeOrder, orderKey, 'tree')
    setDatasTable(data)
  }

  const onNext = () => {
    const imageNext = onGet(defaultDatabase as any, viewer)
    rowClick(imageNext)
  }

  const onPrevious = () => {
    const datas = JSON.parse(JSON.stringify(defaultDatabase))
    const imageNext = onGet(datas.reverse() as any, viewer, true)
    rowClick(imageNext)
  }

  return (
    <ProjectsWrapper>
      {openFilter && <PopupSearch onClose={() => setOpenFilter(false)} />}
      <ImageView
        disabled={disabled}
        url={viewer.url}
        open={viewer.open}
        jsonData={viewer.jsonData}
        onClose={onCloseImageView}
        onNext={onNext}
        onPrevious={onPrevious}
      />
      <InputName value={projectName} onChange={onChangeName} />
      <BoxOptions
        aria-labelledby="demo-radio-buttons-group-label"
        value={projectLevel}
        name="radio-buttons-group"
        onChange={handleChangeLevel}
      >
        <FormControlLabel
          value="factor"
          control={<Radio />}
          label="Between factor"
        />
        <FormControlLabel
          value="within-factor"
          control={<Radio />}
          label="Between factor-within factor"
        />
      </BoxOptions>
      <DropAndDropBox>
        <DragBox>
          {dataFactors.map((factor, index) => {
            return (
              <Fragment key={factor.id}>
                <BoxFactor>
                  <Input
                    onChange={(e) => onChangeNameFactor(factor, e.target.value)}
                    style={{ width: 'calc(100% - 64px)' }}
                    value={
                      factor.name === nameDefault
                        ? `Between factor name ${index}`
                        : factor.name
                    }
                  />
                  <Button onClick={() => onDeleteFactor(factor)}>
                    <DeleteIcon fontSize="small" sx={{ color: 'red' }} />
                  </Button>
                  {projectLevel === 'within-factor' ? (
                    factor.within.map((within, indexWithin) => (
                      <BoxFactor key={within.id} style={{ marginLeft: 24 }}>
                        <Input
                          onChange={(e) =>
                            onChangeNameWithinFactor(
                              factor,
                              within,
                              e.target.value,
                            )
                          }
                          style={{ width: 'calc(100% - 64px)' }}
                          value={
                            within.name === nameDefault
                              ? `Within factor name ${indexWithin}`
                              : within.name
                          }
                        />
                        <Button onClick={() => onDeleteWithin(factor, within)}>
                          <DeleteIcon fontSize="small" sx={{ color: 'red' }} />
                        </Button>
                        {renderData(within.data, { marginLeft: 48 }, (row) => {
                          onDeleteDataWithin(factor, within, row)
                        })}
                        <BoxDrag
                          style={{
                            borderBottom: rowDrag ? '1px dashed red' : '',
                          }}
                          onDrop={() => onDropData(factor, within)}
                          onMouseOver={() => onMouseOver(factor, within)}
                          onDragOver={onDragOver}
                          onDragLeave={onDragLeave}
                        />
                      </BoxFactor>
                    ))
                  ) : (
                    <>
                      {renderData(factor.data, { marginLeft: 24 }, (row) => {
                        onDeleteDataFactor(factor, row)
                      })}
                      <BoxDrag
                        style={{
                          borderBottom: rowDrag ? '1px dashed red' : '',
                        }}
                        onDrop={() => onDropData(factor)}
                        onDragOver={onDragOver}
                        onDragLeave={onDragLeave}
                        onMouseOver={() => onMouseOver(factor)}
                      />
                    </>
                  )}
                </BoxFactor>
                {projectLevel === 'within-factor' && dataFactors.length ? (
                  <NewRowButton
                    onClick={() => onAddWithin(factor.id)}
                    style={{ marginLeft: 24 }}
                  >
                    + Add Within Factor
                  </NewRowButton>
                ) : null}
              </Fragment>
            )
          })}
          <NewRowButton onClick={onAddBetween}>
            + Add Between Factor
          </NewRowButton>
        </DragBox>
        <DropBox>
          <BoxFilter>
            <ButtonFilter
              onClick={() => setOpenFilter(true)}
              style={{ margin: '0 26px 0 0' }}
            >
              Filter
            </ButtonFilter>
          </BoxFilter>
          <DatabaseTableComponent
            onSort={handleSort}
            orderKey={columnSort}
            orderBy={orderBy}
            rowClick={rowClick}
            defaultExpand
            onDrag={onDragRow}
            onDragEnd={onDragEnd}
            draggable
            data={datasTable}
            columns={columns}
          />
        </DropBox>
      </DropAndDropBox>
      <Box
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
        }}
      >
        <ButtonFilter onClick={() => navigate('/projects')}>
          {idEdit ? 'Ok' : 'Add'}
        </ButtonFilter>
        <ButtonFilter onClick={() => navigate('/projects')}>
          Cancel
        </ButtonFilter>
      </Box>
    </ProjectsWrapper>
  )
}

const BoxItem = styled(Box)({
  display: 'flex',
  height: 40,
  alignItems: 'center',
  borderBottom: '1px solid rgba(0,0,0,0.8)',
  paddingLeft: 16,
  marginBottom: 4,
})

const TypographyBoxItem = styled(Box)({
  minWidth: 120,
})

const BoxDrag = styled(Box)({
  paddingBottom: 24,
  width: '100%',
  borderWidth: 1,
})

const BoxFactor = styled(Box)({})

const ProjectsWrapper = styled(Box)(({ theme }) => ({
  width: '100%',
  padding: theme.spacing(2),
  overflow: 'auto',
  height: 'calc(100% - 32px)',
  marginBottom: theme.spacing(3),
}))

const BoxOptions = styled(RadioGroup)(({ theme }) => ({
  width: '100%',
  padding: theme.spacing(1, 2),
}))

const InputName = styled('input')(({ theme }) => ({
  padding: theme.spacing(1),
  outline: 'none',
  borderColor: 'transparent',
  fontSize: 18,
  width: 'calc(100% - 32px)',
  '&:focus': {
    borderColor: '#000',
  },
  display: 'block',
  borderWidth: 1,
}))

const DropAndDropBox = styled(Box)(({ theme }) => ({
  width: '100%',
  display: 'flex',
  gap: theme.spacing(2),
}))

const DragBox = styled(Box)(({ theme }) => ({
  width: '40%',
  padding: theme.spacing(1, 2),
  border: '1px solid #000',
  minHeight: 100,
}))

const DropBox = styled(Box)(({ theme }) => ({
  width: '60%',
  padding: theme.spacing(1, 2),
  border: '1px solid #dedede',
}))

const NewRowButton = styled(Button)(({ theme }) => ({
  width: '60%',
  padding: theme.spacing(1, 2),
  borderStyle: 'dashed',
  borderWidth: 1,
  margin: theme.spacing(1, 0),
}))

const ButtonFilter = styled(Button)(({ theme }) => ({
  margin: theme.spacing(2, 1),
  minWidth: 80,
  paddingLeft: theme.spacing(2),
  paddingRight: theme.spacing(2),
  color: '#ffffff',
  backgroundColor: '#283237 !important',
}))

const BoxFilter = styled(Box)({
  display: 'flex',
  marginBottom: 10,
  justifyContent: 'flex-end',
})

export default ProjectFormComponent
