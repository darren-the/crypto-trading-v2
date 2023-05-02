export const createAggbuysellSeries = (chart) => {}

export const updateAggbuysellSeries = (name, series, data) => {
  if (series.candles === undefined) return
  const markers = data.filter(item => item.buy || item.sell).map(item => {
    var text = ''
    if (item.buy && item.sell) text = 'BUY/SELL'
    else if (item.buy) text = 'BUY'
    else if (item.sell) text = 'SELL'

    return {
      time: item.time,
      position: 'belowBar',
      color: '#000000',
      shape: 'arrowUp',
      text: text
    }
  })
  series.candles.setMarkers(markers)
}