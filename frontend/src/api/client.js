import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

const client = axios.create({ baseURL: API_BASE })

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export const authApi = {
  login: (email, password) => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    return client.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  register: (payload) => client.post('/auth/register', payload),
}

export const grievanceApi = {
  submit: (raw_text) => client.post('/grievances', { raw_text }),
  myGrievances: () => client.get('/grievances/me'),
  departmentQueue: () => client.get('/grievances/department'),
  getOne: (id) => client.get(`/grievances/${id}`),
  getHistory: (id) => client.get(`/grievances/${id}/history`),
  updateStatus: (id, status, note) => client.patch(`/grievances/${id}/status`, { status, note }),
  submitFeedback: (id, rating, comment) => client.post(`/grievances/${id}/feedback`, { rating, comment }),
}

export const departmentApi = {
  list: () => client.get('/departments'),
}

export const analyticsApi = {
  summary: () => client.get('/analytics/summary'),
  runEscalationCheck: () => client.post('/analytics/run-escalation-check'),
}

export default client
