import {
  styled,
  Box,
  Typography,
  Container,
  Button,
  DialogContent,
  Dialog,
  DialogActions,
  DialogContentText
} from "@mui/material";
import { useCallback, useState } from "react";
import { downloadGenerate, loadParams, postGenerate, saveParams } from "api/visualize";
import Loading from "../common/Loading";
import { useSearchParams} from "react-router-dom";
import { useNavigate } from 'react-router-dom'
import { BASE_URL } from "../../const/API";
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos'

type InputType = {
  text: string
  value?: string
  onChange: (e: any) => void
  error: string
}

type CutCoordsType = {
  coronal: string
  sagittal: string
  horizontal: string
}

type ParamsType = {
  cut_coords: CutCoordsType
  threshold: string
}

type AlertDialogProps = {
  open: boolean
  handleClose: () => void
  onSaveParams: () => void
}

type GenerateProps = {
  label: string
  urlImage: string
}

const regexInput = /[^0-9,.-]/

const  AlertDialog = ({open, handleClose, onSaveParams}: AlertDialogProps) => {
  return (
      <div>
        <Dialog
            open={open}
            onClose={handleClose}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
        >
          <DialogContent>
            <DialogContentText>
              Save parameters OK?
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button onClick={onSaveParams} autoFocus>
              Ok
            </Button>
          </DialogActions>
        </Dialog>
      </div>
  );
}

const WrapperInput = ({text, value, onChange, error} : InputType) => {
    return (
        <Box sx={{display: 'flex'}}>
              <Typography sx={{minWidth: 100}}>{text}</Typography>
              <Box sx={{display: 'flex', flexDirection: 'column'}}>
                <VisualizeInput
                    name={text}
                    sx={{width: 250}}
                    value={value}
                    onChange={(event: any) => onChange(event)}
                    onBlur={(event: any) => onChange(event)}
                />
                <SpanError>{error}</SpanError>
              </Box>
        </Box>
    )
}

const WrapperGenerate = ({label, urlImage}: GenerateProps) => {
  return (
      <Box
          sx={{
            display: 'flex',
            alignItems: 'center'
          }}
      >
        <Typography
            sx={{
              fontSize: 25,
              minWidth: 130
            }}
        >
          {label}
        </Typography>
        <Image src={BASE_URL + urlImage} alt={''} />
      </Box>
  )
}

const VisualizeNew = () => {
  const [open, setOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false)
  const [searchParams] = useSearchParams()
  const [urlImage, setUrlImage] = useState<string[]>()
  const id = searchParams.get('id')
  const [dataParams, setDataParams] = useState<ParamsType>({
    cut_coords: {
      coronal: '',
      sagittal: '',
      horizontal: '',
    },
    threshold: ''
  })
  const [errors, setErrors] = useState<ParamsType>({
    cut_coords: {
      coronal: '',
      sagittal: '',
      horizontal: '',
    },
    threshold: ''
  })

  const navigate = useNavigate()
  const onClickBack = () => {
    navigate('/projects')
  }

  const onLoadParams = async () => {
    setIsLoading(true)
    try {
      const res = await loadParams()
      const { coronal, sagittal, horizontal} = res.cut_coords
      const newCutCoords = {
        coronal: coronal.join(','),
        sagittal: sagittal.join(','),
        horizontal: horizontal.join(',')
      }
      setDataParams({cut_coords: newCutCoords, threshold: res.threshold.join(',')})
    }
    finally {
      setIsLoading(false)
      setErrors({
        cut_coords: {
          coronal: '',
          sagittal: '',
          horizontal: '',
        },
        threshold: ''
      }
      )}
  }

  const toNumberArr = useCallback((value: string) => {
    return value.split(',').map((item: string) => Number(item))
  },[])

  const onSaveParams = async () => {
    const { coronal, sagittal, horizontal} = dataParams.cut_coords
    const newParams = {
      threshold: toNumberArr(dataParams.threshold),
      cut_coords: {
        coronal: toNumberArr(coronal),
        sagittal: toNumberArr(sagittal),
        horizontal: toNumberArr(horizontal)
      }
    }
    setIsLoading(true)
    try {
      await saveParams(newParams)
    }
    finally {
      setIsLoading(false)
      setOpen(false)
    }
  }

  const validateParams = (value: string, name: string) => {
    if (!value) return 'This field is required'
    const newArr = value.split(',')
    const checkArr = newArr.some((item: string) => !Number(item) && item !== '0')
    if (name === 'threshold') {
      if (checkArr || newArr.length !== 1) {
        return 'wrong format [single float]'
      }
      return ''
    }
    if(checkArr) {
      return 'wrong format [float, ...]'
    }
    return ''
  }

  const onChangeParams = (event: any) => {
    let { value, name } = event.target
    if(name === 'threshold') setErrors({...errors, threshold: validateParams(value, name)})
    if(name !== 'threshold') setErrors({...errors, cut_coords: {...errors.cut_coords, [name]: validateParams(value, name)}})
    if((name === 'threshold' && regexInput.test(value)) || (name !== 'threshold' && regexInput.test(value))) {
      const checkChar = (checkChar: any, value: string) => {
        const arrValue = value.split('')
        const index = arrValue.findIndex((item: string) => {
          if(name === 'threshold') {
            return regexInput.test(item)
          }
          return regexInput.test(item)
        })
        if(index !== -1) {
          value = value.replace(value[index], '')
          return checkChar(checkChar, value)
        }
        return value
      }
      value = checkChar(checkChar, value)
    }
    if(name === 'threshold') {
       setDataParams({...dataParams, threshold: value})
      return
    }
    const newCutCoords = {...dataParams.cut_coords, [name]: value}
    setDataParams({...dataParams, cut_coords: newCutCoords})
  }
  
  const handleClickOpen = () => {
    const { coronal, sagittal, horizontal} = dataParams.cut_coords
    const { cut_coords } = errors
    setErrors({
      cut_coords: {
        coronal: validateParams(coronal, 'coronal'),
        sagittal: validateParams(sagittal, 'sagittal'),
        horizontal: validateParams(horizontal, 'horizontal'),
      },
      threshold: validateParams(dataParams.threshold, 'threshold')
    })
    if( !coronal || ! sagittal || !horizontal || !dataParams.threshold ) return
    if(Object.keys(cut_coords).some((item) => !!(cut_coords as any)?.[item] || errors.threshold)) return
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const onGenarate = async () => {
    if(!id) return
    setIsLoading(true)
    const { coronal, sagittal, horizontal} = dataParams.cut_coords
    const newParams = {
      threshold: toNumberArr(dataParams.threshold),
      cut_coords: [toNumberArr(coronal), toNumberArr(sagittal), toNumberArr(horizontal)]
    }
    try {
      const data = await postGenerate(newParams, id)
      setUrlImage(data.image_urls)
    }
    finally {
      setIsLoading(false)
    }
  }

  const onDownload = async () => {
    if(!id) return
    const { coronal, sagittal, horizontal} = dataParams.cut_coords
    const newParams = {
      threshold: toNumberArr(dataParams.threshold),
      cut_coords: [toNumberArr(coronal), toNumberArr(sagittal), toNumberArr(horizontal)]
    }
    setIsLoading(true)
    try {
      const {data: blob} = await downloadGenerate(newParams, id)
      const url = window.URL.createObjectURL(new Blob([blob], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'visualize-stat');
      link.click();
    }
    finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <Button
        onClick={onClickBack}
        sx={{width: 'fit-content', textTransform: 'unset', fontSize: '1rem'}}
      >
        <ArrowBackIosIcon /> PROJECTS
      </Button>
      <Container>
          <AlertDialog
            open={open}
            handleClose={handleClose}
            onSaveParams={onSaveParams}
          />
          <Title>STAT IMAGES</Title>
          <VisualizeInputWrapper>
            <Box>
                <WrapperInput
                    text={'threshold'}
                    value={dataParams?.threshold || ''}
                    onChange={onChangeParams}
                    error={errors.threshold}
                />
            </Box>
            <CutCoords>
                <Typography>cut_coords</Typography>
                <Box>
                    <WrapperInput
                        text={'coronal'}
                        value={dataParams?.cut_coords.coronal || ''}
                        onChange={onChangeParams}
                        error={errors.cut_coords.coronal}
                    />
                    <WrapperInput
                        text={'sagittal'}
                        value={dataParams?.cut_coords.sagittal || ''}
                        onChange={onChangeParams}
                        error={errors.cut_coords.sagittal}
                    />
                    <WrapperInput
                        text={'horizontal'}
                        value={dataParams?.cut_coords.horizontal || ''}
                        onChange={onChangeParams}
                        error={errors.cut_coords.horizontal}
                    />
                </Box>
            </CutCoords>
            <Box sx={{
              display: 'flex',
              flexDirection: 'column',
              gap: 2
            }}>
              <ParamsButton onClick={onLoadParams}>Load Params</ParamsButton>
              <ParamsButton onClick={handleClickOpen}>Save Params</ParamsButton>
            </Box>
          </VisualizeInputWrapper>
          <ButtonWrapper>
              <VisualizeButton onClick={onGenarate}>GENERATE</VisualizeButton>
              <VisualizeButton onClick={onDownload}>DOWNLOAD</VisualizeButton>
          </ButtonWrapper>
          {
              urlImage ?
              <ImageWrapper>
                 <WrapperGenerate label={'coronal'} urlImage={urlImage[0]}/>
                 <WrapperGenerate label={'sagittal'} urlImage={urlImage[1]}/>
                 <WrapperGenerate label={'horizontal'} urlImage={urlImage[2]}/>
              </ImageWrapper> : null
          }
          {
            isLoading &&
            <Loading />
          }
      </Container>
    </div>
  )
}

const Title = styled(Typography)({
    fontSize: 25,
    fontWeight: 700,
    margin: '50px 0',
})

const CutCoords = styled(Box)({
    display: 'flex',
    gap: 10,
    marginBottom: 50
})

const VisualizeInputWrapper = styled(Box)({
    display: 'flex',
    justifyContent: 'space-between'
})

const ParamsButton = styled('button')({
  height: 'fit-content',
  padding: 5,
  '&:hover': {
    cursor: 'pointer',
    background: '#d1d7e0',
  }
})

const ButtonWrapper = styled(Box)({
    display: 'flex',
    gap: 10,
    marginBottom: 50
})

const VisualizeButton = styled('button')({
    border: '1px solid #006fff',
    color: '#006fff',
    padding: 10,
    '&:hover': {
        cursor: 'pointer',
        background: '#d1d7e0'
    }
})

const VisualizeInput = styled('input')({
    height: 'fit-content',
})

const SpanError = styled('span')({
  color: 'red'
})

const ImageWrapper = styled(Box)({
    display: 'flex',
    flexDirection: 'column',
    gap: 10,
    width: '100%',
    margin: 'auto',
    paddingBottom: 70
})

const Image = styled('img')({
    width: '100%',
    objectFit: 'contain',
})

export default VisualizeNew
