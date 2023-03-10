import { useEffect } from 'react'
import config from '../../config.json'
import { fetchCandles, fetchHighs, fetchLows, fetchResistance, fetchRsi, fetchSupport } from '../../services/fetch_data'
import { useContext } from 'react'
import { MainContext } from '../../context'


export const useUpdateSeries = () => {
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
      start = end - (config.timeframe_to_ms[timeframe] * config.candles.fetchWindow)
      concatMethod = (newData, oldData) => newData.concat(oldData)

    } else if (loadMode === config.loadMode.APPEND) {
      start = candles.at(-1).time_ms + config.timeframe_to_ms[timeframe]
      end = start + (config.timeframe_to_ms[timeframe] * config.candles.fetchWindow)
      concatMethod = (newData, oldData) => oldData.concat(newData)

    } else if (loadMode === config.loadMode.TRUNCATE_ALL) {
      start = truncTime - (config.timeframe_to_ms[timeframe] * config.candles.fetchWindow / 2)
      end = truncTime + (config.timeframe_to_ms[timeframe] * config.candles.fetchWindow / 2)
      concatMethod = (newData, oldData) => newData
    }

    const updateSeries = async () => {
      const candleData = await fetchCandles(timeframe, start, end)

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
      candleStartTime.current = newCandles[0].time
      lastIndex.current = newCandles.length - 1
      setCandles(newCandles)
      series.candleSeries.setData(newCandles)

      // update rsi
      const rsiData = await fetchRsi(timeframe, start, end)
      const newRsi = concatMethod(rsiData, rsi)
      setRsi(newRsi)
      series.rsiSeries.setData(newRsi)

      // update highs
      const highData = await fetchHighs(timeframe, start, end)
      const candleHighs = candleData.filter(candle => highData.includes(candle.time_ms))
      const newHighs = concatMethod(candleHighs, highs)
      setHighs(newHighs)
      series.highSeries.setData(newHighs)

      // fetch lows
      const lowData = await fetchLows(timeframe, start, end)
      const candleLows = candleData.filter(candle => lowData.includes(candle.time_ms))
      const newLows = concatMethod(candleLows, lows)
      setLows(newLows)
      series.lowSeries.setData(newLows)

      // set visible range
      if (loadMode === config.loadMode.TRUNCATE_ALL) {
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
    }

    updateSeries()

  // eslint-disable-next-line
  }, [loadMode, candles, rsi])
}
