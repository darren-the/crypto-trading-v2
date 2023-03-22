import { useCreateChart } from './hooks/createChart'
import { useCreateSeries } from './hooks/createSeries'
import { useTimestampTrigger, useTimeframeTrigger, useVisibleLogicalRangeTrigger, useVisibleTimeRangeTrigger } from './hooks/triggers'
import { useUpdateSeries } from './hooks/updateSeries'
import { useContext } from 'react'
import { MainContext } from '../context'
import config from '../config.json'
import { useToggleHighsLows, useToggleResSup } from './hooks/toggles'
import { useUpdateLiveSeries } from './hooks/updateLiveSeries'

const Chart = () => {
  const {
    series,
    mainChartRef,
    setTimestamp,
    timeframe,
    setTimeframe,
    toggleHighLow,
    setToggleHighLow,
    toggleResSup,
    setToggleResSup,
    rsiChartRef,
    retracementDisplay,
    liveRef,
    candles,
    liveCandles,
    unaggCandles,
    liveIndex,
  } = useContext(MainContext)

  /* ==================== CHARTING HOOKS ==================== */
  // Charts and series
  useCreateChart()
  useCreateSeries()
  const seriesUpdater = (liveRef.current) ? useUpdateLiveSeries : useUpdateSeries
  seriesUpdater()

  // triggers
  useTimestampTrigger()
  useTimeframeTrigger()
  useVisibleLogicalRangeTrigger()
  const VTRTrigger = (liveRef.current) ? () => {} : useVisibleTimeRangeTrigger
  VTRTrigger()

  // toggles
  useToggleHighsLows()
  useToggleResSup()

  /* ==================== CHARTING BUTTONS ==================== */
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

  // Live back
  const liveBackClick = () => {
    if (!liveRef.current) return
    liveIndex.current--
    if (candles[liveIndex.current].time < candles[liveIndex.current + 1].time) {
      liveCandles.current.pop()
    } else if (candles[liveIndex.current].time === candles[liveIndex.current + 1].time) {
      liveCandles.current[liveCandles.current.length - 1] = candles[liveIndex.current]
    }
    series.candleSeries.setData(liveCandles.current)
  }

  // Live forward
  const liveForwardClick = () => {
    if (!liveRef.current) return
    liveIndex.current++
    if (candles[liveIndex.current - 1].time < candles[liveIndex.current].time) {
      liveCandles.current.push(candles[liveIndex.current])
    } else if (candles[liveIndex.current - 1].time === candles[liveIndex.current].time) {
      liveCandles.current[liveCandles.current.length - 1] = candles[liveIndex.current]
    }
    series.candleSeries.setData(liveCandles.current)
  }

  return (
    <div>
      <div>
        <div style={{ width: '100%', height: 450 }} ref={mainChartRef} />
        <div style={{ width: '100%', height: 150 }} ref={rsiChartRef} />
      </div>
      
      <div style={{ display: 'flex', width: '100%' }}>

        <div style={{ width: '50%', height: 'auto' }}>
          <form onSubmit={submitDate}>
            <label>
              Date
              <input type="text" name="date"></input>
            </label>
          </form>
          {timeframeButtons}
          <div>current timeframe: {timeframe}</div>
          <div>
            <button onClick={toggleHighLowClick}>Toggle highs and lows</button>
            <button onClick={toggleResSupClick}>Toggle resistances and supports</button>
          </div>
          <div>
            <button onClick={liveBackClick}>Back</button>
            <button onClick={liveForwardClick}>Forward</button>

          </div>
        </div>

        <div style={{ width: '50%' }}>
          {retracementDisplay}
        </div>

      </div>
      
    </div>
  )
}

export default Chart