import React, {useEffect, useState} from 'react'
import Box from '@mui/material/Box'
import Collapse from '@mui/material/Collapse'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import OpenInNewIcon from '@mui/icons-material/OpenInNew';

import { ExperimentStatusIcon } from './ExperimentStatusIcon'
import {Button, ClickAwayListener, styled, Tooltip, tooltipClasses, TooltipProps} from "@mui/material";
import { FunctionType } from "./Experiment";
import { BASE_URL } from "../../const/API";
import ImageView from "../ImageView";
import { Viewer } from "../../pages/Database";


export const CollapsibleTable = React.memo<{
  open: boolean
  data?: object
}>(({ open , data}) => {
  return (
    <TableRow>
      <TableCell sx={{ paddingBottom: 0, paddingTop: 0 }} colSpan={10}>
        <Collapse in={open} timeout="auto" unmountOnExit>
          <Box margin={1}>
            <Table size="small" aria-label="purchases">
            <Head />
            {data && Object.keys(data).map((item, index) => {
              return (
                <Body key={index} data={(data as any)?.[item]}/>
              )
            })}
            </Table>
          </Box>
        </Collapse>
      </TableCell>
    </TableRow>
  )
})

const Head = React.memo(() => {
  return (
    <TableHead>
      <TableRow>
        <TableCell>Function</TableCell>
        <TableCell>nodeID</TableCell>
        <TableCell>Success</TableCell>
        <TableCell>Output</TableCell>
      </TableRow>
    </TableHead>
  )
})

const Body = React.memo<{
    data: object
}>(({data}) => {
  return (
    <TableBody>
      <TableRowOfFunction data={data} />
    </TableBody>
  )
})

const TableRowOfFunction = ({ data } : {data: object}) => {
  const {name, success, unique_id, outputs, message} = data as FunctionType
  const [disabled, setDisabled] = useState({ left: true, right: false })
  const [viewer, setViewer] = useState<Viewer>({ open: false, url: '' })
  const [index, setIndex] = useState(0)

  const onCloseImageView = () => {
    setViewer({ open: false, url: '' })
  }

  useEffect(() => {
    if(viewer.open) {
      onOpen()
    }
    //eslint-disable-next-line
  }, [index])

  const onNext = () => {
    if (!viewer.open) return
    setDisabled({ left: false, right: index === outputs.length - 2 })
    setIndex(index + 1)
  }

  const onPrevious = () => {
    if (!viewer.open) return
    setDisabled({ left: index - 1 === 0, right: false })
    setIndex(index - 1)
  }

  const onOpen = () => {
    setViewer({ open: true, url: outputs[index] })
  }

  const [open, setOpen] = React.useState(false);

  const handleTooltipClose = () => {
    setOpen(false);
  };

  const handleTooltipOpen = () => {
    setOpen(true);
  };

  return (
    <>
        <TableRow >
            <TableCell component="th" scope="row">
                {name}
            </TableCell>
            <TableCell>{unique_id}</TableCell>
            <TableCell>
              <ClickAwayListener onClickAway={handleTooltipClose}>
                <div style={{width: 'fit-content'}}>
                  <LightTooltip
                      PopperProps={{
                        disablePortal: true,
                      }}
                      placement="top"
                      onClose={handleTooltipClose}
                      open={open}
                      disableFocusListener
                      disableHoverListener
                      disableTouchListener
                      title={message || ''}
                  >
                    <Button onClick={handleTooltipOpen} disabled={!message}>
                      <ExperimentStatusIcon status={success} />
                    </Button>
                  </LightTooltip>
                </div>
              </ClickAwayListener>
            </TableCell>
            <TableCell>
                <Button disabled={success !== 'success'} onClick={() => onOpen()}>
                    <OpenInNewIcon />
                </Button>
            </TableCell>
        </TableRow>
      {viewer.open &&
          <ImageView
              editAttribute={false}
              disabled={disabled}
              url={viewer.url && `${BASE_URL}${viewer.url}`}
              open={viewer.open}
              onClose={onCloseImageView}
              onNext={onNext}
              onPrevious={onPrevious}
          />}
    </>
  )
}

const LightTooltip = styled(({ className, ...props }: TooltipProps) => (
    <Tooltip {...props} classes={{ popper: className }} />
))(({ theme }) => ({
  [`& .${tooltipClasses.tooltip}`]: {
    backgroundColor: theme.palette.common.white,
    color: 'red',
    boxShadow: theme.shadows[1],
    fontSize: 15,
  },
}));
