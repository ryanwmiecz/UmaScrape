import { useState, useEffect } from 'react'
import { fetchScrapedData } from './services/api'
import './App.css'

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')

  const handleScrape = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const result = await fetchScrapedData(searchQuery)
      console.log('Scraped data:', result) // Debug log
      setData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>UmaScrape</h1>
        <p>Web scraper with real-time data visualization</p>
      </header>

      <main>
        <div className="search-container">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Character name or paste game8 URL"
            className="search-input"
            disabled={loading}
          />
          <button 
            onClick={handleScrape} 
            disabled={loading}
            className="scrape-button"
          >
            {loading ? 'Scraping...' : 'Fetch Data'}
          </button>
        </div>

        {error && (
          <div className="error">
            <p>Error: {error}</p>
          </div>
        )}

        {data && (
          <div className="data-display">
            <h2 className="character-name">{data.title || data.character}</h2>
            
            {data.events && data.events.length > 0 ? (
              data.events.flat().map((event, index) => (
                <div key={index} className="event-section">
                  <h3 className="event-title">{event.event_name}</h3>
                  <table className="event-table">
                    <thead>
                      <tr>
                        <th>Event Conditions</th>
                        <th>Event Effects</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td className="conditions">
                          <div className="event-name-inline">{event.event_name}</div>
                          <div>{event.conditions}</div>
                        </td>
                        <td className="effects">{event.effects}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              ))
            ) : (
              <p>No events found</p>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
