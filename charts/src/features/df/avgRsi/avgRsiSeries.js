export const createAvgrsiSeries = (chart) => {
  const series = chart.addLineSeries()
  series.applyOptions({
    lineStyle: 1,
    lineWidth: 2,
    color: '#7600bc',
  })
  return series
}

export const updateAvgrsiSeries = (name, series, data) => series[name].setData(data)
  