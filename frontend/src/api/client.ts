import axios, { type AxiosInstance } from 'axios'

const BASE_URL = '/v1'

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

const client: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status ?? 500
    const message =
      error.response?.data?.detail ??
      error.response?.data?.message ??
      error.message ??
      `HTTP ${status}`
    throw new ApiError(status, message)
  },
)

export const api = {
  get: <T>(path: string) => client.get<T>(path).then((res) => res.data),
  post: <T>(path: string, body: unknown) =>
    client.post<T>(path, body).then((res) => res.data),
}
