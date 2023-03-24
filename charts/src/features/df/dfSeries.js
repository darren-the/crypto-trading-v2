import { createCandlesSeries, updateCandlesSeries } from './candles/candlesSeries'
import { createRsiSeries, updateRsiSeries } from './rsi/rsiSeries'
import { createHighsSeries, updateHighsSeries } from './highs/highsSeries'
import { createLowsSeries, updateLowsSeries } from './lows/lowsSeries'
import { createResistanceSeries, updateResistanceSeries } from './resistance/resistanceSeries'
import { createSupportSeries, updateSupportSeries } from './support/supportSeries'

// =============== ADD CREATE SERIES HERE ===============
const seriesCreators = {
  'main': [
    createCandlesSeries,
    createHighsSeries,
    createLowsSeries,
    createResistanceSeries,
    createSupportSeries,
  ],
  'rsi': [ createRsiSeries ],
}
// ======================================================

// =============== ADD UPDATE SERIES HERE ===============
const seriesUpdaters = {
  updateCandlesSeries,
  updateRsiSeries,
  updateHighsSeries,
  updateLowsSeries,
  updateResistanceSeries,
  updateSupportSeries,
}
// ======================================================

export const createDfSeries = (charts) => {
  const series = {}
  Object.keys(charts).forEach(chartType => {
    const chart = charts[chartType]
    seriesCreators[chartType].forEach((createSeries) => {
      const name = createSeries.name.toLowerCase().replace('create', '').replace('series', '')
      series[name] = createSeries(chart)
    })
  })
  return series
}

export const updateDfSeries = (name, series, data) => {
  const upperName = name.charAt(0).toUpperCase() + name.slice(1)
  const seriesUpdaterName = 'update' + upperName + 'Series'
  if (seriesUpdaters[seriesUpdaterName] === undefined) return
  seriesUpdaters[seriesUpdaterName](name, series, data)
}
