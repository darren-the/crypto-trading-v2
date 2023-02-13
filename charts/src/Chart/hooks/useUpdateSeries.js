import { useEffect, useRef, useState } from 'react'
import config from '../../config.json'
import { fetchCandles } from '../../services/candles'
import { fetchHighs } from '../../services/highs'
import { fetchLows } from '../../services/lows'

// define constants
const NONE = 0
const TRUNCATE_ALL = 1
const APPEND = 2
const PREPEND = 3

export const useUpdateSeries = (
  chart,
  series,
  timeframe,
  timestamp,
  toggleHighLow
) => {
  // state is used to trigger useEffects
  const [truncTime, setTruncTime] = useState(null)
  const [loadMode, setLoadMode] = useState(NONE)

  // data states
  const [candles, setCandles] = useState([])
  const [highs, setHighs] = useState([])
  const [lows, setLows] = useState([])

  // ref is decoupled from renders (for event handler)
  const loadMoreRef = useRef(false)  
  const initialRender = useRef(true)
  const lastIndex = useRef(null)
  const startOfData = useRef(false)
  const endOfData = useRef(false)
  
  /* =========== HANDLE VISIBLE LOGICAL RANGE CHANGE =========== */
  useEffect(() => {
    if (chart == null || series == null) return

    const VLRChangeHandler = (VLR) => {
      if (loadMoreRef.current) return
      
      if (!startOfData.current && VLR.from < 0) {
        loadMoreRef.current = true
        console.log('need more previous data')
        setLoadMode(PREPEND)
      } else if (!endOfData.current && lastIndex.current != null && VLR.to > lastIndex.current) {
        loadMoreRef.current = true
        console.log('need next data')
        setLoadMode(APPEND)
      }
    }
    chart.timeScale().subscribeVisibleLogicalRangeChange(VLRChangeHandler)

  // eslint-disable-next-line
  }, [series])

  /* ================== DETECT NEW TIMESTAMP ================== */
  useEffect(() => {
    if (timestamp != null) {
      startOfData.current = false
      endOfData.current = false
      setTruncTime(timestamp)
      setLoadMode(TRUNCATE_ALL)
      console.log('new timestamp detected')
    }
  // eslint-disable-next-line
  }, [timestamp])

  /* ================== DETECT NEW TIMEFRAME ================== */
  useEffect(() => {
    if (initialRender.current) initialRender.current = false
    else if (chart == null || series == null || candles.length === 0) return
    else {
      startOfData.current = false
      endOfData.current = false
      setTruncTime(chart.timeScale().getVisibleRange().from * 1000)
      setLoadMode(TRUNCATE_ALL)
      console.log('new timeframe detected')
    }
    // eslint-disable-next-line
  }, [timeframe])

  /* ================== TOGGLE HIGHS AND LOWS ================== */
  useEffect(() => {
    if (series === null) return
    series.highSeries.applyOptions({visible: toggleHighLow})
    series.lowSeries.applyOptions({visible: toggleHighLow})
    // eslint-disable-next-line
  }, [toggleHighLow])

  /* ===================== UPDATE SERIES ===================== */
  useEffect(() => {
    if (loadMode === NONE || series == null) return
    setLoadMode(NONE)  // set here to immediately prevent consecutive calls

    var start = null
    var end = null
    var concatMethod = (data) => data

    // configure start/end window to fetch data. Also configure concatenation method.
    if (loadMode === PREPEND) {
      end = candles[0].time_ms
      start = end - (config.timeframe_to_ms[timeframe] * config.candles.fetchWindow)
      concatMethod = (newData, oldData) => newData.concat(oldData)

    } else if (loadMode === APPEND) {
      start = candles.at(-1).time_ms + config.timeframe_to_ms[timeframe]
      end = start + (config.timeframe_to_ms[timeframe] * config.candles.fetchWindow)
      concatMethod = (newData, oldData) => oldData.concat(newData)

    } else if (loadMode === TRUNCATE_ALL) {
      start = truncTime - (config.timeframe_to_ms[timeframe] * config.candles.fetchWindow / 2)
      end = truncTime + (config.timeframe_to_ms[timeframe] * config.candles.fetchWindow / 2)
      concatMethod = (newData, oldData) => newData
    }

    // fetch candles
    fetchCandles(timeframe, start, end).then(candleData => {
      if (candleData.length === 0) {
        if (loadMode === PREPEND) {
          console.log('start of data')
          startOfData.current = true
        }
        if (loadMode === APPEND) {
          console.log('end of data')
          endOfData.current = true
        }
        if (loadMode === TRUNCATE_ALL) console.log('Invalid range: No data in database for this range')
      }

      // update candlestick series
      const newCandles = concatMethod(candleData, candles)
      series.candleSeries.setData(newCandles)
      setCandles(newCandles)
      lastIndex.current = newCandles.length - 1

      // set visible range
      if (loadMode === TRUNCATE_ALL) {
        chart.timeScale().setVisibleRange({
          from: truncTime / 1000,
          to: (truncTime + config.timeframe_to_ms[timeframe] * config.candles.defaultVisibleWindow) / 1000
        })
      }
      
      // candlestick dependent series updates

      // fetch highs
      fetchHighs(timeframe, start, end).then(highData => {
        // filter candles to highs
        const candleHighs = candleData.filter(candle => highData.includes(candle.time_ms))

        // update highs series
        const newHighs = concatMethod(candleHighs, highs)
        series.highSeries.setData(newHighs)
        setHighs(newHighs)
      })

      // fetch lows
      fetchLows(timeframe, start, end).then(lowData => {
        // filter candles to lows
        const candleLows = candleData.filter(candle => lowData.includes(candle.time_ms))

        // update lows series
        const newLows = concatMethod(candleLows, lows)
        series.lowSeries.setData(newLows)
        setLows(newLows)
      })

      // reset states
      loadMoreRef.current = false
    })
    
  // eslint-disable-next-line
  }, [loadMode, candles])
}
