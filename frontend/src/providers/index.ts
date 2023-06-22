import { createContext, useContext } from 'react'

export type User = {
  created_time: null | string
  display_name: null | string
  email: string
  last_login_time: null | string
  role: string
  uid: string
}

export const UserContext = createContext<{ user?: User; setUser: Function }>({
  setUser: () => null,
})

export const useUser = () => useContext(UserContext)
