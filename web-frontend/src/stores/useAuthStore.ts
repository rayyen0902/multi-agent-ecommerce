import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  token: string | null
  username: string
  setToken: (token: string, username: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      username: '',
      setToken: (token, username) => set({ token, username }),
      logout: () => set({ token: null, username: '' }),
    }),
    {
      name: 'auth-storage',
      storage: {
        getItem: () => {
          const token = sessionStorage.getItem('auth-storage')
          return token ? JSON.parse(token) : null
        },
        setItem: (_, value) => {
          sessionStorage.setItem('auth-storage', JSON.stringify(value))
        },
        removeItem: (_, key) => {
          sessionStorage.removeItem(key)
        },
      },
    }
  )
)
