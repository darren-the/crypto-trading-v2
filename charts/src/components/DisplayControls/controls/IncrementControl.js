import { Context } from '../../../context'
import { useContext, useState } from 'react'
import {
  incrementDisplay,
  decrementDisplay,
  changeIncrement
} from '../../../utils/redux-dispatchers/dispatchers'
import config from '../../../config.json'

const IncrementControl = () => {
  const { series, setDfComponent } = useContext(Context)
  const [currentIncrement, setCurrentIncrement] = useState(config.baseMs)
  const incrementOptions = config.timeframes.map(timeframe =>
    <option key={timeframe} value={timeframe}>{timeframe}</option>
  )
  const changeIncrementOnChange = (e) => {
    const newIncrementMs = config.timeframeToMs[e.target.value]
    changeIncrement({
      series,
      setDfComponent,
      increment: newIncrementMs,
    })
    setCurrentIncrement(newIncrementMs)
  }

  return (
    <div>
      Current increment:
      <select onChange={changeIncrementOnChange} defaultValue={currentIncrement}>
        {incrementOptions}
      </select>
      <button onClick={() => decrementDisplay({ series, setDfComponent })}>Decrement</button>
      <button onClick={() => incrementDisplay({ series, setDfComponent })}>Increment</button>
    </div>
  )
}

export default IncrementControl