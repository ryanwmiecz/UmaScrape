/**
 * RaceList component for displaying race matches.
 * Shows races mentioned in character events in a grid layout.
 */
import PropTypes from 'prop-types'
import '../App.css'

export const RaceList = ({ races }) => {
  if (!races || races.length === 0) return null

  return (
    <div className="races-section">
      <h3 className="races-title">
        🏁 Races Mentioned in Events ({races.length})
      </h3>
      <div className="races-grid">
        {races.map((match, index) => (
          <div key={index} className="race-card">
            <div className="race-tier">{match.tier}</div>
            <div className="race-name">{match.race}</div>
            <div className="race-details">
              <span className="race-period">{match.period}</span>
              <span className="race-distance">{match.distance}</span>
            </div>
            <div className="race-event">Event: {match.event_name}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

RaceList.propTypes = {
  races: PropTypes.arrayOf(
    PropTypes.shape({
      race: PropTypes.string.isRequired,
      period: PropTypes.string.isRequired,
      tier: PropTypes.string.isRequired,
      distance: PropTypes.string.isRequired,
      event_name: PropTypes.string.isRequired,
      mentioned_in: PropTypes.string
    })
  )
}

RaceList.defaultProps = {
  races: []
}

export default RaceList
