export const createRsiSeries = (chart) => {
  const series = chart.addLineSeries()
  series.applyOptions({
    lineWidth: 2,
  })

  // 70 rsi bound
  series.createPriceLine({
    price: 70,
    color: '#000000',
    lineWidth: 2,
    lineStyle: 2,
  })

  // 30 rsi bound
  series.createPriceLine({
    price: 30,
    color: '#000000',
    lineWidth: 2,
    lineStyle: 2,
  })

  return series
}

export const updateRsiSeries = (name, series, data) => series[name].setData(data)
