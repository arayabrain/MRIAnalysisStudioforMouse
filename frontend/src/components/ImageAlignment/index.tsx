import { Box, IconButton, Modal, styled } from '@mui/material'
import { ChangeEvent, FC, useEffect, useMemo, useRef, useState } from 'react'
import CloseIcon from '@mui/icons-material/Close'
import { ObjectType } from 'pages/Database'
import { useDispatch } from 'react-redux'
import { setInputNodeParamAlignment } from 'store/slice/InputNode/InputNodeSlice'
import { Params } from 'store/slice/InputNode/InputNodeType'
import { DATABASE_URL_HOST } from 'const/API'

type ImageViewProps = {
  open: boolean
  onClose?: () => void
  onNext?: () => void
  onPrevious?: () => void
  urls: { id: string | number; url: string }[]
  jsonData?: ObjectType
  disabled?: { left: boolean; right: boolean }
  params?: { nodeId: string; alignments: Params[] }
  readOnly?: boolean
}

const ImageAlignment: FC<ImageViewProps> = ({
  open,
  onClose,
  urls,
  params = { nodeId: '', alignments: [] },
  readOnly = false,
}) => {
  const viewerRef = useRef<any>()
  const [image, setUrl] = useState(urls[0])
  const [isLoadFile, setIsLoadFile] = useState(false)
  const [loadedSuccess, setLoadedSuccess] = useState(false)
  const volumes = useRef<any>()
  const dispatch = useDispatch()

  const urlRef = useRef(image)

  const [stateParams, setStateParams] = useState<Params[]>(params.alignments)

  const paramAligment = useMemo(() => {
    return stateParams.find((param) => param.image_id === image?.id)
  }, [image?.id, stateParams])

  useEffect(() => {
    if (open) {
      setTimeout(loadFile, 200)
    }
    return () => {
      viewerRef.current.clearVolumes?.()
    }
    //eslint-disable-next-line
  }, [])

  useEffect(() => {
    urlRef.current = image
    loadFileIndex()
    //eslint-disable-next-line
  }, [image])

  useEffect(() => {
    if (loadedSuccess) {
      const paramInit = params.alignments?.find(
        (param) => param.image_id === image.id,
      )
      setValueToBraibrowser(paramInit)
    }
    //eslint-disable-next-line
  }, [loadedSuccess, image.id])

  const onOk = () => {
    if (params?.nodeId && stateParams) {
      dispatch(
        setInputNodeParamAlignment({
          nodeId: params.nodeId,
          param: stateParams,
        }),
      )
    }
    onClose?.()
  }

  const onPreImage = () => {
    const index = urls.findIndex((item) => item.id === image.id)
    if (index === 0) return
    setUrl(urls[index - 1])
  }

  const onNextImage = () => {
    const index = urls.findIndex((item) => item.id === image.id)
    if (index === urls.length - 1) return
    setUrl(urls[index + 1])
  }

  const setValueToBraibrowser = (valueParams?: Params) => {
    if (valueParams) {
      volumes.current.setResize({
        x: Number(valueParams.x_resize),
        y: Number(valueParams.y_resize),
        z: Number(valueParams.z_resize),
      })
      volumes.current.setRadian(
        Number(valueParams.y_rotate),
        Number(valueParams.x_rotate),
        Number(valueParams.z_rotate),
      )
      volumes.current.setVoxelCoords(
        Number(valueParams.y_pos),
        Number(valueParams.z_pos),
        Number(valueParams.x_pos),
      )
      viewerRef.current.redrawVolumes()
    }
  }

  const onChangeValue = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    if (params?.nodeId && stateParams) {
      const newParams = stateParams.map((align) =>
        align.image_id === image.id ? { ...align, [name]: value } : align,
      )
      setStateParams(newParams)
    }
  }

  const onBlurRadian = (e: any) => {
    const { name, value } = e.target
    let valueRadian = Number(value)
    if (isNaN(valueRadian)) {
      valueRadian = 0
    } else if (valueRadian < 0) {
      valueRadian = 0
    } else if (valueRadian > 2 * Math.PI) {
      valueRadian = 0
    }
    if (params?.nodeId && stateParams) {
      const newParams = stateParams.map((align) =>
        align.image_id === image.id ? { ...align, [name]: valueRadian } : align,
      )
      setStateParams(newParams)
    }
  }

  const loadFileIndex = () => {
    if (!image?.url || isLoadFile || !viewerRef.current) return
    setIsLoadFile(true)
    setLoadedSuccess(false)
    viewerRef.current.clearVolumes()
    viewerRef.current.loadVolumes({
      volumes: [
        {
          type: 'nifti1',
          nii_url: `${DATABASE_URL_HOST}${image.url}`,
          template: {
            element_id: 'volume-ui-template',
            viewer_insert_className: 'volume-viewer-display',
          },
          overlay: {
            template: {
              element_id: 'overlay-ui-template',
              viewer_insert_className: 'overlay-viewer-display',
            },
          },
        },
      ],
      complete: () => setValueToBraibrowser(paramAligment),
    })
  }

  const volumeLoaded = (event: any, isLoaded?: boolean) => {
    const brainbrowser = (window as any).BrainBrowser
    const { volume } = event
    volumes.current = volume
    const paramsNode: Params = {
      image_id: urlRef.current.id,
      x_pos: 0,
      y_pos: 0,
      z_pos: 0,
      x_rotate: volume.header.xspace.radian,
      y_rotate: volume.header.yspace.radian,
      z_rotate: volume.header.zspace.radian,
      x_resize: volume.header.xspace.step,
      y_resize: volume.header.yspace.step,
      z_resize: volume.header.zspace.step,
    }
    if (brainbrowser.utils.isFunction(volume.getVoxelCoords)) {
      const voxel = volume.getVoxelCoords()
      paramsNode.x_pos = voxel.k
      paramsNode.y_pos = voxel.i
      paramsNode.z_pos = voxel.j
    }
    const newParams = (pre: Params[]) => {
      if (pre.find((align) => align.image_id === urlRef.current.id)) {
        return pre.map((align) => {
          if (align.image_id === urlRef.current.id) return paramsNode
          return align
        })
      }
      return [...pre, paramsNode]
    }
    setStateParams(newParams)
    setIsLoadFile(false)
    setLoadedSuccess(true)
  }

  const gerenateValueNumber = (value?: number) => {
    if (typeof value === 'undefined') return ''
    return value
  }

  const loadFile = () => {
    if (!image.url || isLoadFile) return
    setIsLoadFile(true)
    setLoadedSuccess(false)
    const brainbrowser = (window as any).BrainBrowser
    const color_map_config = brainbrowser.config.get('color_maps')[2]
    viewerRef.current = brainbrowser.VolumeViewer.start(
      'brainbrowser',
      (viewer: any) => {
        viewer.addEventListener('volumeloaded', (e: any) =>
          volumeLoaded(e, true),
        )
        viewer.addEventListener('sliceupdate', volumeLoaded)
        viewer.addEventListener('error', () => {
          setIsLoadFile(false)
          setTimeout(loadFile, 200)
        })
        const { url: urlColor, cursor_color } = color_map_config
        viewer.loadDefaultColorMapFromURL(urlColor, cursor_color)
        viewer.setDefaultPanelSize(256, 256)
        viewer.render()
        viewer.clearVolumes()
        viewer.loadVolumes({
          volumes: [
            {
              type: 'nifti1',
              nii_url: `${DATABASE_URL_HOST}${image.url}`,
              template: {
                element_id: 'volume-ui-template',
                viewer_insert_className: 'volume-viewer-display',
              },
              overlay: {
                template: {
                  element_id: 'overlay-ui-template',
                  viewer_insert_className: 'overlay-viewer-display',
                },
              },
              complete: function () {
                setIsLoadFile(false)
              },
            },
          ],
        })
      },
    )
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      aria-labelledby="modal-modal-title"
      aria-describedby="modal-modal-description"
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '100%',
          height: '100%',
        }}
      >
        <ImageViewWrapper>
          <div style={{ alignItems: 'stretch' }}>
            <div id="brainbrowser-wrapper">
              <div
                id="volume-viewer"
                style={{
                  minWidth: 768,
                  minHeight: 256,
                  background: '#ffffff',
                }}
              >
                <div id="brainbrowser"></div>
              </div>
              <Flex>
                <BoxSet>
                  <ContentSet>
                    <Flex>
                      <Text>right {'{mm}'}</Text>
                      <input
                        type={'number'}
                        name="x_pos"
                        value={gerenateValueNumber(paramAligment?.x_pos)}
                        onChange={onChangeValue}
                        readOnly={readOnly}
                      />
                    </Flex>
                    <Flex>
                      <Text>forward {'{mm}'}</Text>
                      <input
                        type={'number'}
                        name="y_pos"
                        value={gerenateValueNumber(paramAligment?.y_pos)}
                        onChange={onChangeValue}
                        readOnly={readOnly}
                      />
                    </Flex>
                    <Flex>
                      <Text>up {'{mm}'}</Text>
                      <input
                        type={'number'}
                        name="z_pos"
                        value={gerenateValueNumber(paramAligment?.z_pos)}
                        onChange={onChangeValue}
                        readOnly={readOnly}
                      />
                    </Flex>
                    <Flex>
                      <Text>roll {'{rad}'}</Text>
                      <input
                        name="x_rotate"
                        value={gerenateValueNumber(paramAligment?.x_rotate)}
                        onChange={onChangeValue}
                        onBlur={onBlurRadian}
                        readOnly={readOnly}
                      />
                    </Flex>
                    <Flex>
                      <Text>pitch {'{rad}'}</Text>
                      <input
                        name="y_rotate"
                        value={gerenateValueNumber(paramAligment?.y_rotate)}
                        onChange={onChangeValue}
                        onBlur={onBlurRadian}
                        readOnly={readOnly}
                      />
                    </Flex>
                    <Flex>
                      <Text>yaw {'{rad}'}</Text>
                      <input
                        name="z_rotate"
                        value={gerenateValueNumber(paramAligment?.z_rotate)}
                        onChange={onChangeValue}
                        onBlur={onBlurRadian}
                        readOnly={readOnly}
                      />
                    </Flex>
                    <Flex>
                      <Text>resize {'{x}'}</Text>
                      <input
                        name="x_resize"
                        value={gerenateValueNumber(paramAligment?.x_resize)}
                        onChange={onChangeValue}
                        readOnly={readOnly}
                      />
                    </Flex>
                    <Flex>
                      <Text>resize {'{y}'}</Text>
                      <input
                        value={gerenateValueNumber(paramAligment?.y_resize)}
                        name="y_resize"
                        onChange={onChangeValue}
                        readOnly={readOnly}
                      />
                    </Flex>
                    <Flex>
                      <Text>resize {'{z}'}</Text>
                      <input
                        value={gerenateValueNumber(paramAligment?.z_resize)}
                        name="z_resize"
                        onChange={onChangeValue}
                        readOnly={readOnly}
                      />
                    </Flex>
                    <ButtonSet
                      onClick={() => setValueToBraibrowser(paramAligment)}
                    >
                      Set Origin
                    </ButtonSet>
                  </ContentSet>
                </BoxSet>
                <Flex
                  sx={{
                    flexDirection: 'column',
                    position: 'relative',
                    gap: 15,
                    justifyContent: 'center',
                    alignItems: 'center',
                  }}
                >
                  <SwitchImage>
                    <span>Select Image</span>
                    <SwitchContent>
                      <ButtonPre onClick={onPreImage}>{'<'}</ButtonPre>
                      <InputImage value={image.url} readOnly />
                      <ButtonNext onClick={onNextImage}>{'>'}</ButtonNext>
                    </SwitchContent>
                    <span>{`(${
                      urls.findIndex((item) => item.id === image.id) + 1
                    }/${urls.length})`}</span>
                  </SwitchImage>
                  <Flex sx={{ gap: 5 }}>
                    <ButtonCanCel onClick={onClose}>CANCEL</ButtonCanCel>
                    <ButtonOk onClick={onOk}>OK</ButtonOk>
                  </Flex>
                </Flex>
              </Flex>
            </div>
          </div>
          <ButtonClose onClick={onClose}>
            <CloseIconWrapper />
          </ButtonClose>
        </ImageViewWrapper>
      </div>
    </Modal>
  )
}

const ButtonClose = styled(IconButton)({
  width: 50,
  height: 50,
  position: 'absolute',
  right: '10%',
  top: '10%',
  zIndex: 9999,
  background: 'rgba(0, 0, 0, 0.6)',
  '&:hover': {
    background: 'rgba(0, 0, 0, 0.8)',
  },
})

const ButtonPre = styled('button')({
  width: 50,
  height: 50,
  position: 'unset',
  zIndex: 1,
  borderRadius: '50%',
  backgroundColor: 'unset',
  border: 'none',
  cursor: 'pointer',
  fontSize: 20,
  '&:hover': {
    background: 'rgba(0, 0, 0, 0.1)',
  },
})

const ButtonNext = styled(ButtonPre)({
  right: '10%',
})

const InputImage = styled('input')({
  height: 'fit-content',
})

const ImageViewWrapper = styled(Box)({
  marginTop: 48,
  overflow: 'auto',
  margin: 'auto',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: '#fff',
})

const ContentSet = styled(Box)({
  padding: 20,
})

const Flex = styled(Box)({
  display: 'flex',
})

const Text = styled('span')({
  display: 'block',
  minWidth: 150,
})

const ButtonSet = styled('button')({
  marginTop: 20,
  cursor: 'pointer',
})

const BoxSet = styled(Box)({
  border: '2px solid #000',
  width: 'fit-content',
  margin: '30px 50px',
})

const SwitchImage = styled(Box)({
  height: 'max-content',
  display: 'flex',
  alignItems: 'center',
  flexDirection: 'column',
})

const SwitchContent = styled(Box)({
  height: 'max-content',
  display: 'flex',
  alignItems: 'center',
})

const ButtonOk = styled('button')({
  padding: '10px 20px',
  background: '#000000c7',
  border: '2px solid #000',
  color: '#fff',
  cursor: 'pointer',
})

const ButtonCanCel = styled('button')({
  padding: 10,
  border: '2px solid #000',
  cursor: 'pointer',
})

const CloseIconWrapper = styled(CloseIcon)({
  color: '#ffffff',
})

export default ImageAlignment
