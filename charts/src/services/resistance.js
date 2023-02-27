import axios from 'axios'
import config from '../config.json'

export const fetchResistance = (
  timeframe,
  start,
  end
) => {
  return axios.get(`${config.base_url}${config.resistance.path}?timeframe=${timeframe}&start=${start}&end=${end}`).then(response => {
    // Format resistance data
    return response.data.data.map(element => {
      return {
        time: element[0] / 1000,
        time_ms: element[0],
        top_history: element[1].split(',').map(top => parseFloat(top))
      }
    })
})
  .catch(error => 
    console.log(error)
  )
}