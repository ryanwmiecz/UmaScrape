/**
 * StatsDisplay component for showing recommended character stats.
 */
import PropTypes from 'prop-types'
import './StatsDisplay.css'

const StatsDisplay = ({ stats }) => {
  if (!stats) {
    return null
  }

  const statItems = [
    { name: 'Speed', value: stats.speed, color: '#60a5fa' },
    { name: 'Stamina', value: stats.stamina, color: '#34d399' },
    { name: 'Power', value: stats.power, color: '#f87171' },
    { name: 'Guts', value: stats.guts, color: '#fbbf24' },
    { name: 'Wit', value: stats.wit, color: '#a78bfa' }
  ]

  return (
    <div className="stats-display">
      <h3 className="stats-title">Recommended Stats</h3>
      <div className="stats-grid">
        {statItems.map(stat => (
          <div key={stat.name} className="stat-item">
            <div className="stat-name">{stat.name}</div>
            <div 
              className="stat-value" 
              style={{ color: stat.color }}
            >
              {stat.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

StatsDisplay.propTypes = {
  stats: PropTypes.shape({
    speed: PropTypes.number,
    stamina: PropTypes.number,
    power: PropTypes.number,
    guts: PropTypes.number,
    wit: PropTypes.number
  })
}

StatsDisplay.defaultProps = {
  stats: null
}

export default StatsDisplay
