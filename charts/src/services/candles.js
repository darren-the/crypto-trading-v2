import axios from 'axios'
import config from '../config.json'

export const fetchCandles = (
  timeframe,
  start,
  end
) => {
  return axios.get(`${config.base_url}${config.candles.path}?timeframe=${timeframe}&start=${start}&end=${end}`).then(response => {
    // Format candle data
    return response.data.data.map(element => {
      return {
        time: element[0] / 1000,
        time_ms: element[0],
        open: element[1],
        close: element[2],
        high: element[3],
        low: element[4],
      }
    })
})
  .catch(error => 
    console.log(error)
  )
}