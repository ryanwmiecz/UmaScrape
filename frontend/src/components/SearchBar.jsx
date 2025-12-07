/**
 * SearchBar component for character search input.
 * Handles search input and submission.
 */
import PropTypes from 'prop-types'
import '../App.css'

export const SearchBar = ({ onSearch, loading, value, onChange }) => {
  const handleSubmit = (e) => {
    e.preventDefault()
    onSearch()
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      onSearch()
    }
  }

  return (
    <div className="search-container">
      <input
        type="text"
        value={value}
        onChange={onChange}
        onKeyPress={handleKeyPress}
        placeholder="Search for a character (e.g., Agnes Tachyon)"
        className="search-input"
        disabled={loading}
        aria-label="Character search"
      />
      <button 
        onClick={onSearch} 
        disabled={loading}
        className="scrape-button"
        aria-label={loading ? 'Fetching data...' : 'Fetch character data'}
      >
        {loading ? 'Scraping...' : 'Fetch Data'}
      </button>
    </div>
  )
}

SearchBar.propTypes = {
  onSearch: PropTypes.func.isRequired,
  loading: PropTypes.bool,
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired
}

SearchBar.defaultProps = {
  loading: false,
  value: ''
}

export default SearchBar
