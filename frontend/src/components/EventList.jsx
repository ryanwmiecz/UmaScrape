/**
 * EventList component for displaying character events.
 * Shows event conditions and effects in table format.
 */
import PropTypes from 'prop-types'
import '../App.css'

const EventList = ({ events, title }) => {
  if (!events || events.length === 0) {
    return <p>No events found</p>
  }

  // Flatten nested event arrays
  const flatEvents = events.flat()

  return (
    <>
      {title && <h2 className="character-name">{title}</h2>}
      
      {flatEvents.map((event, index) => (
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
      ))}
    </>
  )
}

EventList.propTypes = {
  events: PropTypes.arrayOf(
    PropTypes.oneOfType([
      PropTypes.shape({
        event_name: PropTypes.string.isRequired,
        conditions: PropTypes.string.isRequired,
        effects: PropTypes.string.isRequired
      }),
      PropTypes.array
    ])
  ),
  title: PropTypes.string
}

EventList.defaultProps = {
  events: [],
  title: null
}

export default EventList
