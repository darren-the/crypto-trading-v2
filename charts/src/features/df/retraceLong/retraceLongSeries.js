export const createRetracelongSeries = (chart) => {}

export const updateRetracelongSeries = (name, series, data) => {
  if (series.candles === undefined) return
  const markers = data.filter(item => item.long).map(retraceLong => {
    return {
      time: retraceLong.time,
      position: 'aboveBar',
      color: '#000000',
      shape: 'arrowDown',
      text: 'LONG',
    }
  })
  series.candles.setMarkers(markers)
}