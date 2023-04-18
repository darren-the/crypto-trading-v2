export const createAggretracelongSeries = (chart) => {}

export const updateAggretracelongSeries = (name, series, data) => {
  if (series.candles === undefined) return
  const markers = data.filter(item => item.long).map(retraceLong => {
    return {
      time: retraceLong.time,
      position: 'belowBar',
      color: '#000000',
      shape: 'arrowUp',
      text: 'LONG',
    }
  })
  series.candles.setMarkers(markers)
}