export const createSupportSeries = (chart) => {
  const series = chart.addLineSeries({})
  return series
}

export const updateSupportSeries = (name, series, data) => {
  if (series.lows === undefined) return
  series.lows._internal__series._private__customPriceLines = []
  series.lows._internal__series._internal_model()._internal_updateSource(series.highs._internal__series)
  if (data.length > 0) {
    data[0].bottom_history.forEach(bottom => {
      series.lows.createPriceLine({
        price: bottom,
        color: '#26a69a',
        lineWidth: 2,
        lineStyle: 0,
      })
    })
  }
}