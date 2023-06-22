import { Box, styled, Typography } from '@mui/material'
import {
  FC,
  MouseEvent,
  useCallback,
  useEffect,
  useRef,
  useState,
  TouchEvent,
} from 'react'

type ChangeDragProps = {
  title: string
  value: number
  onChange: (value: number) => void
  className?: string
  max?: number
  min?: number
  onChangeMin?: (v: number) => any
  showInputMax?: boolean
  showInputMin?: boolean
}

const ChangeDrag: FC<ChangeDragProps> = (props) => {
  const { title, value, onChange, className, max = 2, min = 0 } = props
  const { onChangeMin, showInputMax } = props
  const [width, setWidth] = useState(0)
  const mouseDown = useRef(0)

  const refDrag = useRef<any>()
  const refDot = useRef<any>()

  useEffect(() => {
    getWidth()
    //eslint-disable-next-line
  }, [])

  const getWidth = () => {
    if (!refDrag.current) getWidth()
    setWidth(refDrag.current.clientWidth - 24)
  }

  const onMouseDown = useCallback((event: MouseEvent<HTMLDivElement>) => {
    mouseDown.current = event.pageX
    refDrag.current.style.cursor = 'grabbing'
    refDot.current.style.cursor = 'grabbing'
  }, [])

  const onTouchStart = useCallback((event: TouchEvent<HTMLDivElement>) => {
    mouseDown.current = event.touches[0].pageX
    refDrag.current.style.cursor = 'grabbing'
    refDot.current.style.cursor = 'grabbing'
  }, [])

  const onMouseMove = (event: MouseEvent<HTMLDivElement>) => {
    if (!mouseDown.current) return
    const mouseInit = refDrag.current.getBoundingClientRect().x
    const mouseMove = event.pageX - mouseInit - 12
    let scale = (mouseMove / width) * (max - min) + min
    if (scale > max) scale = max
    if (scale < min) scale = min
    onChange(scale)
  }

  const onTouchMove = (event: TouchEvent<HTMLDivElement>) => {
    if (!mouseDown.current) return
    const mouseInit = refDrag.current.getBoundingClientRect().x
    const mouseMove = event.touches[0].pageX - mouseInit
    let scale = (mouseMove / width) * (max - min)
    if (scale > max) scale = max
    if (scale < min) scale = min
    onChange(Number(scale.toFixed(2)))
  }

  const onMouseLeave = useCallback(() => {
    mouseDown.current = 0
    refDrag.current.style.cursor = 'default'
    refDot.current.style.cursor = ''
  }, [])

  return (
    <ScaleWrapper
      className={className}
      ref={refDrag}
      onMouseMove={onMouseMove}
      onTouchMove={onTouchMove}
      onMouseLeave={onMouseLeave}
      onMouseUp={onMouseLeave}
    >
      <TitleScale>{title}</TitleScale>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Input
          value={Number(value.toPrecision(2))}
          onChange={(e) => onChangeMin?.(Number(e.target.value))}
        />
        {showInputMax ? (
          <Input
            style={{ textAlign: 'right' }}
            value={Number(max.toPrecision(2))}
            readOnly
          />
        ) : null}
      </div>
      <BoxWrapper>
        <BoxLine style={{ width: ((value - min) * width) / (max - min) }} />
        <Dot
          ref={refDot}
          onMouseDown={onMouseDown}
          onTouchEnd={onMouseLeave}
          onTouchStart={onTouchStart}
          style={{ left: ((value - min) * width) / (max - min) }}
        />
      </BoxWrapper>
    </ScaleWrapper>
  )
}

const BoxWrapper = styled(Box)(() => ({
  width: '100%',
  height: 4,
  background: 'rgba(60, 60, 67, 0.18)',
  position: 'relative',
  borderRadius: 2,
  userSelect: 'none',
}))

const Dot = styled(Box)(() => ({
  position: 'absolute',
  width: 24,
  height: 24,
  background: '#7a7a7a',
  borderRadius: 100,
  top: -11,
  cursor: 'pointer',
}))

const TitleScale = styled(Typography)(() => ({
  fontSize: 14,
  fontWeight: 700,
}))

const BoxLine = styled(Box)(() => ({
  position: 'absolute',
  height: 4,
  background: '#0A7AFF',
  borderRadius: 2,
}))

const ScaleWrapper = styled(Box)(({ theme }) => ({
  paddingBottom: 20,
  '@media (max-width: 809px)': {
    paddingTop: theme.spacing(2),
  },
}))

const Input = styled('input')({
  border: 'none',
  outline: 'none',
  width: 50,
  marginBottom: 20,
})

export default ChangeDrag
