import { getRefreshToken } from 'utils/auth'
import axios from 'utils/axios'

export const login = async (data: { email: string; password: string }) => {
  const response = await axios.post('/auth/login', data)
  return response.data
}

export const refreshToken = async () => {
  const response = await axios.post('/auth/refresh', {
    refresh_token: getRefreshToken(),
  })
  return response.data
}

export const getMe = async () => {
  const response = await axios.get('/auth/me')
  return response.data
}

export const listUser = async (query?: object) => {
  const response = await axios.get('/admin/user', { params: query })
  return response.data
}

export const createUser = async (data: object) => {
  const response = await axios.post(`/admin/user`, data)
  return response.data
}

export const editUser = async (userId: string | number, data: object) => {
  const response = await axios.put(`/admin/user/${userId}`, data)
  return response.data
}

export const deleteUser = async (userId: string | number) => {
  const response = await axios.delete(`/admin/user/${userId}`)
  return response.data
}

export const deleteAccountProfile = async () => {
  const response = await axios.delete(`/auth/me`)
  return response.data
}

export const editNameProfile = async (data: object) => {
  const response = await axios.put(`/auth/me`, data)
  return response.data
}

export const editPassProfile = async (data: object) => {
  const response = await axios.put(`/auth/change-password`, data)
  return response.data
}

export const resetPassword = async (email: string) => {
  const response = await axios.post(
    `/admin/user/send_reset_password?email=${email}`,
    email,
  )
  return response.data
}
