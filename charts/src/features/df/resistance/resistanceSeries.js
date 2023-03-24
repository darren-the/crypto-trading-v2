export const createResistanceSeries = (chart) => {
  const series = chart.addLineSeries({})
  return series
}

export const updateResistanceSeries = (name, series, data) => {
  if (series.highs === undefined) return
  series.highs._internal__series._private__customPriceLines = []
  series.highs._internal__series._internal_model()._internal_updateSource(series.highs._internal__series)
  if (data.length > 0) {
    data[0].top_history.forEach(top => {
      series.highs.createPriceLine({
        price: top,
        color: '#ef5350',
        lineWidth: 2,
        lineStyle: 0,
      })
    })
  }
}