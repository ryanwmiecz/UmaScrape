/**
 * Main App component - refactored with component composition.
 * Uses custom hooks and modular components for better maintainability.
 */
import { useState } from 'react'
import { fetchScrapedData } from './services/api'
import { useApiCall } from './hooks/useApiCall'
import SearchBar from './components/SearchBar'
import ErrorDisplay from './components/ErrorDisplay'
import RaceList from './components/RaceList'
import EventList from './components/EventList'
import './App.css'

function App() {
  const [searchQuery, setSearchQuery] = useState('')
  const { data, loading, error, execute } = useApiCall()

  const handleSearch = async () => {
    try {
      await execute(fetchScrapedData, searchQuery)
    } catch (err) {
      // Error is already handled by useApiCall
      console.error('Search failed:', err)
    }
  }

  // Debug: log data when it changes
  if (data) {
    console.log('Received data:', data)
    console.log('Events:', data.events)
    console.log('Events type:', Array.isArray(data.events))
    console.log('Events length:', data.events?.length)
  }

  const handleInputChange = (e) => {
    setSearchQuery(e.target.value)
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>UmaScrape</h1>
        <p>Web scraper with real-time data visualization</p>
      </header>

      <main>
        <SearchBar
          onSearch={handleSearch}
          loading={loading}
          value={searchQuery}
          onChange={handleInputChange}
        />

        <ErrorDisplay error={error} />

        {data && (
          <div className="data-display">
            <RaceList races={data.matching_races} />
            <EventList events={data.events} title={data.title} />
          </div>
        )}
      </main>
    </div>
  )
}

export default App
