import {
  Box,
  Button,
  FormControlLabel,
  Input,
  Radio,
  RadioGroup,
  styled,
  Typography,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import DatabaseTableComponent, { Column } from 'components/DatabaseTable'
import React, {
  useState,
  DragEvent,
  Fragment,
  useRef,
  CSSProperties,
  useEffect,
  useMemo,
} from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { getNanoId } from 'utils/nanoid/NanoIdUtils'
import {
  DatabaseData,
  defaultDatabase,
  ImagesDatabase,
  PopupSearch,
  Viewer,
} from '../Database'
import ImageView from 'components/ImageView'
import {
  onFilterValue,
  onGet,
  onRowClick,
  onSort,
  OrderKey,
} from 'utils/database'
import { ObjectType } from '../Database'
import { ChangeEvent } from 'react'
import { RecordDatabase } from '../Database'
import { useDispatch } from 'react-redux'
import { getDatasetList } from 'store/slice/Dataset/DatasetAction'
import { ProjectTypeValue } from 'store/slice/Project/ProjectType'
import {
  createProject,
  editProject,
  getProjectId,
} from 'store/slice/Project/ProjectAction'
import Loading from 'components/common/Loading'
import { getDataBaseTree } from 'api/rawdb'
import { DATABASE_URL_HOST } from 'const/API'
import { selectDataset } from 'store/slice/Dataset/DatasetSelector'
import { useSelector } from 'react-redux'
import { Dataset } from 'store/slice/Dataset/DatasetType'
import { selectCurrentProject } from 'store/slice/Project/ProjectSelector'
import { resetCurrentProject } from 'store/slice/Project/ProjectSlice'
import { reset } from 'store/slice/Dataset/DatasetSlice'
import { setLoadingExpriment } from 'store/slice/Experiments/ExperimentsSlice'
import { setRunBtnOption } from 'store/slice/Pipeline/PipelineSlice'
import { RUN_BTN_OPTIONS } from 'store/slice/Pipeline/PipelineType'

const columns: Column[] = [
  { title: 'Lab', name: 'lab_name', filter: true, width: 100 },
  { title: 'User', name: 'user_name', filter: true, width: 100 },
  { title: 'Date', name: 'recording_time', filter: true, width: 130 },
  { title: 'Subject', name: 'subject', filter: true, width: 120 },
  {
    title: 'Session',
    name: 'session',
    child: 'label',
    filter: true,
    width: 190,
  },
  {
    title: 'Datatype',
    name: 'datatype',
    styleTitle: { fontWeight: 400 },
    filter: true,
    width: 100,
  },
  {
    title: 'Image ID',
    name: 'id',
    width: 100,
    styleTitle: { fontWeight: 400 },
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
    styleTitle: { fontWeight: 400 },
    width: 70,
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
    render: (_, value) => JSON.stringify(value),
  },
  {
    title: 'Voxel size',
    name: 'image_attributes.voxel',
    filter: true,
    width: 110,
    styleTitle: { fontWeight: 400 },
    render: (_, value) => JSON.stringify(value),
  },
]

type ProjectAdd = {
  project_name?: string
  project_type?: string
  image_count: number
  image_url: string
  protocol: string
  id: string
  image_id: number
  jsonData: ObjectType
}

type DataWithin = {
  id: string
  data: ProjectAdd[]
  name: string
}

type DataFactor = {
  within: DataWithin[]
} & DataWithin

const nameDefault = 'DEFAULT'

const defaultFactor = [
  { name: nameDefault, within: [], id: getNanoId(), data: [] },
]

const remapDatasetToDataFactor = ({
  dataset,
}: Dataset): { datasets: DataFactor[]; ids: number[] } => {
  if (!dataset) return { ids: [], datasets: defaultFactor }
  let ids: number[] = []
  const datasets = dataset.map((sub) => ({
    id: sub.id,
    name: sub.folder_name || nameDefault,
    within: (sub.sub_folders || []).map((sub_within) => ({
      id: sub_within.id,
      name: sub_within.folder_name,
      data: (sub_within.images || []).map((image) => {
        ids.push(image.id)
        return {
          project_name: image.attributes.datatype as string,
          project_type: image.attributes.image_type as string,
          id: String(image.id),
          image_count: 1,
          image_id: image.id,
          protocol: image.attributes.protocol as string,
          image_url: image.image_url,
          jsonData: image.attributes,
        }
      }),
    })),
    data: (sub.images || []).map((image) => {
      ids.push(image.id)
      return {
        project_name: image.attributes.datatype as string,
        project_type: image.attributes.image_type as string,
        id: String(image.id),
        image_count: 1,
        image_id: image.id,
        protocol: image.attributes.protocol as string,
        image_url: image.image_url,
        jsonData: image.attributes,
      }
    }),
  }))
  return { ids, datasets }
}

const ProjectFormComponent = () => {
  const [searchParams, setParams] = useSearchParams()
  const idEdit = searchParams.get('id')
  const [viewer, setViewer] = useState<Viewer>({ open: false, url: '' })
  const [orderBy, setOrdeBy] = useState<'ASC' | 'DESC' | ''>('')
  const [columnSort, setColumnSort] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const routeGoback = searchParams.get('back')
  const nodeId = searchParams.get('nodeId')
  const isPendingDrag = useRef(false)
  const dispatch = useDispatch()
  const navigate = useNavigate()

  const dataset = useSelector(selectDataset)
  const currentProject = useSelector(selectCurrentProject)

  const [databasese, setDatabases] = useState<DatabaseData>(defaultDatabase)
  const [initDatabases, setInitDatabases] =
    useState<DatabaseData>(defaultDatabase)
  const [projectName, setProjectName] = useState(
    currentProject?.project_name || 'Prj Name 1',
  )
  const [projectType, setProjectType] = useState<ProjectTypeValue>(
    currentProject?.project_type || ProjectTypeValue.FACTOR,
  )
  const [disabled, setDisabled] = useState({ left: false, right: false })
  const [openFilter, setOpenFilter] = useState(false)
  const [rowDrag, setRowDrag] = useState<ImagesDatabase | ImagesDatabase[]>()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const { datasets, ids } = useMemo(() => remapDatasetToDataFactor(dataset), [])
  const [dataFactors, setDataFactors] = useState<DataFactor[]>(datasets)
  const [imageIDs, setImageIDs] = useState<number[]>(ids)

  const timeoutClick = useRef<NodeJS.Timeout | undefined>()
  const [isEditName, setIsEditName] = useState(false)

  const errorProjectEmpty = useMemo(() => !projectName, [projectName])

  const queryFilter: {[key: string]: string } = useMemo(() => {
    return {
      session_label: searchParams.get('session_label') || '',
      datatypes_label: searchParams.get('datatypes_label') || '',
      type: searchParams.get('type') || '',
      protocol: searchParams.get('protocol') || '',
    }
  }, [searchParams])

  useEffect(() => {
    setLoading(true)
    if (!idEdit) {
      getDataTree().then(() => setLoading(false))
      return
    }
    Promise.all([
      dispatch(getDatasetList({ project_id: idEdit })),
      dispatch(
        getProjectId({
          project_id: idEdit,
          callback: () => setLoading(false),
        }),
      ),
      getDataTree(),
    ]).then(() => setLoading(false))
    return () => {
      dispatch(resetCurrentProject())
      dispatch(reset())
    }
    //eslint-disable-next-line
  }, [])

  useEffect(() => {
    const { datasets, ids } = remapDatasetToDataFactor(dataset)
    setDataFactors(datasets)
    setImageIDs(ids)
  }, [dataset])

  useEffect(() => {
    if (currentProject?.project_name) {
      setProjectName(currentProject?.project_name)
    }
  }, [currentProject?.project_name])

  useEffect(() => {
    if (currentProject?.project_type) {
      setProjectType(currentProject.project_type as number)
    }
  }, [currentProject?.project_type])

  const onFilter = (value: { [key: string]: string }) => {
    if (!initDatabases) return
    const records = onFilterValue(
      value,
      initDatabases,
      'tree',
    ) as RecordDatabase[]
    const data = onSort(
      JSON.parse(JSON.stringify(records)),
      orderBy,
      columnSort as OrderKey,
      'tree',
    ) as RecordDatabase[]
    setDatabases({ ...initDatabases, records: data })
    if (!Object.keys(value).length) return
    const newParams = Object.keys(value)
      .map((key) => value[key] && `${key}=${value[key]}`)
      .join('&')
    idEdit ? setParams(`id=${idEdit}&${newParams}${nodeId ? `&nodeId=${nodeId}` : ''}${routeGoback ? `&back=${routeGoback}` : ''}`) : setParams(newParams)
  }

  const getDataTree = async () => {
    try {
      const response = await getDataBaseTree()
      const records = onFilterValue(queryFilter, response, 'tree')
      setDatabases({...databasese, records: records as RecordDatabase[]})
      setInitDatabases(response)
    } catch {}
  }

  const onChangeName = (e: ChangeEvent<HTMLInputElement>) => {
    setProjectName(e.target.value)
  }

  const handleChangeLevel = (event: React.ChangeEvent<HTMLInputElement>) => {
    const type = Number(event.target.value) as ProjectTypeValue
    setProjectType(type)
    let within: DataWithin[] = []
    if (type === ProjectTypeValue.WITHIN_FACTOR) {
      within = [{ name: nameDefault, id: getNanoId(), data: [] }]
    }
    setImageIDs([])
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
    setImageIDs((pre) =>
      pre.filter((id) => {
        if (projectType === ProjectTypeValue.FACTOR) {
          return !row.data.find((rowData) => rowData.image_id === id)
        }
        return !row.within.find((w) => w.data.find((d) => d.image_id === id))
      }),
    )
    setDataFactors((pre) => pre.filter((e) => e.id !== row.id))
  }

  const onDeleteWithin = (factor: DataFactor, row: DataWithin) => {
    setImageIDs((pre) =>
      pre.filter((id) => !row.data.find((rowData) => rowData.image_id === id)),
    )
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
    setImageIDs((pre) => pre.filter((id) => id !== row.image_id))
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
    setImageIDs((pre) => pre.filter((id) => id !== row.image_id))
    setDataFactors((pre) =>
      pre.map((p) => {
        if (p.id === factor.id) {
          return { ...p, data: p.data.filter((d) => d.id !== row.id) }
        }
        return p
      }),
    )
  }

  const onDragRow = (row: ImagesDatabase[] = []) => {
    setRowDrag(row)
  }

  const onBeginDrag = () => {
    isPendingDrag.current = true
    const mouseup = () => {
      isPendingDrag.current = false
      window.removeEventListener('mouseup', mouseup)
    }
    window.addEventListener('mouseup', mouseup)
  }

  const onDragEnd = () => {
    setRowDrag(undefined)
  }

  const onMouseOver = (factor: DataFactor, within?: DataWithin) => {
    if (isPendingDrag.current) return
    onDropData(factor, within)
    setRowDrag(undefined)
  }

  const onDropData = (factor: DataFactor, within?: DataWithin) => {
    if (!Array.isArray(rowDrag) && !rowDrag?.image_url) {
      return
    }
    let newData: ProjectAdd[] = []
    const checkExistIdImage =
      imageIDs.length &&
      imageIDs.some((id) => {
        if (!Array.isArray(rowDrag)) return rowDrag.id === id
        return rowDrag.some((row) => row.id === id)
      })
    if (checkExistIdImage) {
      return alert('Duplicate images cannot be registered.')
    }
    const newIds = Array.isArray(rowDrag)
      ? rowDrag.map((row) => row.id)
      : [rowDrag.id]
    setImageIDs([...imageIDs, ...newIds])
    if (!Array.isArray(rowDrag)) {
      newData = [
        {
          id: getNanoId(),
          project_name: rowDrag.datatype_label,
          image_count: 1,
          image_id: rowDrag.id,
          project_type: rowDrag.image_attributes.image_type as string,
          protocol: rowDrag.image_attributes.protocol as string,
          image_url: rowDrag?.image_url,
          jsonData: rowDrag?.image_attributes,
        },
      ]
    } else if (Array.isArray(rowDrag)) {
      newData = rowDrag.map((row) => ({
        id: getNanoId(),
        project_name: row.datatype_label,
        image_count: 1,
        image_id: row.id,
        project_type: row.image_attributes.image_type as string,
        protocol: row.image_attributes.protocol as string,
        image_url: row?.image_url,
        jsonData: row?.image_attributes,
      }))
    }
    if (projectType === ProjectTypeValue.FACTOR) {
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
    style?: CSSProperties,
    onDelete?: (row: ProjectAdd) => void,
  ) => {
    return data.map((e, index) => (
      <BoxItem
        key={`${e.id}_${index}`}
        style={style}
        onClick={() => rowDataClick(e)}
      >
        <TypographyBoxItem style={{ minWidth: 40 }}>
          {e.image_id}
        </TypographyBoxItem>
        <TypographyBoxItem>{e.project_name}</TypographyBoxItem>
        <TypographyBoxItem style={{ minWidth: 80 }}>
          {e.project_type}
        </TypographyBoxItem>
        <TypographyBoxItem>{e.protocol}</TypographyBoxItem>
        <Box style={{ display: 'flex', justifyContent: 'flex-end', width: 64 }}>
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

  const rowClick = async (row: ImagesDatabase) => {
    const { view, checkNext, checkPre } = await onRowClick(databasese, row)
    setViewer(view)
    setDisabled({ left: !checkPre, right: !checkNext })
  }

  const rowDataClick = (row: ProjectAdd) => {
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
      id: row.image_id,
    })
    setDisabled({ left: true, right: true })
  }

  const handleSort = (orderKey: string, orderByValue: 'DESC' | 'ASC' | '') => {
    if (!initDatabases) return
    const filterValue = {
      session_label: searchParams.get('session_label') || '',
      datatypes_label: searchParams.get('datatypes_label') || '',
      type: searchParams.get('type') || '',
      protocol: searchParams.get('protocol') || '',
    }
    const records = onFilterValue(filterValue, initDatabases, 'tree')
    const data = onSort(
      JSON.parse(JSON.stringify(records)),
      orderByValue,
      orderKey as OrderKey,
    )
    setDatabases({ ...initDatabases, records: data as RecordDatabase[] })
    setColumnSort(orderKey)
    setOrdeBy(orderByValue)
  }

  const onNext = () => {
    if (!viewer.image) return
    const imageNext = onGet(databasese, viewer.image, false)
    if (imageNext) rowClick(imageNext as ImagesDatabase)
  }

  const onPrevious = () => {
    if (!viewer.image) return
    const imagePre = onGet(databasese, viewer.image, true)
    if (imagePre) rowClick(imagePre as ImagesDatabase)
  }

  const onCancle = () => {
    if (routeGoback) {
      navigate(`${routeGoback}&id=${idEdit}`, { state: { cancel: true } })
      dispatch(setLoadingExpriment({ loading: false }))
    } else {
      navigate('/projects')
    }
  }

  const generateName = (name: string, index: number, subject: string) => {
    if (name === nameDefault) {
      return `${subject} factor name ${index}`
    }
    return name
  }

  const getBorderDrag = (): string => {
    if (
      (Array.isArray(rowDrag) && rowDrag.length) ||
      (!Array.isArray(rowDrag) && !!rowDrag)
    ) {
      return '1px dashed red'
    }
    return ''
  }

  const onOk = async () => {
    if (errorProjectEmpty) return
    if (
      dataFactors.some((factor) => {
        return (
          !factor.name ||
          (factor.within.length && factor.within.some((within) => !within.name))
        )
      })
    ) {
      return
    }
    setLoading(true)
    const project = {
      project_name: projectName,
      project_type: projectType,
    }
    const dataset = dataFactors.map((factor, index) => ({
      folder_name: generateName(factor.name, index, 'Between'),
      source_image_ids: factor.data.map((d) => d.image_id),
      sub_folders: factor.within.map((within, iWithin) => ({
        folder_name: generateName(within.name, iWithin, 'Within'),
        source_image_ids: within.data.map((d) => d.image_id),
      })),
    }))
    if (idEdit) {
      dispatch(
        editProject({
          project,
          project_id: idEdit,
          dataset,
          callback: async (isSuccess: boolean) => {
            if (isSuccess) {
              if (nodeId) {
                await dispatch(setLoadingExpriment({ loading: true }))
                if (routeGoback) {
                  navigate(`${routeGoback}&id=${idEdit}`)
                }
              } else {
                onCancle()
              }
            }
            dispatch(
              setRunBtnOption({
                runBtnOption: RUN_BTN_OPTIONS.RUN_NEW,
                runAlreadyDisabled: true,
              }),
            )
            setLoading(false)
          },
        }),
        )
      } else {
        dispatch(
        createProject({
          project,
          dataset,
          callback: (isSuccess: boolean) => {
            if (isSuccess) {
              return onCancle()
            }
            dispatch(
              setRunBtnOption({
                runBtnOption: RUN_BTN_OPTIONS.RUN_NEW,
                runAlreadyDisabled: true,
              }),
            )
            setLoading(false)
          },
        }),
      )
    }
  }

  const handleClear = () => {
    idEdit ? setParams(`id=${idEdit}${nodeId ? `&nodeId=${nodeId}` : ''}${routeGoback ? `&back=${routeGoback}` : ''}`) : setParams('')
    const data = onSort(
      JSON.parse(JSON.stringify(initDatabases.records)),
      orderBy,
      columnSort as OrderKey,
    )
    setDatabases({ ...initDatabases, records: data as RecordDatabase[] })
  }

  return (
    <ProjectsWrapper>
      {openFilter && (
        <PopupSearch
          defaultValue={queryFilter}
          onFilter={onFilter}
          onClose={() => setOpenFilter(false)}
        />
      )}
      {viewer.url && viewer.open && (
        <ImageView
          editAttribute={false}
          disabled={disabled}
          url={viewer.url && `${DATABASE_URL_HOST}${viewer.url}`}
          open={viewer.open}
          jsonData={viewer.jsonData}
          onClose={onCloseImageView}
          onNext={onNext}
          onPrevious={onPrevious}
          id={Number(viewer.id)}
        />
      )}
      {isEditName ? (
        <Fragment>
          <InputName
            autoFocus
            onBlur={() => {
              if (errorProjectEmpty) return
              setIsEditName(false)
            }}
            value={projectName}
            onChange={onChangeName}
            style={{
              borderColor: errorProjectEmpty ? 'red' : '#000',
              borderStyle: 'solid',
            }}
          />
          {errorProjectEmpty && (
            <span style={{ fontSize: 12, color: 'red' }}>
              Project name can't empty
            </span>
          )}
        </Fragment>
      ) : (
        <TextName onClick={() => setIsEditName(true)}>{projectName}</TextName>
      )}
      <BoxOptions
        aria-labelledby="demo-radio-buttons-group-label"
        value={projectType}
        name="radio-buttons-group"
        onChange={handleChangeLevel}
      >
        <Box>
          <Box>
            <FormControlLabel
              value={ProjectTypeValue.FACTOR}
              control={<Radio />}
              label="Between factor"
              disabled={!!idEdit}
            />
          </Box>
          <FormControlLabel
            value={ProjectTypeValue.WITHIN_FACTOR}
            control={<Radio />}
            label="Between factor-within factor"
            disabled={!!idEdit}
          />
        </Box>
      </BoxOptions>
      <DropAndDropBox>
        <DragBox>
          {dataFactors.map((factor, index) => {
            return (
              <Fragment key={factor.id}>
                <BoxFactor>
                  <div>
                    <Input
                      error={!factor.name}
                      onChange={(e) =>
                        onChangeNameFactor(factor, e.target.value)
                      }
                      style={{ width: 'calc(100% - 64px)' }}
                      value={generateName(factor.name, index, 'Between')}
                    />
                    <Button onClick={() => onDeleteFactor(factor)}>
                      <DeleteIcon fontSize="small" sx={{ color: 'red' }} />
                    </Button>
                    {!factor.name && (
                      <div style={{ fontSize: 12, color: 'red' }}>
                        Factor name can't empty
                      </div>
                    )}
                  </div>
                  {projectType === ProjectTypeValue.WITHIN_FACTOR ? (
                    factor.within.map((within, iWithin) => (
                      <BoxFactor key={within.id} style={{ marginLeft: 24 }}>
                        <div>
                          <Input
                            error={!within.name}
                            onChange={(e) => {
                              const { value } = e.target
                              onChangeNameWithinFactor(factor, within, value)
                            }}
                            style={{ width: 'calc(100% - 64px)' }}
                            value={generateName(within.name, iWithin, 'Within')}
                          />
                          <Button
                            onClick={() => onDeleteWithin(factor, within)}
                          >
                            <DeleteIcon
                              fontSize="small"
                              sx={{ color: 'red' }}
                            />
                          </Button>
                          {!within.name && (
                            <div style={{ fontSize: 12, color: 'red' }}>
                              Within factor name can't empty
                            </div>
                          )}
                        </div>
                        {renderData(within.data, { marginLeft: 48 }, (row) => {
                          onDeleteDataWithin(factor, within, row)
                        })}
                        <BoxDrag
                          style={{ borderBottom: getBorderDrag() }}
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
                        style={{ borderBottom: getBorderDrag() }}
                        onDrop={() => onDropData(factor)}
                        onDragOver={onDragOver}
                        onDragLeave={onDragLeave}
                        onMouseOver={() => onMouseOver(factor)}
                      />
                    </>
                  )}
                </BoxFactor>
                {projectType === ProjectTypeValue.WITHIN_FACTOR &&
                dataFactors.length ? (
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
            <Box sx={{display: 'flex', gap: 5}}>
              { Object.keys(queryFilter).some((key) => queryFilter[key]) &&
                <Button variant="contained" onClick={handleClear}>
                Clear Filter
              </Button>}
              <ButtonFilter
                onClick={() => setOpenFilter(true)}
                style={{ margin: '0 26px 0 0' }}
              >
                Filter
              </ButtonFilter>
            </Box>
          </BoxFilter>
          <DatabaseTableComponent
            addProject={true}
            onSort={handleSort}
            orderKey={columnSort}
            orderBy={orderBy}
            rowClick={rowClick}
            defaultExpand
            onBeginDrag={onBeginDrag}
            onDrag={onDragRow}
            onDragEnd={onDragEnd}
            draggable
            data={databasese.records}
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
        <ButtonFilter
          onClick={onOk}
          sx={{ backgroundColor: 'limegreen !important' }}
        >
          {idEdit ? 'Ok' : 'Add'}
        </ButtonFilter>
        <ButtonFilter onClick={onCancle}>Cancel</ButtonFilter>
      </Box>
      {loading && <Loading />}
    </ProjectsWrapper>
  )
}

const TextName = styled(Typography)(({ theme }) => ({
  textOverflow: 'ellipsis',
  width: 'calc(40% - 16px)',
  overflow: 'hidden',
  whiteSpace: 'nowrap',
  padding: theme.spacing(1),
  borderWidth: 1,
  fontSize: 16,
}))

const BoxItem = styled(Box)({
  display: 'flex',
  height: 40,
  alignItems: 'center',
  borderBottom: '1px solid rgba(0,0,0,0.8)',
  paddingLeft: 16,
  marginBottom: 4,
  justifyContent: 'space-between',
})

const TypographyBoxItem = styled(Box)({
  minWidth: 120,
  whiteSpace: 'nowrap',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
})

const BoxDrag = styled(Box)({
  paddingBottom: 24,
  width: '100%',
  borderWidth: 1,
})

const BoxFactor = styled(Box)({})

const ProjectsWrapper = styled(Box)(({ theme }) => ({
  width: `calc(100% - ${theme.spacing(2)})`,
  padding: theme.spacing(2),
  marginBottom: theme.spacing(3),
  userSelect: 'none',
}))

const BoxOptions = styled(RadioGroup)(({ theme }) => ({
  width: '100%',
  padding: theme.spacing(1, 2),
  display: 'flex',
  flexDirection: 'inherit',
}))

const InputName = styled('input')(({ theme }) => ({
  padding: theme.spacing(1),
  outline: 'none',
  borderColor: 'transparent',
  fontSize: 18,
  width: 'calc(40% - 16px)',
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
  height: 'calc(100% - 177px)',
  overflow: 'hidden',
}))

const DragBox = styled(Box)(({ theme }) => ({
  width: '40%',
  padding: theme.spacing(1, 2),
  border: '1px solid #000',
  minHeight: 100,
  height: 'calc(100% - 18px)',
  overflow: 'auto',
}))

const DropBox = styled(Box)(({ theme }) => ({
  width: '60%',
  padding: theme.spacing(1, 2),
  border: '1px solid #dedede',
  height: 'calc(100% - 18px)',
  overflow: 'auto',
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
