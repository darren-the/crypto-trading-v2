import { useCreateChart } from './hooks/chart'
import { useTimestampTrigger, useTimeframeTrigger, useVisibleLogicalRangeTrigger, useVisibleTimeRangeTrigger } from './hooks/triggers'
import { useUpdateSeries } from './hooks/series'
import { useContext } from 'react'
import { MainContext } from '../context'
import config from '../config.json'
import { useToggleHighsLows, useToggleResSup } from './hooks/toggles'


const Chart = () => {
  const {
    chartRef,
    setTimestamp,
    timeframe,
    setTimeframe,
    toggleHighLow,
    setToggleHighLow,
    toggleResSup,
    setToggleResSup,
} = useContext(MainContext)
  
  // Charting
  useCreateChart()
  useTimestampTrigger()
  useTimeframeTrigger()
  useVisibleLogicalRangeTrigger()
  useVisibleTimeRangeTrigger()
  useToggleHighsLows()
  useToggleResSup()
  useUpdateSeries()

  // Function for inputting a date
  const submitDate = (e) => {
    e.preventDefault()

    // Convert date string to timestamp
    const date = new Date(e.target.date.value)
    setTimestamp(date.getTime())

    e.target.reset()
  }

  // Buttons to change timeframe
  const timeframeButtons = config.timeframes.map(t =>
    <button key={t} onClick={() => setTimeframe(t)}>{t}</button>
  )

  // Toggle high low function
  const toggleHighLowClick = () => {
    if (toggleHighLow) setToggleHighLow(false)
    else setToggleHighLow(true)
  }

  // Toggle res sup function
  const toggleResSupClick = () => {
    if (toggleResSup) setToggleResSup(false)
    else setToggleResSup(true)
  }


  return (
    <div>
      <div style={{width: 1600, height: 700}}ref={chartRef} />
      <form onSubmit={submitDate}>
        <label>
          Date
          <input type="text" name="date"></input>
        </label>
      </form>
      {timeframeButtons}
      <div>current timeframe: {timeframe}</div>
      <button onClick={toggleHighLowClick}>Toggle highs and lows</button>
      <button onClick={toggleResSupClick}>Toggle resistances and supports</button>
    </div>
  )
}

export default Chart