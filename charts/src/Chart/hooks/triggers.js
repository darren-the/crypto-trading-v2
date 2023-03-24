import { useEffect } from 'react'
import { useContext } from 'react'
import { MainContext } from '../../context'
import config from '../../config.json'


export const useTimestampTrigger = () => {
  const {
    timestamp,
    startOfDataFlag,
    endOfDataFlag,
    setTruncTime,
    setLoadMode,
    series,
    isLoading,
  } = useContext(MainContext)
  // THIS COULD BE REFACTORED, no need to be a useeffect
  
  useEffect(() => {
    if (timestamp != null) {
      startOfDataFlag.current = false
      endOfDataFlag.current = false
      setTruncTime(timestamp)
      setLoadMode(config.loadMode.TRUNCATE_ALL)
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
}

export const useTimeframeTrigger = () => {
  const {
    timeframe,
    initialRender,
    chart,
    series,
    candles,
    startOfDataFlag,
    endOfDataFlag,
    setTruncTime,
    setLoadMode,
    isLoading,
    liveCandles,
    features,
  } = useContext(MainContext)
  // THIS COULD BE REFACTORED, no need to be a useeffect
  useEffect(() => {
    if (initialRender.current) initialRender.current = false
    else if (chart == null || series == null || features.Candles.state.length === 0) return
    else {
      startOfDataFlag.current = false
      endOfDataFlag.current = false
      // get truncate time
      const truncTime = liveCandles.current[liveCandles.current.length - 1].base_time * 1000 + config.base_ms
      setTruncTime(truncTime)
      setLoadMode(config.loadMode.TRUNCATE_ALL)
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
}

export const useVisibleLogicalRangeTrigger = () => {
  const {
    chart,
    series,
    isLoading,
    startOfDataFlag,
    setLoadMode,
    endOfDataFlag,
    lastIndex,
  } = useContext(MainContext)

  useEffect(() => {
    if (chart == null || series == null) return

    const VLRChangeHandler = (VLR) => {
      if (isLoading.current) return
      
      if (!startOfDataFlag.current && VLR.from < 0) {
        isLoading.current = true
        console.log('need more previous data')
        isLoading.current = true
        setLoadMode(config.loadMode.PREPEND)
      } else if (!endOfDataFlag.current && lastIndex.current != null && VLR.to > lastIndex.current) {
        isLoading.current = true
        console.log('need next data')
        isLoading.current = true
        setLoadMode(config.loadMode.APPEND)
      }
    }
    chart.timeScale().subscribeVisibleLogicalRangeChange(VLRChangeHandler)

  // eslint-disable-next-line
  }, [series])
}

export const useVisibleTimeRangeTrigger = () => {
  const {
    chart,
    series,
    candles,
    timeframe,
    VTRChangeHandlerRef,
    mainChartRef,
    candleStartTime,
    resistance,
    support,
    isLoading,
    resSupVisible,
    resPriceLines,
    supPriceLines,
    retracement,
    setRetracementDisplay,
    highs,
    lows,
    highLowVisible,
  } = useContext(MainContext)

  useEffect(() => {
    if (chart == null || series == null) return

    if (VTRChangeHandlerRef != null) chart.timeScale().unsubscribeVisibleTimeRangeChange(VTRChangeHandlerRef.current)

    VTRChangeHandlerRef.current = (VTR) => {
      // Set live marker position
      var liveMarkerIndex = 0
      if (candles.length > 0 && !isLoading.current) {
        const liveMarkerCoordinate = mainChartRef.current.clientWidth * config.candles.live_marker_offset_percentage
        const liveMarkerTime = chart.timeScale().coordinateToTime(liveMarkerCoordinate)
        const liveMarkerTimeConstrained = 
          (liveMarkerTime < candles[0].time) ? candles[0].time :
          (liveMarkerTime > candles[candles.length - 1].time) ? candles[candles.length - 1].time :
          liveMarkerTime
        liveMarkerIndex = (liveMarkerTimeConstrained - candleStartTime.current) * 1000 / config.timeframe_to_ms[timeframe]
        series.candleSeries.setMarkers([
          {
              time: liveMarkerTimeConstrained,
              position: 'aboveBar',
              color: '#000000',
              shape: 'arrowDown',
              text: 'Live',
          },
        ])
      }

      // update highs
      if (highs.length > 0 && !isLoading.current && highLowVisible.current) {
        const candleHighs = candles.filter(candle => highs[liveMarkerIndex].high_history.includes(candle.time_ms))
        series.highSeries.setData(candleHighs)

      }

      // update lows
      if (lows.length > 0 & !isLoading.current && highLowVisible.current) {
        const candleLows = candles.filter(candle => lows[liveMarkerIndex].low_history.includes(candle.time_ms))
        series.lowSeries.setData(candleLows)
      }

      // update resistance
      if (resistance.length > 0 && !isLoading.current && resSupVisible.current) {
        if (resPriceLines.current.length > 0) resPriceLines.current.map(line => series.candleSeries.removePriceLine(line))
        resPriceLines.current = resistance[liveMarkerIndex].top_history.map(top_price =>
          series.candleSeries.createPriceLine({
            price: top_price,
            color: '#ef5350',
            lineWidth: 2,
            lineStyle: 0,
          })
        )
      }

      // update support
      if (support.length > 0 && !isLoading.current && resSupVisible.current) {
        if (supPriceLines.current.length > 0) supPriceLines.current.map(line => series.candleSeries.removePriceLine(line))
        supPriceLines.current = support[liveMarkerIndex].bottom_history.map(bottom_price =>
          series.candleSeries.createPriceLine({
            price: bottom_price,
            color: '#26a69a',
            lineWidth: 2,
            lineStyle: 0,
          })
        )
      }

      // update retracement
      if (retracement.length > 0 && !isLoading.current) {
        const current_retracement = retracement[liveMarkerIndex]
        setRetracementDisplay(
          `High retracement = ${Math.round(current_retracement.high_retracement * 100)}%, ` +
          `Low retracement = ${Math.round(current_retracement.low_retracement * 100)}%`
          )
      }
    }

    chart.timeScale().subscribeVisibleTimeRangeChange(VTRChangeHandlerRef.current)

  // eslint-disable-next-line
  }, [series, candles, resistance, support, retracement, timeframe, highs, lows])
}