import { useEffect, useRef, useState } from 'react'
import config from '../../config.json'
import { fetchCandles } from '../../services/candles'
import { fetchHighs } from '../../services/highs'
import { fetchLows } from '../../services/lows'
import { fetchResistance } from '../../services/resistance'
import { fetchSupport } from '../../services/support'

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
  toggleHighLow,
  toggleResSup,
) => {
  // state is used to trigger useEffects
  const [truncTime, setTruncTime] = useState(null)
  const [loadMode, setLoadMode] = useState(NONE)

  // data states
  const [candles, setCandles] = useState([])
  const [highs, setHighs] = useState([])
  const [lows, setLows] = useState([])
  const [resistance, setResistance] = useState([])
  const [support, setSupport] = useState([])

  // ref is decoupled from renders (for event handler)
  const loadMoreRef = useRef(false)  
  const initialRender = useRef(true)
  const candleStartTime = useRef(0)
  const lastIndex = useRef(null)
  const startOfData = useRef(false)
  const endOfData = useRef(false)
  const resPriceLines = useRef([])
  const supPriceLines = useRef([])
  const resSupVisible = useRef(true)
  const VTRChangeHandlerRef = useRef(null)
  const isLoading = useRef(false)
  
  /* =========== HANDLE VISIBLE LOGICAL RANGE CHANGE =========== */
  useEffect(() => {
    if (chart == null || series == null) return

    const VLRChangeHandler = (VLR) => {
      if (loadMoreRef.current || isLoading.current) return
      
      if (!startOfData.current && VLR.from < 0) {
        loadMoreRef.current = true
        console.log('need more previous data')
        isLoading.current = true
        setLoadMode(PREPEND)
      } else if (!endOfData.current && lastIndex.current != null && VLR.to > lastIndex.current) {
        loadMoreRef.current = true
        console.log('need next data')
        isLoading.current = true
        setLoadMode(APPEND)
      }
    }
    chart.timeScale().subscribeVisibleLogicalRangeChange(VLRChangeHandler)

  // eslint-disable-next-line
  }, [series])

  /* =========== HANDLE VISIBLE TIME RANGE CHANGE =========== */
  useEffect(() => {
    if (chart == null || series == null) return

    if (VTRChangeHandlerRef != null) chart.timeScale().unsubscribeVisibleTimeRangeChange(VTRChangeHandlerRef.current)

    VTRChangeHandlerRef.current = (VTR) => {
      const to_index = (VTR.to - candleStartTime.current) * 1000 / config.timeframe_to_ms[timeframe]
      if (resistance.length > 0 && !isLoading.current && resSupVisible.current) {
        if (resPriceLines.current.length > 0) resPriceLines.current.map(line => series.candleSeries.removePriceLine(line))
        resPriceLines.current = resistance[to_index].top_history.map(top_price =>
          series.candleSeries.createPriceLine({
            price: top_price,
            color: '#ef5350',
            lineWidth: 2,
            lineStyle: 0,
          })
        )
      }
      if (support.length > 0 && !isLoading.current && resSupVisible.current) {
        if (supPriceLines.current.length > 0) supPriceLines.current.map(line => series.candleSeries.removePriceLine(line))
        supPriceLines.current = support[to_index].bottom_history.map(bottom_price =>
          series.candleSeries.createPriceLine({
            price: bottom_price,
            color: '#26a69a',
            lineWidth: 2,
            lineStyle: 0,
          })
        )
      }
    }

    chart.timeScale().subscribeVisibleTimeRangeChange(VTRChangeHandlerRef.current)

  // eslint-disable-next-line
  }, [series, candles, resistance, support, timeframe])

  /* ================== DETECT NEW TIMESTAMP ================== */
  useEffect(() => {
    if (timestamp != null) {
      startOfData.current = false
      endOfData.current = false
      setTruncTime(timestamp)
      setLoadMode(TRUNCATE_ALL)
      Object.entries(series).forEach(([k,v]) => {
          v.applyOptions({
            visible: false
          })
      })
      isLoading.current = true
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
      Object.entries(series).forEach(([k,v]) => {
        v.applyOptions({
          visible: false
        })
      })
      isLoading.current = true
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

  /* ================== TOGGLE RES AND SUPPS ================== */
  useEffect(() => {
    if (series === null) return
    if (resSupVisible.current) resSupVisible.current = false
    else resSupVisible.current = true
    if (resPriceLines.current.length > 0) resPriceLines.current.map(line => series.candleSeries.removePriceLine(line))
    if (supPriceLines.current.length > 0) supPriceLines.current.map(line => series.candleSeries.removePriceLine(line))
    // eslint-disable-next-line
  }, [toggleResSup])

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

    const updateSeries = async () => {
      // update candles
      const candleData = await fetchCandles(timeframe, start, end)
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
      const newCandles = concatMethod(candleData, candles)
      setCandles(newCandles)

      candleStartTime.current = newCandles[0].time
      lastIndex.current = newCandles.length - 1

      // update highs
      const highData = await fetchHighs(timeframe, start, end)
      const candleHighs = candleData.filter(candle => highData.includes(candle.time_ms))
      const newHighs = concatMethod(candleHighs, highs)
      setHighs(newHighs)
      

      // fetch lows
      const lowData = await fetchLows(timeframe, start, end)
      const candleLows = candleData.filter(candle => lowData.includes(candle.time_ms))
      const newLows = concatMethod(candleLows, lows)
      setLows(newLows)

      // update charts
      series.candleSeries.setData(newCandles)
      series.highSeries.setData(newHighs)
      series.lowSeries.setData(newLows)
      
      // set visible range
      if (loadMode === TRUNCATE_ALL) {
        chart.timeScale().setVisibleRange({
          from: truncTime / 1000,
          to: (truncTime + config.timeframe_to_ms[timeframe] * config.candles.defaultVisibleWindow) / 1000
        })
      }

      // Show all data
      Object.entries(series).forEach(([k,v]) => {
        v.applyOptions({
          visible: true
        })
      })

      // update resistances
      const resData = await fetchResistance(timeframe, start, end)
      const newRes = concatMethod(resData, resistance)
      setResistance(newRes)

      // update supports
      const supData = await fetchSupport(timeframe, start, end)
      const newSup = concatMethod(supData, support)
      setSupport(newSup)
      
      isLoading.current = false
      loadMoreRef.current = false  // prevent spam loading new data
    }
      
    updateSeries()

  // eslint-disable-next-line
  }, [loadMode, candles, lows, highs])
}
