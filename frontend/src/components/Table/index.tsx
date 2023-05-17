import { Box, styled, Typography } from '@mui/material'
import { FC, useCallback } from 'react'
import ReactPaginate from 'react-paginate'
import KeyboardArrowLeftIcon from '@mui/icons-material/KeyboardArrowLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward'
import { ProjectType } from 'store/slice/Project/ProjectType'

export type Column = {
  width?: number | string
  title: string
  dataIndex?: string
  name?: string
  align?: string
  filter?: boolean
  render?: (
    item: ProjectType,
    value?: string | object | number,
    index?: number,
  ) => JSX.Element | null | undefined
}

type TableComponentProps = {
  data?: ProjectType[]
  orderBy?: 'ASC' | 'DESC'
  orderKey?: string
  className?: string
  columns?: Column[]
  paginate?: {
    page: number
    total: number
    page_size: number
    breakLabel?: string
    nextLabel?: string
    previousLabel?: string
    pageRangeDisplayed?: number
    renderOnZeroPageCount?: string
    onPageChange?: (selectedItem: { selected: number }) => any
  }
}

const TableComponent: FC<TableComponentProps> = (props) => {
  const {
    data = [],
    columns = [],
    paginate,
    className,
    orderBy,
    orderKey,
  } = props
  const pageCount = (paginate?.total || 0) / (paginate?.page_size || 1)

  const renderCol = useCallback(
    (col: Column, item: ProjectType, index: number) => {
      const value = item[(col.name || col.dataIndex || '') as keyof ProjectType]
      if (col.render) return col.render(item, value, index)
      return value || null
    },
    [],
  )

  return (
    <Box className={className}>
      <Table>
        <Thead>
          <Tr>
            {columns.map((col, iCol) => {
              const nameCol = col.name || col.dataIndex || ''
              return (
                <Th
                  style={{ width: col.width, textAlign: col.align as any }}
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
            <Tr key={item.id || index}>
              {columns.map((col, iCol) => (
                <Td
                  style={{ textAlign: col.align as any }}
                  key={col.dataIndex || col.name || iCol}
                >
                  {renderCol(col, item, index)}
                </Td>
              ))}
            </Tr>
          ))}
        </TBody>
      </Table>
      {!data.length ? <NoData>No Data</NoData> : null}
      {pageCount ? (
        <MyPaginate
          disableInitialCallback
          marginPagesDisplayed={3}
          pageRangeDisplayed={3}
          breakLabel={'...'}
          pageCount={pageCount}
          previousLabel={<KeyboardArrowLeftIcon />}
          nextLabel={<ChevronRightIcon />}
          {...paginate}
        />
      ) : null}
    </Box>
  )
}

const MyPaginate = styled(ReactPaginate)<any>`
  margin-bottom: 2rem;
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  list-style-type: none;
  padding: 1rem 0;
  li a {
    padding: 0.6rem 1rem;
    cursor: pointer;
  }
  li.previous,
  li.next {
    margin-top: -2px;
  }
  li.previous.disabled,
  li.next.disabled {
    opacity: 0.4;
  }
  li.previous a,
  li.next a,
  li.break a {
    border-color: transparent;
  }
  li.active a {
    background-color: #0366d6;
    border-color: transparent;
    color: white;
    min-width: 32px;
  }
  li.disabled a {
    color: grey;
  }
  li.disable,
  li.disabled a {
    cursor: default;
  }
  li.selected {
    color: #1677ff;
    font-weight: 600;
  }
`

const Table = styled('table')({
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
  maxWidth: 155,
  wordBreak: 'break-word',
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

export default TableComponent
