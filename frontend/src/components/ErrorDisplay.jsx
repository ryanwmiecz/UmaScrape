/**
 * ErrorDisplay component for showing error messages.
 * Displays errors in a consistent, user-friendly format.
 */
import PropTypes from 'prop-types'
import '../App.css'

export const ErrorDisplay = ({ error }) => {
  if (!error) return null

  return (
    <div className="error" role="alert">
      <p><strong>Error:</strong> {error}</p>
    </div>
  )
}

ErrorDisplay.propTypes = {
  error: PropTypes.string
}

ErrorDisplay.defaultProps = {
  error: null
}

export default ErrorDisplay
