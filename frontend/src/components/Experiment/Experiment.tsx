import React, {useCallback, useEffect, useState} from 'react'
import {ExperimentTable} from './ExperimentTable'
import {useSearchParams} from "react-router-dom";
import {getResultProject} from "../../api/experiments/Experiments";
import {EXPERIMENTS_STATUS} from "../../store/slice/Experiments/ExperimentsType";
import Loading from "../common/Loading";

export type FunctionType = {
  name: string
  message?: string
  outputs: string[]
  success: EXPERIMENTS_STATUS
  unique_id: string
}

export type Data = {
  [key: string]: {
    name: string
    unique_id: string
    results: {
      name: string
      subject_id: string
      nodeDict: object
      edgeDict: object
      function: object
    }[]
    status: EXPERIMENTS_STATUS
    started_at: string
    finished_at: string
  }
}

const Experiment = React.memo(() => {
  const [searchParams] = useSearchParams()
  const [data, setData] = useState<Data>()
  const [isLoading, setIsLoading] = useState(false)
  const id = searchParams.get('id')
  const fetchData = useCallback(async () => {
    setIsLoading(true)
    if(!id) return
    try {
      const res = await getResultProject(id)
      setData(res)
    }
    catch {}
    finally {
      setIsLoading(false)
    }
  }, [id])
  useEffect(() => {
    fetchData()
    //eslint-disable-next-line
  }, [])

  return (
    <div style={{ display: 'flex', height: 'calc(100% - 58px)' }}>
      <main
        style={{
          display: 'flex',
          flexDirection: 'column',
          flexGrow: 1,
          height: '100%',
          padding: 16,
        }}
      >
        <ExperimentTable data={data}/>
        {
          isLoading ? <Loading /> : null
        }
      </main>
    </div>
  )
})

export default Experiment
