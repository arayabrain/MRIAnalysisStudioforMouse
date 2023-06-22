import axios from 'utils/axios'
import { DATABASE_URL_HOST } from 'const/API'

export const getDataBaseTree = async () => {
  const response = await axios.get(`${DATABASE_URL_HOST}/rawdb/search`)
  return response.data
}

export const getDataBaseList = async () => {
  const response = await axios.get(`${DATABASE_URL_HOST}/rawdb/search/list`)
  return response.data
}

export const getRawdb = async (id: number) => {
  const response = await axios.get(`${DATABASE_URL_HOST}/rawdb/${id}`)
  return response.data
}

export const editAttributes = async (id: number, data: string) => {
  const response = await axios.put(`${DATABASE_URL_HOST}/rawdb/${id}`, data)
  return response.data
}

export const deleteRawDb = async (id: number | string) => {
  const response = await axios.delete(`${DATABASE_URL_HOST}/rawdb/${id}`)
  return response.data
}
