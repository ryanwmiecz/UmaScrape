import { useState, useEffect } from 'react'
import { fetchScrapedData } from './services/api'
import './App.css'

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleScrape = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const result = await fetchScrapedData()
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
        <button 
          onClick={handleScrape} 
          disabled={loading}
          className="scrape-button"
        >
          {loading ? 'Scraping...' : 'Fetch Data'}
        </button>

        {error && (
          <div className="error">
            <p>Error: {error}</p>
          </div>
        )}

        {data && (
          <div className="data-display">
            <h2>Scraped Data</h2>
            <pre>{JSON.stringify(data, null, 2)}</pre>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
