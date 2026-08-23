import axios from 'axios';
import { getAuthState, setAuthState, clearAuth } from '../store/authStore';

const baseURL = "http://localhost/api";
const apiClient = axios.create({ baseURL: baseURL, withCredentials: true });
const refreshClient = axios.create({baseURL: baseURL, withCredentials: true});

// Shared by the 401 interceptor below and by App's mount-time silent login —
// hits /refresh (relies on the httpOnly refresh-token cookie) and stores the
// new access token in the in-memory auth store. Throws on failure so callers
// can decide what "no valid session" means for them.
export async function refreshAccessToken() {
  const response = await refreshClient.post('refresh');
  const newAccessToken = response.data.access_token;
  setAuthState({ accessToken: newAccessToken });
  return newAccessToken;
}

apiClient.interceptors.request.use((config) => {
  const { accessToken } = getAuthState();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  response => response,

  async error => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const newAccessToken = await refreshAccessToken();

        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh token is expired/invalid — there's no valid session left,
        // so drop both the access token and the stored user, then send the
        // person back to login.
        clearAuth();

        if (typeof window !== 'undefined' && window.location.pathname !== '/auth') {
          window.location.href = '/auth';
        }

        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);
export default apiClient;
