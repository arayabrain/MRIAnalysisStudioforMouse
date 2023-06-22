import { createContext } from 'react'

export const DialogContext = createContext<{
  onOpen: (nodeId: string) => any
  onOpenDialogFile: (value: {
    filePath: string | string[]
    open: boolean
    fileTreeType?: string
    multiSelect: boolean
    onSelectFile: (path: string | string[]) => any
  }) => any
  onMessageError: (v: {
    anchorElRef: { current: Element | null }
    message: string
  }) => any
  onOpenImageAlignment: (
    nodeId: boolean,
    params: { [key: string]: string | undefined },
  ) => any
}>({
  onOpen: () => null,
  onOpenDialogFile: () => null,
  onMessageError: () => null,
  onOpenImageAlignment: () => null,
})
