import { type } from 'os'

declare module 'react-flow-renderer' {
  type ReactFlowProvider = FC<any>
  type addEdge = (
    edgeParams: Edge | Connection,
    elements: Elements<any>,
  ) => Elements<any>
  type Controls = any
  type FlowElement<T = any> = Node<T> | Edge<T>
  type Elements<T = any> = Array<FlowElement<T>>
  type ElementId = string
  type Connection = {
    source: ElementId | null
    target: ElementId | null
    sourceHandle: ElementId | null
    targetHandle: ElementId | null
  }
  interface Edge<T = any> {
    id: ElementId
    type?: string
    source: ElementId
    target: ElementId
    sourceHandle?: ElementId | null
    targetHandle?: ElementId | null
    label?: string | ReactNode
    labelStyle?: CSSProperties
    labelShowBg?: boolean
    labelBgStyle?: CSSProperties
    labelBgPadding?: [number, number]
    labelBgBorderRadius?: number
    style?: CSSProperties
    animated?: boolean
    arrowHeadType?: ArrowHeadType
    isHidden?: boolean
    data?: T
    className?: string
  }
  interface Node<T = any> {
    id: ElementId
    position: XYPosition
    type?: string
    __rf?: any
    data?: T
    style?: CSSProperties
    className?: string
    targetPosition?: Position
    sourcePosition?: Position
    isHidden?: boolean
    draggable?: boolean
    selectable?: boolean
    connectable?: boolean
    dragHandle?: string
  }
}
