import TimeframeControl from './controls/TimeframeControl'
import DateControl from './controls/DateControl'
import IncrementControl from './controls/IncrementControl'

const DisplayControls = () => {
  return (
    <div style={{ width: '50%', height: 'auto' }}>
      <DateControl />
      <TimeframeControl />
      <IncrementControl />
    </div>
  )
}

export default DisplayControls
