import { useEffect } from 'react'
import config from '../../config.json'
import { fetchCandles, fetchHighs, fetchLows, fetchResistance, fetchRetracement, fetchRsi, fetchSupport } from '../../services/fetch_data'
import { useContext } from 'react'
import { MainContext } from '../../context'


export const useUpdateLiveSeries = () => {
  const {
    chart,
    series,
    timeframe,
    truncTime,
    loadMode,
    setLoadMode,
    candleStartTime,
    lastIndex,
    startOfDataFlag,
    endOfDataFlag,
    isLoading,
    candles,
    setCandles,
    highs,
    setHighs,
    lows,
    setLows,
    resistance,
    setResistance,
    support,
    setSupport,
    rsi,
    setRsi,
    pipelineId,
    symbol,
    retracement,
    setRetracement,
    liveIndex,
    liveCandles,
  } = useContext(MainContext)

  useEffect(() => {
    if (loadMode === config.loadMode.NONE || series == null) return
    setLoadMode(config.loadMode.NONE)  // set here to immediately prevent consecutive calls

    var start = null
    var end = null
    var concatMethod = (data) => data

    // configure start/end window to fetch data. Also configure concatenation method.
    if (loadMode === config.loadMode.PREPEND) {
      end = candles[0].time_ms
      start = end - (config.timeframe_to_ms[timeframe] * config.candles.liveFetchWindow)
      concatMethod = (newData, oldData) => newData.concat(oldData)

    } else if (loadMode === config.loadMode.APPEND) {
      // APPEND is disabled for live chart
      console.log('APPEND is disabled for live chart')
      endOfDataFlag.current = true
      isLoading.current = false
      return
    } else if (loadMode === config.loadMode.TRUNCATE_ALL) {
      start = truncTime - (config.timeframe_to_ms[timeframe] * config.candles.liveFetchWindow / 2)
      end = truncTime + (config.timeframe_to_ms[timeframe] * config.candles.liveFetchWindow / 2)
      concatMethod = (newData, oldData) => newData
    }

    const updateSeries = async () => {
      const candleData = await fetchCandles(symbol, timeframe, pipelineId, start, end)

      // Check whether there is anymore data to be fetched
      if (candleData.length === 0) {
        if (loadMode === config.loadMode.PREPEND) {
          console.log('start of data')
          startOfDataFlag.current = true
        }
        if (loadMode === config.loadMode.APPEND) {
          console.log('end of data')
          endOfDataFlag.current = true
        }
        if (loadMode === config.loadMode.TRUNCATE_ALL) console.log('Invalid range: No data in database for this range')
      }

      // update candles
      const newCandles = concatMethod(candleData, candles)
      // candleStartTime.current = newCandles[0].time
      // lastIndex.current = newCandles.length - 1
      setCandles(newCandles)
      if (loadMode === config.loadMode.TRUNCATE_ALL) {
        // Set live index
        liveIndex.current = newCandles.findIndex(candle => candle.base_time === truncTime / 1000) - 1
      }
      const histCandles = newCandles.slice(0, liveIndex.current + 1)
      liveCandles.current = histCandles.filter(candle => candle.is_complete)  // aggregate history
      // append last candle if incomplete
      const lastCandle = histCandles[histCandles.length - 1]
      if (!lastCandle.is_complete) liveCandles.current.push(lastCandle)
      series.candleSeries.setData(liveCandles.current)

      // set visible range
      if (loadMode === config.loadMode.TRUNCATE_ALL) {
        chart.timeScale().setVisibleRange({
          from: (truncTime - config.timeframe_to_ms[timeframe] * config.candles.defaultVisibleWindow) / 1000,
          to: truncTime
        })
      }

      // Show all data
      Object.entries(series).forEach(([k,v]) => {
        v.applyOptions({
          visible: true
        })
      })
      
      isLoading.current = false
    }

    updateSeries()

  // eslint-disable-next-line
  }, [loadMode, candles, rsi])
}
