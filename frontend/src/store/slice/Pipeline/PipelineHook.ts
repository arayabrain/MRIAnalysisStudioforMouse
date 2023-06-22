import React from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useSearchParams, useLocation, useNavigate } from 'react-router-dom'
import { selectRunPostData } from 'store/selectors/run/RunSelectors'
import {
  selectPipelineIsCanceled,
  selectPipelineIsStartedSuccess,
  selectPipelineLatestUid,
  selectPipelineStatus,
} from './PipelineSelectors'
import { run, pollRunResult, runByCurrentUid } from './PipelineActions'
import { cancelPipeline, setRunBtnOption } from './PipelineSlice'
import { selectFilePathIsUndefined } from '../InputNode/InputNodeSelectors'
import { selectAlgorithmNodeNotExist } from '../AlgorithmNode/AlgorithmNodeSelectors'
import { useSnackbar } from 'notistack'
import { RUN_BTN_OPTIONS, RUN_STATUS } from './PipelineType'
import {
  fetchExperiment,
  getExperiments,
  importExperimentByUid,
} from '../Experiments/ExperimentsActions'
import { reset } from '../Dataset/DatasetSlice'
import { getDatasetList } from '../Dataset/DatasetAction'
import { AppDispatch } from 'store/store'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone' // dependent on utc plugin
import { setLoadingExpriment } from '../Experiments/ExperimentsSlice'
import { getUrlFromSubfolder } from '../Dataset/DatasetSelector'

dayjs.extend(utc)
dayjs.extend(timezone)

const POLLING_INTERVAL = 5000

export type UseRunPipelineReturnType = ReturnType<typeof useRunPipeline>

export function useRunPipeline() {
  const dispatch = useDispatch()
  const appDispatch: AppDispatch = useDispatch()
  const uid = useSelector(selectPipelineLatestUid)
  const isCanceled = useSelector(selectPipelineIsCanceled)
  const isStartedSuccess = useSelector(selectPipelineIsStartedSuccess)
  const filePathIsUndefined = useSelector(selectFilePathIsUndefined)
  const algorithmNodeNotExist = useSelector(selectAlgorithmNodeNotExist)
  const runPostData = useSelector(selectRunPostData)
  const [searchParams] = useSearchParams()
  const projectId = searchParams.get('id')
  const navigate = useNavigate()

  const handleRunPipeline = React.useCallback(
    (name: string) => {
      dispatch(run({ runPostData: { name, ...runPostData, forceRunList: [] } }))
    },
    [dispatch, runPostData],
  )
  const handleRunPipelineByUid = React.useCallback(() => {
    dispatch(runByCurrentUid({ runPostData }))
  }, [dispatch, runPostData])
  const location = useLocation()

  React.useEffect(() => {
    window.addEventListener('beforeunload', removeStateIsEdit)
    if (!projectId) {
      navigate('/projects')
    } else {
      if (!location.state?.cancel) {
        appDispatch(getDatasetList({ project_id: projectId }))
          .unwrap()
          .then(({ dataset, last_updated_time }) => {
            let urls: { id: string | number; url: string }[] = []
            getUrlFromSubfolder(dataset, urls)
            appDispatch(fetchExperiment({ projectId, urls }))
              .unwrap()
              .then(({ data: { finished_at } }) => {
                const imgsetUpdatedSinceLastRun = dayjs(
                  dayjs(last_updated_time).format('YYYY-MM-DD HH:mm'),
                ).diff(
                  dayjs(dayjs(finished_at).format('YYYY-MM-DD HH:mm')),
                  'm',
                ) > 0
                imgsetUpdatedSinceLastRun && dispatch(
                  setRunBtnOption({
                    runBtnOption: RUN_BTN_OPTIONS.RUN_NEW,
                    runAlreadyDisabled: true,
                  }),
                )
              })
              .catch((_) => {
                appDispatch(
                  importExperimentByUid({ uid: 'default', urls }),
                )
              })
          })
      } else {
        appDispatch(getDatasetList({ project_id: projectId })).then(() => {
          dispatch(setLoadingExpriment({ loading: false }))
        })
      }
    }

    return () => {
      dispatch(reset())
      dispatch(setLoadingExpriment({ loading: true }))
      window.removeEventListener('beforeunload', removeStateIsEdit)
    }
    //eslint-disable-next-line
  }, [])

  const removeStateIsEdit = () => {
    navigate(location.pathname, { replace: true })
  }

  const handleCancelPipeline = React.useCallback(() => {
    if (uid != null) {
      dispatch(cancelPipeline())
    }
  }, [dispatch, uid])

  React.useEffect(() => {
    const intervalId = setInterval(() => {
      if (isStartedSuccess && !isCanceled && uid != null) {
        dispatch(pollRunResult({ uid: uid }))
      }
    }, POLLING_INTERVAL)
    return () => {
      clearInterval(intervalId)
    }
  }, [dispatch, uid, isCanceled, isStartedSuccess])

  const status = useSelector(selectPipelineStatus)

  const { enqueueSnackbar } = useSnackbar()
  // タブ移動による再レンダリングするたびにスナックバーが実行されてしまう挙動を回避するために前回の値を保持
  const [prevStatus, setPrevStatus] = React.useState(status)
  React.useEffect(() => {
    if (prevStatus !== status) {
      if (status === RUN_STATUS.FINISHED) {
        enqueueSnackbar('Finished', { variant: 'success' })
        dispatch(getExperiments())
      } else if (status === RUN_STATUS.START_SUCCESS) {
        dispatch(getExperiments())
      } else if (status === RUN_STATUS.ABORTED) {
        enqueueSnackbar('Aborted', { variant: 'error' })
        dispatch(getExperiments())
      } else if (status === RUN_STATUS.CANCELED) {
        enqueueSnackbar('Canceled', { variant: 'info' })
        dispatch(getExperiments())
      }
      setPrevStatus(status)
    }
  }, [dispatch, status, prevStatus, enqueueSnackbar])

  return {
    filePathIsUndefined,
    algorithmNodeNotExist,
    uid,
    status,
    isStartedSuccess,
    handleRunPipeline,
    handleRunPipelineByUid,
    handleCancelPipeline,
  }
}
