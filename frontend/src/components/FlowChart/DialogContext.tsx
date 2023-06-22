import { FILE_TREE_TYPE } from 'api/files/Files'
import { createContext } from 'react'
import { Params } from 'store/slice/InputNode/InputNodeType'

export declare type OpenDialogValue = {
  filePath: string | string[]
  open: boolean
  fileTreeType?: FILE_TREE_TYPE
  multiSelect: boolean
  onSelectFile: (path: string | string[]) => void
}

export declare type ErrorDialogValue = {
  anchorElRef: { current: Element | null }
  message: string
}

export const DialogContext = createContext<{
  onOpen: (nodeId: string) => void
  onOpenDialogFile: (value: OpenDialogValue) => void
  onMessageError: (value: ErrorDialogValue) => void
  images: { id: string | number; url: string }[]
  onOpenImageAlignment: (
    v: boolean,
    params?: { nodeId: string; alignments: Params[] },
  ) => void
}>({
  onOpen: () => null,
  onOpenDialogFile: () => null,
  onMessageError: () => null,
  onOpenImageAlignment: () => null,
  images: [],
})
