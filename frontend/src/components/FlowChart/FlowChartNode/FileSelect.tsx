import React, { useContext, useEffect } from 'react'
import { Button, Typography } from '@mui/material'
import ButtonGroup from '@mui/material/ButtonGroup'

import { FILE_TREE_TYPE } from 'api/files/Files'
import { LinearProgressWithLabel } from './LinerProgressWithLabel'
import {
  AlignmentData,
  FILE_TYPE,
  Params,
} from 'store/slice/InputNode/InputNodeType'
import { useFileUploader } from 'store/slice/FileUploader/FileUploaderHook'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { DialogContext } from '../DialogContext'
import { useSelector } from 'react-redux'
import {
  selectInputNodeById,
  selectInputNodeParam,
} from 'store/slice/InputNode/InputNodeSelectors'
import { setInputNodeParamAlignment } from 'store/slice/InputNode/InputNodeSlice'
import { useDispatch } from 'react-redux'

export const FileSelect = React.memo<{
  multiSelect?: boolean
  filePath: string | string[]
  fileType: FILE_TYPE
  nodeId?: string
  onChangeFilePath: (path: string | string[]) => void
}>(({ multiSelect = false, filePath, nodeId, fileType, onChangeFilePath }) => {
  const {
    // filePath: uploadedFilePath,
    onUploadFile,
    pending,
    uninitialized,
    progress,
    error,
  } = useFileUploader({ fileType, nodeId })
  const onUploadFileHandle = (formData: FormData, fileName: string) => {
    onUploadFile(formData, fileName)
  }
  return (
    <>
      {!uninitialized && pending && progress != null && (
        <div style={{ marginLeft: 2, marginRight: 2 }}>
          <LinearProgressWithLabel value={progress} />
        </div>
      )}
      <FileSelectImple
        nodeId={nodeId}
        multiSelect={multiSelect}
        filePath={filePath}
        onSelectFile={onChangeFilePath}
        onUploadFile={onUploadFileHandle}
        fileTreeType={fileType}
        selectButtonLabel={`Select ${fileType}`}
      />
      {error != null && (
        <Typography variant="caption" color="error">
          {error}
        </Typography>
      )}
    </>
  )
})

type FileSelectImpleProps = {
  multiSelect?: boolean
  filePath: string | string[]
  onUploadFile: (formData: FormData, fileName: string) => void
  onSelectFile: (path: string | string[]) => void
  fileTreeType?: FILE_TREE_TYPE
  selectButtonLabel?: string
  uploadButtonLabel?: string
  nodeId?: string
}

export const FileSelectImple = React.memo<FileSelectImpleProps>(
  ({ filePath, nodeId }) => {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()
    const { onOpenImageAlignment, images } = useContext(DialogContext)
    const dispatch = useDispatch()

    const inputNode = useSelector(
      selectInputNodeParam(nodeId || ''),
    ) as AlignmentData

    const id = searchParams.get('id')

    useEffect(() => {
      if (!nodeId) return
      let newParams: Params[] = []
      if (Array.isArray(filePath)) {
        newParams = filePath.map((path: string) => {
          const image = images.find((image) => image.url === path)
          return {
            image_id: image?.id || path,
            x_pos: 0,
            x_resize: 1,
            x_rotate: 0,
            y_pos: 0,
            y_resize: 1,
            y_rotate: 0,
            z_pos: 0,
            z_resize: 1,
            z_rotate: 0,
          }
        })
      }
      dispatch(
        setInputNodeParamAlignment({
          nodeId,
          param: newParams,
        }),
      )
      //eslint-disable-next-line
    }, [filePath, nodeId, JSON.stringify(images)])

    const getNameSelectec = () => {
      if (Array.isArray(filePath)) {
        return `${filePath.length} images selected.`
      }
      return `${filePath ? 1 : 0} images selected.`
    }

    return (
      <div style={{ padding: 16 }}>
        <ButtonGroup size="small" style={{ width: '90%', margin: 'auto' }}>
          <Button
            style={{ width: '80%' }}
            variant="outlined"
            onClick={() =>
              navigate(
                `/projects/new-project?id=${id}&nodeId=${nodeId}&back=/projects/workflow?tab=0&id=${id}`,
              )
            }
          >
            EDIT IMAGESET
          </Button>
        </ButtonGroup>
        <div style={{ marginTop: 8 }}>
          <Typography className="selectFilePath" variant="caption">
            {getNameSelectec()}
          </Typography>
        </div>
        <ButtonGroup size="small" style={{ width: '90%', margin: '8px 0' }}>
          <Button
            disabled={!filePath || !filePath.length}
            onClick={() => {
              if (!nodeId) return
              onOpenImageAlignment(true, {
                nodeId,
                alignments: inputNode?.alignments?.value || [],
              })
            }}
            style={{ width: '80%' }}
            variant="outlined"
          >
            ALIGNMENT
          </Button>
        </ButtonGroup>
      </div>
    )
  },
)
