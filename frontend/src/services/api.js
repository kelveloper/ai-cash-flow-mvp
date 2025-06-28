import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 60000, // Increased to 60 seconds for complex queries
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for debugging and performance tracking
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    config.startTime = Date.now()
    return config
  },
  (error) => {
    console.error('❌ API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling and performance tracking
api.interceptors.response.use(
  (response) => {
    const duration = Date.now() - response.config.startTime
    console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${response.config.url} (${duration}ms)`)
    return response
  },
  (error) => {
    const duration = error.config?.startTime ? Date.now() - error.config.startTime : 0
    console.error('❌ API Response Error:', {
      url: error.config?.url,
      status: error.response?.status,
      message: error.response?.data?.detail || error.message,
      duration: `${duration}ms`
    })
    
    // Provide helpful error messages for timeouts
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      console.warn('⚠️ Request timed out - consider using pagination or filters to reduce data size')
    }
    
    return Promise.reject(error)
  }
)

export default api 