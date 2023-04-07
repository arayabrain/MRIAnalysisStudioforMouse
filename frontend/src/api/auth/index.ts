import axios from 'components/utils/axios'

export const login = async (data: { email: string; password: string }) => {
  const response = await axios.post('/auth/login', data)
  return response.data
}

export const getMe = async () => {
  const response = await axios.get('/auth/me')
  return response.data
}

export const listUser = async (query?: any) => {
  const response = await axios.get('/admin/user', { params: query })
  return response.data
}

export const editUser = async (userId: string | number, data: any) => {
  const response = await axios.put(`/admin/user/${userId}`, data)
  return response.data
}
