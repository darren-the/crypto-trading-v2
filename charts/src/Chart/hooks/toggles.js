import { useContext, useEffect } from 'react'
import { MainContext } from '../../context'

export const useToggleHighsLows = () => {
  const {
    series,
    toggleHighLow,
    highLowVisible,
  } = useContext(MainContext)

  useEffect(() => {
    if (series === null) return
    if (highLowVisible.current) highLowVisible.current = false
    else highLowVisible.current = true
    series.highSeries.applyOptions({visible: toggleHighLow})
    series.lowSeries.applyOptions({visible: toggleHighLow})
    // eslint-disable-next-line
  }, [toggleHighLow])
}

export const useToggleResSup = () => {
  const {
    series,
    resSupVisible,
    resPriceLines,
    supPriceLines,
    toggleResSup,
  } = useContext(MainContext)

  useEffect(() => {
    if (series === null) return
    if (resSupVisible.current) resSupVisible.current = false
    else resSupVisible.current = true
    if (resPriceLines.current.length > 0) resPriceLines.current.map(line => series.candleSeries.removePriceLine(line))
    if (supPriceLines.current.length > 0) supPriceLines.current.map(line => series.candleSeries.removePriceLine(line))
    // eslint-disable-next-line
  }, [toggleResSup])
}