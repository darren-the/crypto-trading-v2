export const createTraderSeries = (chart) => {
  const series = chart.addAreaSeries()
  series.applyOptions({
    lineWidth: 2,
    color: '#7600bc',
  })
  return series
}

export const updateTraderSeries = (name, series, data) => series[name].setData(data)
  