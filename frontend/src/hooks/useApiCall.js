/**
 * Custom React hook for managing API calls with loading and error states.
 * Eliminates boilerplate state management in components.
 */
import { useState, useCallback } from 'react'

/**
 * Hook for managing async API calls with automatic state management
 * @returns {Object} State and execution function
 * @returns {*} data - Response data (null initially)
 * @returns {boolean} loading - Loading state
 * @returns {string|null} error - Error message (null if no error)
 * @returns {Function} execute - Function to execute the API call
 * @returns {Function} reset - Function to reset state
 */
export const useApiCall = () => {
  const [state, setState] = useState({
    data: null,
    loading: false,
    error: null
  })

  /**
   * Execute an async function and manage state automatically
   * @param {Function} apiFunction - Async function to execute
   * @param {...*} args - Arguments to pass to the function
   * @returns {Promise<*>} Result from the API call
   */
  const execute = useCallback(async (apiFunction, ...args) => {
    setState(prev => ({ ...prev, loading: true, error: null }))
    
    try {
      const result = await apiFunction(...args)
      setState({ data: result, loading: false, error: null })
      return result
    } catch (err) {
      const errorMessage = err.message || 'An unexpected error occurred'
      setState({ data: null, loading: false, error: errorMessage })
      throw err
    }
  }, [])

  /**
   * Reset state to initial values
   */
  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null })
  }, [])

  return {
    ...state,
    execute,
    reset
  }
}

/**
 * Hook for managing form input with validation
 * @param {string} initialValue - Initial input value
 * @param {Function} validator - Optional validation function
 * @returns {Object} Input state and handlers
 */
export const useInput = (initialValue = '', validator = null) => {
  const [value, setValue] = useState(initialValue)
  const [error, setError] = useState(null)

  const handleChange = useCallback((e) => {
    const newValue = e.target.value
    setValue(newValue)
    
    if (validator) {
      const validationError = validator(newValue)
      setError(validationError)
    }
  }, [validator])

  const reset = useCallback(() => {
    setValue(initialValue)
    setError(null)
  }, [initialValue])

  return {
    value,
    error,
    onChange: handleChange,
    reset,
    setValue
  }
}

export default useApiCall
