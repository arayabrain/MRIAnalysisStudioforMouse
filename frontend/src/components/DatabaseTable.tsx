import { Box, styled, Typography } from '@mui/material'
import { MouseEvent, FC, Fragment, useState, useRef, useEffect } from 'react'
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown'
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward'

type Column = {
  width?: number
  title: string
  dataIndex?: string
  name?: string
  child?: string
  filter?: boolean
  render?: (
    item?: any,
    value?: any,
    index?: number,
  ) => JSX.Element | null | undefined | string | number
}

type TableComponentProps = {
  data?: any[]
  className?: string
  columns?: Column[]
  orderBy?: 'ASC' | 'DESC'
  orderKey?: string
  onSort?: (orderKey: string, orderBy: string) => any
  rowClick?: (row: any) => any
  onClickEvent?: (e: any, row: any) => any
  draggable?: boolean
  onDrag?: (row?: any) => any
  onDragEnd?: (row?: any) => any
  defaultExpand?: boolean
  previewImage?: boolean
}

type RenderColumnProps = {
  item: any
  columns: Column[]
  orderBy?: 'ASC' | 'DESC'
  orderKey?: string
  onSort?: (orderKey: string, orderBy: string) => any
  rowClick?: (e: any, row: any) => any
  draggable?: boolean
  onDrag?: (event: any, row?: any) => any
  onDragEnd?: (row?: any) => any
  index: number
  isData?: boolean
  defaultExpand?: boolean
  dataShow?: boolean
  beginDrag?: boolean
  draggableProps?: boolean
  previewImage?: boolean
  allowMutilKey?: boolean
  drags: any[]
  onMouseDown: (event: MouseEvent<HTMLTableRowElement>, image: any) => any
}

const renderCol = (col: Column, item: any, index: number, child?: boolean) => {
  const key = col.name || col.dataIndex || ''
  const value = item[child ? col.child || key : key]
  if (col.render) return col.render(item, value, index)
  return typeof value === 'object' || Array.isArray(value) ? null : value
}

const ChildCol = (props: RenderColumnProps) => {
  const { columns, item, index, rowClick, defaultExpand, isData } = props
  const [show, setShow] = useState<boolean>(!!defaultExpand)

  const onClickCol = (event: MouseEvent<HTMLTableDataCellElement>) => {
    event.preventDefault()
    event.stopPropagation()
    setShow(!show)
  }

  return (
    <Fragment>
      <Tr
        onClick={(e) => rowClick?.(e, item)}
        style={{ backgroundColor: 'rgb(238, 238, 238)' }}
      >
        {columns.map((column) => {
          const key = column.name || column.dataIndex || ''
          const value =
            isData && key === 'datatypes'
              ? item.title
              : renderCol(column, item, index)
          return (
            <Td
              key={`row_child_${column.name || column.dataIndex}`}
              onClick={onClickCol}
              style={{ cursor: 'pointer' }}
            >
              <ElementFlex>
                {['datatypes', 'sessions'].includes(key) && value ? (
                  <ArrowDropDownIconWrap
                    style={{ transform: `rotate(${show ? 180 : 0}deg)` }}
                  />
                ) : null}
                {['datatypes', 'sessions', 'subject'].includes(key)
                  ? value
                  : null}
              </ElementFlex>
            </Td>
          )
        })}
      </Tr>
      {show && (
        <RenderColumn
          {...props}
          draggable={props.draggableProps}
          item={item}
          dataShow
          isData={isData}
        />
      )}
    </Fragment>
  )
}

const RenderColumn = (props: RenderColumnProps) => {
  const {
    columns,
    item,
    index,
    rowClick,
    dataShow,
    previewImage,
    isData,
    drags,
    onMouseDown,
    beginDrag,
  } = props
  const { draggable, onDrag, onDragEnd } = props

  const onDragEvent = (event: any, image: any) => {
    return onDrag?.(event, [image])
  }

  if (Array.isArray(item.sessions) && item.sessions?.length && !isData) {
    const itemData = item.sessions
    return itemData.map((i: any, index: number) => (
      <ChildCol key={`col_${i.id}_${index}`} {...props} item={i} />
    ))
  }

  if (
    Array.isArray(item.datatypes?.images) &&
    item.datatypes?.images?.length &&
    !isData
  ) {
    const itemData = item.datatypes
    return <ChildCol {...props} item={itemData} isData />
  }

  if (isData) {
    return item.images.map((image: any, index: number) => {
      const isDragging = drags.find((drag: any) => drag.id === image.id)
      return (
        <Tr
          onMouseDown={(e) => onMouseDown?.(e, image)}
          id={image.id}
          key={`data_show_image_${image.id}_${index}`}
          onClick={(e) => rowClick?.(e, image)}
          // draggable={draggable}
          // onDragStart={(e) => onDragEvent?.(e, image)}
          // onDragEnd={onDragEnd}
          style={{
            border: `${
              isDragging && draggable && !beginDrag ? 2 : 0
            }px dashed #1976d2`,
            transition: 'all 0.3s',
            opacity: isDragging && draggable && beginDrag ? 0.3 : 1,
            backgroundColor:
              dataShow || previewImage ? 'transparent' : 'rgb(238, 238, 238)',
          }}
        >
          {columns.map((column) => {
            const key = column.name || column.dataIndex || ''
            return (
              <Td key={`col_${column.name || column.dataIndex}`}>
                {dataShow && ['datatypes', 'sessions'].includes(key)
                  ? null
                  : renderCol(column, image, index)}
              </Td>
            )
          })}
        </Tr>
      )
    })
  }

  return (
    <Tr
      onClick={(e) => rowClick?.(e, item)}
      draggable={draggable}
      onDragStart={(e) => onDragEvent?.(e, item)}
      onDragEnd={onDragEnd}
      style={{
        transition: 'all 0.3s',
        backgroundColor:
          dataShow || previewImage ? 'transparent' : 'rgb(238, 238, 238)',
      }}
    >
      {columns.map((column) => {
        const key = column.name || column.dataIndex || ''
        return (
          <Td key={`col_${column.name || column.dataIndex}`}>
            {dataShow && ['datatypes', 'sessions'].includes(key)
              ? null
              : renderCol(column, item, index)}
          </Td>
        )
      })}
    </Tr>
  )
}

const DatabaseTableComponent: FC<TableComponentProps> = (props) => {
  const {
    className,
    orderKey,
    orderBy,
    onSort,
    draggable,
    rowClick,
    onDrag,
    onDragEnd,
    ...p
  } = props
  const { data = [], columns = [] } = props
  const [drags, setDrags] = useState<any[]>([])
  const [mouseMoveRect, setMouseMoveRect] = useState({ pageX: 0, pageY: 0 })
  const timeoutClick = useRef<NodeJS.Timeout | undefined>()

  const ctrRef = useRef(false)
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
    return () => {
      window.removeEventListener('keydown', onKeyupEvent)
      window.removeEventListener('keyup', onKeyupEvent)
      window.removeEventListener('mouseup', onMouseUp)
      window.removeEventListener('mousemove', onMouseMove)
    }
    //eslint-disable-next-line
  }, [])

  const onKeydownEvent = (event: KeyboardEvent) => {
    ctrRef.current = event.ctrlKey || event.metaKey
  }

  const onKeyupEvent = (event: KeyboardEvent) => {
    if (event.ctrlKey || event.metaKey) return
    ctrRef.current = false
    setDrags([])
    onDragEnd?.()
  }

  const onSortHandle = (nameCol: string) => {
    onSort?.(nameCol, orderBy === 'ASC' ? 'DESC' : 'ASC')
  }

  const onRowClickEvent = (
    event: MouseEvent<HTMLTableColElement>,
    image: any,
  ) => {
    if (!ctrRef.current || !draggable) {
      if (!timeoutClick.current) {
        timeoutClick.current = setTimeout(() => {
          timeoutClick.current = undefined
        }, 300)
        if (!ctrRef.current) {
          setDrags([image])
          const tds = event.currentTarget.getElementsByTagName('td')
          refTdSelect.current[event.currentTarget.id] = {
            dom: event.currentTarget as unknown as HTMLTableRowElement,
            tds: [],
          }
          for (let i = 0; i < tds.length; i++) {
            refTdSelect.current[event.currentTarget.id].tds.push({
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
    if (drags.find((drag: any) => drag.id === image.id)) {
      setDrags(drags.filter((drag: any) => drag.id !== image.id))
      delete refTdSelect.current[event.currentTarget.id]
    } else {
      setDrags([...drags, image])
      const tds = event.currentTarget.getElementsByTagName('td')
      refTdSelect.current[event.currentTarget.id] = {
        dom: event.currentTarget as unknown as HTMLTableRowElement,
        tds: [],
      }
      for (let i = 0; i < tds.length; i++) {
        refTdSelect.current[event.currentTarget.id].tds.push({
          id: tds[i].id,
          dom: tds[i],
          html: tds[i].innerHTML,
        })
      }
    }
  }

  const onMouseDown = (event: MouseEvent<HTMLTableRowElement>, image: any) => {
    if (
      !drags.length ||
      !draggable ||
      !drags.some((drag) => drag.id === image.id)
    )
      return
    mouseStart.current = { pageX: event.pageX, pageY: event.pageY }
    onDrag?.(drags)
  }

  const onMouseUp = () => {
    mouseStart.current = undefined
    setBeginDrag(false)
  }

  const onMouseMove = (event: any) => {
    if (!mouseStart.current || !draggable || !mouseStart.current) return
    setBeginDrag(true)
    setMouseMoveRect({
      pageX: event.pageX - mouseStart.current.pageX,
      pageY: event.pageY - mouseStart.current.pageY,
    })
  }

  const onBeginDrag = (e: any, image: any) => {
    e.preventDefault()
    onDrag?.(image)
  }

  return (
    <>
      <TableWrap className={className}>
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
                    onClick={() => onSortHandle(nameCol)}
                    style={{
                      maxWidth: col.width,
                      width: col.width,
                      cursor: 'pointer',
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
                item={item}
                index={index}
                columns={columns}
                {...p}
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
          const trNow = refTdSelect.current[el.id]
          const { width, height, top, left } =
            trNow.dom?.getBoundingClientRect()
          const style = {
            width,
            height,
            top: top - window.scrollY + mouseMoveRect.pageY,
            left: left + mouseMoveRect.pageX,
          }
          return (
            <BoxDrag key={el.id} style={style}>
              {trNow.tds.map((td, index) => {
                const { width } = td.dom.getBoundingClientRect()
                return (
                  <Box key={`${td.id}_${index}`} style={{ width, padding: 16 }}>
                    {td.html}
                  </Box>
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
  border: '1px dashed #1976d2',
  display: 'flex',
  alignItems: 'center',
})

const ArrowDropDownIconWrap = styled(ArrowDropDownIcon)({
  transition: 'transform 0.3s',
})

const ElementFlex = styled(Box)({
  display: 'flex',
  alignItems: 'center',
})

const TableWrap = styled(Box)({
  overflowX: 'scroll',
})

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

export default DatabaseTableComponent
