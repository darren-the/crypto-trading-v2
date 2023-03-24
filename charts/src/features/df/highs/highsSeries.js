import { store } from '../../../app/store'
import { selectDisplayedData } from '../../../utils/redux-dispatchers/dispatch-utils'
import config from '../../../config.json'

export const createHighsSeries = (chart) => {
  const series = chart.addCandlestickSeries({})
  series.applyOptions({
    wickUpColor: '#3674d9',
    upColor: '#3674d9',
    wickDownColor: '#3674d9',
    downColor: '#3674d9',
    borderVisible: false,
    priceLineVisible: false,
  })
  return series
}

export const updateHighsSeries = (name, series, data) => {
  const candlesDisplayedData = selectDisplayedData('candles')
  const timeframe = store.getState().candles.timeframe
  if (data.length > 0 && candlesDisplayedData.length > 0) {
    const candleHighs = data[0].high_history.map(highTime => {
      const index = (highTime - candlesDisplayedData[0].time * 1000) / config.timeframeToMs[timeframe]
      return candlesDisplayedData[index]
    })
    series[name].setData(candleHighs.filter(high => high !== undefined))
  }

}