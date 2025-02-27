import type {
  ExperimentDTO,
  ExperimentsDTO,
  FunctionsDTO,
} from 'api/experiments/Experiments'
import type {
  ExperimentListType,
  ExperimentType,
  ExperimentFunction,
  EXPERIMENTS_STATUS,
} from './ExperimentsType'
import { RunResultDTO } from 'api/run/Run'
export function convertToExperimentListType(
  dto: ExperimentsDTO,
): ExperimentListType {
  const experimentList: ExperimentListType = {}
  Object.entries(dto).forEach(([uid, value]) => {
    experimentList[uid] = convertToExperimentType(value)
  })
  return experimentList
}

export function convertToExperimentType(dto: ExperimentDTO): ExperimentType {
  const functions: { [nodeId: string]: ExperimentFunction } = {}
  Object.entries(dto.function).forEach(([_, value]) => {
    functions[value.unique_id] = {
      name: value.name,
      nodeId: value.unique_id,
      status: convertToExperimentStatus(value.success),
      hasNWB: value.hasNWB,
    }
  })
  return {
    uid: dto.unique_id,
    timestamp: dto.started_at,
    status: dto.success,
    name: dto.name,
    hasNWB: dto.hasNWB,
    functions,
  }
}

export function convertFunctionsToRunResultDTO(
  dto: FunctionsDTO,
): RunResultDTO {
  const result: RunResultDTO = {}
  Object.entries(dto).forEach(([key, value]) => {
    result[key] = {
      status: value.success,
      message: value.message ?? '',
      name: value.name,
      outputPaths: value.outputPaths,
    }
  })
  return result
}

function convertToExperimentStatus(dto: string): EXPERIMENTS_STATUS {
  switch (dto) {
    case 'running':
      return 'running'
    case 'success':
      return 'success'
    case 'error':
      return 'error'
    default:
      throw new Error('failed to convert to EXPERIMENTS_STATUS')
  }
}

export function convertToFlowChartList(
  dto: ExperimentsDTO,
): ExperimentListType {
  const experimentList: ExperimentListType = {}
  Object.entries(dto).forEach(([uid, value]) => {
    experimentList[uid] = convertToExperimentType(value)
  })
  return experimentList
}
