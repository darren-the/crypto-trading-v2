export const createStructureSeries = (chart) => {
  const series = chart.addLineSeries({})
  return series
}

export const updateStructureSeries = (name, series, data) => {
  if (series.candles === undefined) return
  series.candles._internal__series._private__customPriceLines = []
  series.candles._internal__series._internal_model()._internal_updateSource(series.candles._internal__series)
  if (data.length > 0) {
    if (data[0].structTop >= 0) series.candles.createPriceLine({
      price: data[0].structTop,
      color: '#ef5350',
      lineWidth: 2,
      lineStyle: 0,
    })
    if (data[0].equilTop >= 0) series.candles.createPriceLine({
      price: data[0].equilTop,
      color: '#ef5350',
      lineWidth: 2,
      lineStyle: 0,
    })
    if (data[0].structBottom >= 0) series.candles.createPriceLine({
      price: data[0].structBottom,
      color: '#26a69a',
      lineWidth: 2,
      lineStyle: 0,
    })
    if (data[0].equilBottom >= 0) series.candles.createPriceLine({
      price: data[0].equilBottom,
      color: '#26a69a',
      lineWidth: 2,
      lineStyle: 0,
    })
  }
}