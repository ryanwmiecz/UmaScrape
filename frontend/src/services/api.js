import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * Fetch scraped data from backend
 * @returns {Promise<Object>} Scraped data
 */
export const fetchScrapedData = async () => {
  try {
    const response = await api.get('/scrape')
    if (response.data.success) {
      return response.data.data
    } else {
      throw new Error(response.data.error || 'Failed to fetch data')
    }
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.error || 'Server error')
    } else if (error.request) {
      throw new Error('No response from server. Is the backend running?')
    } else {
      throw new Error(error.message)
    }
  }
}

/**
 * Health check endpoint
 * @returns {Promise<Object>} Health status
 */
export const checkHealth = async () => {
  try {
    const response = await api.get('/health')
    return response.data
  } catch (error) {
    throw new Error('Backend is not responding')
  }
}

export default api
