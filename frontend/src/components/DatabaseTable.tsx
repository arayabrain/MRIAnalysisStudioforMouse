import { Box, styled, Typography } from '@mui/material'
import {
  MouseEvent as MouseEventReact,
  FC,
  Fragment,
  useState,
  useRef,
  useEffect,
  CSSProperties,
} from 'react'
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown'
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward'
import {
  DatatypesDatabase,
  ImagesDatabase,
  RecordDatabase,
  RecordList,
  SessionsDatabase,
} from 'pages/Database'
import React from 'react'

type Object = {
  [key: string]: Object | string
}

export type Column = {
  width?: number
  styleTitle?: CSSProperties
  title: string
  dataIndex?: string
  name?: string
  child?: string
  filter?: boolean
  render?: (
    item?: RecordDatabase | RecordList | ImagesDatabase,
    value?: string | object | number,
    index?: number,
  ) => JSX.Element | null | undefined | string | number
}

type TableComponentProps = {
  addProject: boolean
  data?: (RecordDatabase | RecordList)[]
  className?: string
  columns?: Column[]
  orderBy?: 'ASC' | 'DESC' | ''
  orderKey?: string
  onSort?: (orderKey: string, orderBy: 'ASC' | 'DESC' | '') => void
  rowClick?: (row: ImagesDatabase) => void
  onClickEvent?: (
    e: MouseEventReact<HTMLTableRowElement>,
    row: ImagesDatabase,
  ) => void
  draggable?: boolean
  onDrag?: (row?: ImagesDatabase[]) => void
  onBeginDrag?: () => void
  onDragEnd?: (row?: ImagesDatabase) => void
  defaultExpand?: boolean
}

type RenderColumnProps = {
  data: RecordDatabase | SessionsDatabase | ImagesDatabase | RecordList
  columns: Column[]
  orderBy?: 'ASC' | 'DESC'
  orderKey?: string
  onSort?: (orderKey: string, orderBy: string) => void
  rowClick?: (
    e: MouseEventReact<HTMLTableRowElement>,
    row: ImagesDatabase,
  ) => void
  draggable?: boolean
  onDrag?: (
    event: MouseEventReact<HTMLTableRowElement>,
    row?: ImagesDatabase[],
  ) => void
  onDragEnd?: (row?: ImagesDatabase) => void
  recordIndex: number
  defaultExpand?: boolean
  dataShow?: boolean
  beginDrag?: boolean
  draggableProps?: boolean
  allowMutilKey?: boolean
  drags: ImagesDatabase[]
  onMouseDown: (
    event: MouseEventReact<HTMLTableRowElement>,
    image: ImagesDatabase,
  ) => void
}

const renderCol = (
  col: Column,
  item: ImagesDatabase | RecordDatabase | RecordList,
  index: number,
) => {
  const key = col.name || col.dataIndex || ''
  let value: ImagesDatabase | RecordDatabase | RecordList | string = item
  if (key.includes('.')) {
    const keys = key.split('.')
    keys.forEach((k) => {
      if (k === 'voxel_size' || k === 'size') {
        value = JSON.stringify((value as unknown as Object)?.[k])
      } else {
        value = (value as unknown as Object)?.[k] as
          | ImagesDatabase
          | RecordDatabase
          | RecordList
          | string
      }
    })
  } else value = (item as unknown as Object)[key] as string
  if (col.render) return col.render(item, value, index)
  return typeof value === 'object' || Array.isArray(value) ? null : value
}

const RenderChild: FC<{
  columns: Column[]
  type: DatatypesDatabase
  propsColumn: RenderColumnProps
  data: SessionsDatabase
  recordIndex: number
  indexChild: number
}> = ({ columns, type, propsColumn, data, indexChild, recordIndex }) => {
  const [openChild, setOpenChild] = useState(true)
  return (
    <Fragment>
      <Tr
        style={{
          transition: 'all 0.3s',
          backgroundColor: 'rgb(238, 238, 238)',
        }}
      >
        {columns.map((column) => {
          const key = column.name || column.dataIndex || ''
          return (
            <Td
              key={`col_${column.name || column.dataIndex}`}
              onClick={() => key === 'datatype' && setOpenChild(!openChild)}
            >
              {key === 'datatype' ? (
                <BoxCenter>
                  {type.label}
                  {type.images?.length ? (
                    <ArrowDropDownIcon
                      style={{
                        transform: `rotate(${!openChild ? -180 : 0}deg)`,
                      }}
                    />
                  ) : null}
                </BoxCenter>
              ) : (
                ''
              )}
            </Td>
          )
        })}
      </Tr>
      {openChild &&
        type.images.map((image, index) => (
          <RenderColumn
            {...propsColumn}
            key={`child_row_image_${image.id}_${index}`}
            data={
              {
                ...image,
                session_index: data.session_index,
                subject_index: data.subject_index,
                session_id: data.id,
                datatype_index: indexChild,
                image_index: index,
                datatype_label: type.label,
                subject_id: data.parent_id,
                record_index: recordIndex,
              } as unknown as ImagesDatabase
            }
          />
        ))}
    </Fragment>
  )
}

const RenderColumn = (props: RenderColumnProps) => {
  const { columns, data, recordIndex, rowClick, drags, onMouseDown } = props
  const { draggable, onDrag } = props
  const [openChildParent, setOpenChildPrent] = useState(true)
  const [openSubjects, setOpenSubjects] = useState<string[]>(
    (data as RecordDatabase)?.subjects?.map?.((e) => e.id) || [],
  )

  const isDrag = drags.find((drag) => {
    return (
      drag.id === data.id &&
      drag.session_id === (data as ImagesDatabase).session_id &&
      drag.datatype_index === (data as ImagesDatabase).datatype_index
    )
  })

  const onDragEvent = (
    event: MouseEventReact<HTMLTableRowElement>,
    image: ImagesDatabase,
  ) => {
    return onDrag?.(event, [image])
  }

  const onSetOpenSubject = (subId: string) => {
    if (openSubjects.includes(subId)) {
      setOpenSubjects(openSubjects.filter((o) => o !== subId))
    } else setOpenSubjects([...openSubjects, subId])
  }

  if (
    (data as RecordDatabase)?.subjects?.length ||
    (data as SessionsDatabase).datatypes?.length
  ) {
    return (
      <Fragment>
        <Tr
          style={{
            transition: 'all 0.3s',
            backgroundColor: 'rgb(238, 238, 238)',
          }}
        >
          {columns.map((column) => {
            const key = column.name || column.dataIndex || ''
            return (
              <Td
                key={`col_${column.name || column.dataIndex}`}
                onClick={() =>
                  key === 'session' && setOpenChildPrent(!openChildParent)
                }
              >
                {key === 'action' ? null : (
                  <BoxCenter>
                    {renderCol(
                      column,
                      data as RecordDatabase | RecordList,
                      recordIndex,
                    )}
                    {renderCol(
                      column,
                      data as RecordDatabase | RecordList,
                      recordIndex,
                    ) &&
                      key === 'session' && (
                        <ArrowDropDownIcon
                          style={{
                            transform: `rotate(${
                              !openChildParent ? -180 : 0
                            }deg)`,
                          }}
                        />
                      )}
                  </BoxCenter>
                )}
              </Td>
            )
          })}
        </Tr>
        {openChildParent &&
          (data as RecordDatabase).subjects?.map((sub, subject_index) => {
            return (
              <Fragment key={sub.id}>
                <Tr
                  style={{
                    transition: 'all 0.3s',
                    backgroundColor: 'rgb(238, 238, 238)',
                  }}
                >
                  {columns.map((column) => {
                    const key = column.name || column.dataIndex || ''
                    return (
                      <Td
                        key={`col_${column.name || column.dataIndex}`}
                        onClick={() =>
                          key === 'subject' && onSetOpenSubject(sub.id)
                        }
                      >
                        {key === 'subject' ? (
                          <BoxCenter>
                            {sub.label}
                            {sub.sessions?.length ? (
                              <ArrowDropDownIcon
                                style={{
                                  transform: `rotate(${
                                    !openSubjects.includes(sub.id) ? -180 : 0
                                  }deg)`,
                                }}
                              />
                            ) : null}
                          </BoxCenter>
                        ) : (
                          ''
                        )}
                      </Td>
                    )
                  })}
                </Tr>
                {openSubjects.includes(sub.id) &&
                  sub.sessions.map((session, session_index) => (
                    <RenderColumn
                      {...props}
                      key={`session_${session.id}`}
                      data={
                        {
                          ...session,
                          session: session.label,
                          session_index,
                          subject_index,
                        } as SessionsDatabase
                      }
                    />
                  ))}
              </Fragment>
            )
          })}
        {openChildParent &&
          (data as SessionsDatabase).datatypes?.map((type, ii) => {
            return (
              <RenderChild
                key={`data_types_${type.id}`}
                type={type}
                data={data as SessionsDatabase}
                propsColumn={props}
                columns={columns}
                indexChild={ii}
                recordIndex={recordIndex}
              />
            )
          })}
      </Fragment>
    )
  }

  return (
    <Tr
      onClick={(e) => rowClick?.(e, data as ImagesDatabase)}
      draggable={draggable}
      onDragStart={(e) => onDragEvent?.(e, data as ImagesDatabase)}
      onMouseDown={(e) => onMouseDown(e, data as ImagesDatabase)}
      style={{
        transition: 'all 0.3s',
        backgroundColor: isDrag ? 'rgba(25,118,210,0.15)' : '',
      }}
    >
      {columns.map((column) => {
        return (
          <Td key={`col_${column.name || column.dataIndex}`}>
            {renderCol(column, data as ImagesDatabase, recordIndex)}
          </Td>
        )
      })}
    </Tr>
  )
}

const DatabaseTableComponent: FC<TableComponentProps> = (props) => {
  const {
    addProject,
    className,
    orderKey,
    orderBy,
    onSort,
    draggable,
    rowClick,
    onDrag,
    onDragEnd,
    onBeginDrag: onBeginDragProps,
    ...p
  } = props
  const { data = [], columns = [] } = props
  const [drags, setDrags] = useState<ImagesDatabase[]>([])
  const [mouseMoveRect, setMouseMoveRect] = useState({ pageX: 0, pageY: 0 })
  const timeoutClick = useRef<NodeJS.Timeout | undefined>()

  const ctrRef = useRef(false)
  const refTable = useRef<HTMLDivElement | null>(null)
  const refTdSelect = useRef<{
    [key: string]: {
      dom: HTMLTableRowElement
      tds: { id: number | string; dom: HTMLTableCellElement; html: string }[]
    }
  }>({})
  const mouseStart = useRef<{ pageX: number; pageY: number } | undefined>()
  const [beginDrag, setBeginDrag] = useState(false)

  useEffect(() => {
    window.addEventListener('keydown', onKeydownEvent)
    window.addEventListener('keyup', onKeyupEvent)
    window.addEventListener('mouseup', onMouseUp)
    window.addEventListener('mousemove', onMouseMove)
    window.addEventListener('click', onClick)
    return () => {
      window.removeEventListener('keydown', onKeyupEvent)
      window.removeEventListener('keyup', onKeyupEvent)
      window.removeEventListener('mouseup', onMouseUp)
      window.removeEventListener('mousemove', onMouseMove)
      window.removeEventListener('click', onClick)
    }
    //eslint-disable-next-line
  }, [])

  const onKeydownEvent = (event: KeyboardEvent) => {
    ctrRef.current = event.ctrlKey || event.metaKey
  }

  const onKeyupEvent = () => {
    ctrRef.current = false
  }

  const onClick = (event: MouseEvent) => {
    if (refTable.current?.contains?.(event.target as Element)) return
    ctrRef.current = false
    setDrags([])
    onDragEnd?.()
  }

  const onSortHandle = (nameCol: string) => {
    if (orderKey === nameCol) {
      let order: 'ASC' | 'DESC' | '' = ''
      if (orderBy === 'ASC') {
        order = 'DESC'
      } else if (!orderBy) {
        order = 'ASC'
      }
      onSort?.(nameCol, order)
    } else onSort?.(nameCol, 'ASC')
  }

  const onRowClickEvent = (
    event: MouseEventReact<HTMLTableRowElement>,
    image: ImagesDatabase,
  ) => {
    const idDom = `${image.id}_${image.datatype_index}_${image.session_id}`
    if (!ctrRef.current) {
      if (!timeoutClick.current) {
        timeoutClick.current = setTimeout(() => {
          timeoutClick.current = undefined
        }, 300)
        if (draggable) {
          setDrags([image])
          const tds = event.currentTarget.getElementsByTagName('td')
          refTdSelect.current[idDom] = {
            dom: event.currentTarget as unknown as HTMLTableRowElement,
            tds: [],
          }
          for (let i = 0; i < tds.length; i++) {
            refTdSelect.current[idDom].tds.push({
              id: tds[i].id,
              dom: tds[i],
              html: tds[i].innerHTML,
            })
          }
        }
        return
      }
      return rowClick?.(image)
    }
    if (!draggable) return
    if (
      drags.find(
        (drag) =>
          drag.id === image.id &&
          drag.datatype_index === image.datatype_index &&
          drag.session_index === image.session_index,
      )
    ) {
      setDrags(
        drags.filter(
          (drag: ImagesDatabase) =>
            drag.id === image.id &&
            drag.datatype_index === image.datatype_index &&
            drag.session_index === image.session_index,
        ),
      )
      delete refTdSelect.current[idDom]
    } else {
      setDrags([...drags, image])
      const tds = event.currentTarget.getElementsByTagName('td')
      refTdSelect.current[idDom] = {
        dom: event.currentTarget as unknown as HTMLTableRowElement,
        tds: [],
      }
      for (let i = 0; i < tds.length; i++) {
        refTdSelect.current[idDom].tds.push({
          id: tds[i].id,
          dom: tds[i],
          html: tds[i].innerHTML,
        })
      }
    }
  }

  const onMouseDown = (
    event: MouseEventReact<HTMLTableRowElement>,
    image: ImagesDatabase,
  ) => {
    if (
      !drags.length ||
      !draggable ||
      !drags.some(
        (drag) =>
          drag.id === image.id &&
          drag.datatype_index === image.datatype_index &&
          drag.session_index === image.session_index,
      )
    ) {
      return
    }
    mouseStart.current = {
      pageX: event.pageX,
      pageY: event.pageY,
    }
    onBeginDragProps?.()
    setMouseMoveRect({ pageX: 0, pageY: 0 })
    onDrag?.(drags)
  }

  const onMouseUp = () => {
    mouseStart.current = undefined
    setBeginDrag(false)
    setTimeout(() => {
      onDrag?.(undefined)
    }, 100)
  }

  const onMouseMove = (event: MouseEvent) => {
    if (!mouseStart.current || !draggable || !mouseStart.current) return
    setBeginDrag(true)
    setMouseMoveRect({
      pageX: event.pageX - mouseStart.current.pageX,
      pageY: event.pageY - mouseStart.current.pageY,
    })
  }

  const onBeginDrag = (
    e: MouseEventReact<HTMLTableRowElement>,
    image?: ImagesDatabase[],
  ) => {
    e.preventDefault()
    onDrag?.(image)
  }

  return (
    <>
      <TableWrap ref={refTable} className={className} addProject={addProject}>
        <DataTable
          style={{
            width: columns.reduce((a, b) => a + (Number(b.width) || 110), 0),
          }}
        >
          <Thead>
            <Tr>
              {columns.map((col, iCol) => {
                const nameCol = col.name || col.dataIndex || ''
                return (
                  <Th
                    onClick={() => {
                      if (col.filter) onSortHandle(nameCol)
                    }}
                    style={{
                      maxWidth: col.width,
                      minWidth: col.width,
                      width: col.width,
                      cursor: 'pointer',
                      ...(col.styleTitle || {}),
                    }}
                    key={col.dataIndex || col.name || iCol}
                  >
                    {col.title}
                    <ArrowDownwardIconOrder
                      style={{
                        transform: `rotate(${orderBy === 'ASC' ? 180 : 0}deg)`,
                        opacity:
                          orderBy && nameCol === orderKey && col.filter ? 1 : 0,
                      }}
                    />
                  </Th>
                )
              })}
            </Tr>
          </Thead>
          <TBody>
            {data.map((item, index) => (
              <RenderColumn
                allowMutilKey={ctrRef.current}
                recordIndex={index}
                columns={columns}
                {...p}
                data={item}
                rowClick={(e, image) => onRowClickEvent(e, image)}
                onMouseDown={onMouseDown}
                beginDrag={beginDrag}
                draggable={false}
                draggableProps={draggable}
                key={`row_table_${item.id}_${index}`}
                drags={drags}
                onDrag={onBeginDrag}
                onDragEnd={onDragEnd}
              />
            ))}
          </TBody>
        </DataTable>
        {!data.length ? <NoData>No Data</NoData> : null}
      </TableWrap>
      {beginDrag &&
        drags.map((el) => {
          const rowId = `${el.id}_${el.datatype_index}_${el.session_id}`
          const trNow = refTdSelect.current[rowId]
          const { width, height, top, left } =
            trNow.dom?.getBoundingClientRect()
          const style = {
            width,
            height,
            top: top + mouseMoveRect.pageY,
            left: left + mouseMoveRect.pageX,
          }
          return (
            <BoxDrag key={el.id} style={style}>
              {trNow.tds.map((td, index) => {
                const { width } = td.dom.getBoundingClientRect()
                return (
                  <Box
                    key={`${rowId}_-${index}`}
                    style={{ width, padding: 16 }}
                    dangerouslySetInnerHTML={{ __html: td.html }}
                  />
                )
              })}
            </BoxDrag>
          )
        })}
    </>
  )
}

const BoxDrag = styled(Box)({
  position: 'absolute',
  background: '#ffffff',
  backgroundColor: 'rgba(25,118,210,0.15)',
  display: 'flex',
  alignItems: 'center',
})

const TableWrap = styled(Box, {
  shouldForwardProp: (props) => props !== 'addProject',
})<{ addProject: boolean }>(({ addProject }) => ({
  overflowX: 'scroll',
  height: `calc(100vh - ${addProject ? 365 : 205}px)`,
}))

const DataTable = styled('table')({
  boxSizing: 'border-box',
  minWidth: '100%',
  borderCollapse: 'collapse',
  border: '1px solid rgba(224, 224, 224, 1)',
})

const Thead = styled('thead')({})

const Tr = styled('tr')({})

const Th = styled('th')(({ theme }) => ({
  padding: theme.spacing(2),
  textAlign: 'left',
  backgroundColor: 'none',
  color: 'rgba(0,0,0,.88)',
  fontWeight: 600,
  border: '1px solid rgba(224, 224, 224, 1)',
  userSelect: 'none',
  ':first-of-type': {
    borderTopLeftRadius: 4,
  },
  ':last-of-type': {
    borderTopRightRadius: 4,
  },
}))

const TBody = styled('tbody')(() => ({}))

const Td = styled('td')(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: '1px solid rgba(224, 224, 224, 1)',
}))

const NoData = styled(Typography)({
  textAlign: 'center',
  fontWeight: '600',
  fontSize: 20,
  paddingTop: 16,
})

const ArrowDownwardIconOrder = styled(ArrowDownwardIcon)({
  width: 16,
  height: 16,
  transition: 'transform 0.3s',
  marginBottom: -3,
  marginLeft: 5,
})

const BoxCenter = styled(Box)({
  display: 'flex',
  alignItems: 'center',
})

export default React.memo(DatabaseTableComponent)
