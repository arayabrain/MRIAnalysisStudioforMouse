export const saveToken = (access_token: string) => {
  localStorage.setItem('access_token', access_token)
}
export const getToken = () => {
  return localStorage.getItem('access_token')
}
export const saveRefreshToken = (refresh_token: string) => {
  localStorage.setItem('refresh_token', refresh_token)
}
export const getRefreshToken = () => {
  return localStorage.getItem('refresh_token')
}
export const removeToken = () => {
  return localStorage.removeItem('access_token')
}
export const saveExToken = (ExToken: string) => {
  localStorage.setItem('ExToken', ExToken)
}
export const getExToken = () => {
  return localStorage.getItem('ExToken')
}
export const removeExToken = () => {
  return localStorage.removeItem('ExToken')
}

export const isAdmin = (role?: number | string) => {
  return role === 1
}

export const isReseacher = (role?: string | number) => {
  return role === 20
}

export const optionsRole = [
  {
    code: 1,
    name: 'Admin',
  },
  {
    code: 10,
    name: 'Data Manager',
  },
  {
    code: 20,
    name: 'User',
  },
]
