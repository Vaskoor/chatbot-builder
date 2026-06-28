// frontend/lib/stores/authStore.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: any | null;
  setTokens: (access: string, refresh: string) => void;
  setUser: (user: any) => void;
  logout: () => void;
}
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      setTokens: (access, refresh) => {
        set({ accessToken: access, refreshToken: refresh });
        localStorage.setItem('access_token', access);

        localStorage.setItem('refresh_token', refresh);
      },
      setUser: (user) => set({ user }),
      logout: () => {
        set({ accessToken: null, refreshToken: null, user: null });
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
export const getAuthToken = () => localStorage.getItem('access_token');
export const setAuthToken = (access: string, refresh: string) => {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
  useAuthStore.getState().setTokens(access, refresh);
};
export const clearAuthToken = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  useAuthStore.getState().logout();
};
