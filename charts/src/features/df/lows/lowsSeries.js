import { store } from '../../../app/store'
import { selectDisplayedData } from '../../../utils/redux-dispatchers/dispatch-utils'
import config from '../../../config.json'

export const createLowsSeries = (chart) => {
  const series = chart.addCandlestickSeries({})
  series.applyOptions({
    wickUpColor: '#fccb19',
    upColor: '#fccb19',
    wickDownColor: '#fccb19',
    downColor: '#fccb19',
    borderVisible: false,
    priceLineVisible: false,
  })
  return series
}

export const updateLowsSeries = (name, series, data) => {
  const candlesDisplayedData = selectDisplayedData('candles')
  const timeframe = store.getState().candles.timeframe
  if (data.length > 0 && candlesDisplayedData.length > 0) {
    const candleLows = data[0].low_history.map(lowTime => {
      const index = (lowTime - candlesDisplayedData[0].time * 1000) / config.timeframeToMs[timeframe]
      return candlesDisplayedData[index]
    })
    series[name].setData(candleLows.filter(low => low !== undefined))
  }

}