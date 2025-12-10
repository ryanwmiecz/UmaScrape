/**
 * RankDisplay component for showing character overall tier rank.
 * Displays prominently with color coding based on rank.
 */
import PropTypes from 'prop-types'
import './RankDisplay.css'

const RankDisplay = ({ rank, characterName }) => {
  if (!rank) {
    return null
  }

  // Determine rank class for styling
  const getRankClass = (rank) => {
    const rankUpper = rank.toUpperCase()
    if (rankUpper === 'SS') return 'rank-ss'
    if (rankUpper === 'S') return 'rank-s'
    if (rankUpper === 'A') return 'rank-a'
    if (rankUpper === 'B') return 'rank-b'
    return 'rank-default'
  }

  const rankClass = getRankClass(rank)

  return (
    <div className="rank-display-container">
      <div className={`rank-badge ${rankClass}`}>
        <div className="rank-label">Overall Tier</div>
        <div className="rank-value">{rank.toUpperCase()}</div>
        <div className="rank-sublabel">Rank</div>
      </div>
      {characterName && (
        <div className="rank-description">
          <p>{characterName} is ranked <strong>{rank.toUpperCase()}</strong> tier in the current meta</p>
        </div>
      )}
    </div>
  )
}

RankDisplay.propTypes = {
  rank: PropTypes.string,
  characterName: PropTypes.string
}

RankDisplay.defaultProps = {
  rank: null,
  characterName: null
}

export default RankDisplay
