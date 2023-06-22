import { RootState } from 'store/store'
import { SubFolder } from './DatasetType'

export const selectDataset = (state: RootState) => state.dataset

export const selectCurrentProjectId = (state: RootState) =>
  state.dataset.project_id

export const getUrlFromSubfolder = (
  subfolders: SubFolder[] = [],
  urls: { id: string | number; url: string }[],
) => {
  subfolders.forEach((sub) => {
    if (sub.sub_folders) {
      getUrlFromSubfolder(sub.sub_folders, urls)
    } else if (sub.images?.length) {
      const urlsImage = sub.images.map((image) => ({
        url: image.image_url,
        id: image.id,
      }))
      urls.push(...urlsImage)
    }
  })
  return urls
}

export const selectListImageUrl = (
  state: RootState,
): { id: string | number; url: string }[] => {
  if (!state.dataset.dataset) return []
  let urls: { id: string | number; url: string }[] = []
  urls = getUrlFromSubfolder(state.dataset.dataset, urls)
  return urls
}
