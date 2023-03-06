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
  } = useContext(MainContext)

  useEffect(() => {
    if (initialRender.current) initialRender.current = false
    else if (chart == null || series == null || candles.length === 0) return
    else {
      startOfDataFlag.current = false
      endOfDataFlag.current = false
      setTruncTime(chart.timeScale().getVisibleRange().from * 1000)
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
    candleStartTime,
    resistance,
    support,
    isLoading,
    resSupVisible,
    resPriceLines,
    supPriceLines,
  } = useContext(MainContext)

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
}