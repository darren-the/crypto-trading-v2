export const createCandlesSeries = (chart) => {
  const series = chart.addCandlestickSeries({})
  return series
}

export const updateCandlesSeries = (name, series, data) => series[name].setData(data)
