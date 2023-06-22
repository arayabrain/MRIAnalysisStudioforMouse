export const INPUT_NODE_SLICE_NAME = 'inputNode'

export const FILE_TYPE_SET = {
  CSV: 'csv',
  IMAGE: 'image',
  HDF5: 'hdf5',
  FLUO: 'fluo',
  BEHAVIOR: 'behavior',
} as const

export type Params = {
  image_id: number | string
  x_pos: number
  y_pos: number
  z_pos: number
  x_rotate: number
  y_rotate: number
  z_rotate: number
  x_resize: number
  y_resize: number
  z_resize: number
}

export type AlignmentData = {
  alignments: {
    path: string
    type: string
    value: Params[]
  }
}

export type FILE_TYPE = typeof FILE_TYPE_SET[keyof typeof FILE_TYPE_SET]

export type InputNode = {
  [nodeId: string]: InputNodeType
}

export type InputNodeType = CsvInputNode | ImageInputNode | HDF5InputNode

interface InputNodeBaseType<
  T extends FILE_TYPE,
  P extends { [key: string]: unknown },
> {
  fileType: T
  selectedFilePath?: string | string[]
  param: P
}

export type CsvInputParamType = {
  setHeader: number | null
  setIndex: boolean
  transpose: boolean
}

export interface CsvInputNode
  extends InputNodeBaseType<'csv', CsvInputParamType> {
  selectedFilePath?: string
}

export interface ImageInputNode
  extends InputNodeBaseType<'image', AlignmentData> {
  selectedFilePath?: string[]
}

export interface HDF5InputNode extends InputNodeBaseType<'hdf5', {}> {
  selectedFilePath?: string
  hdf5Path?: string
}
