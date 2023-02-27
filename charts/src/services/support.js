import axios from 'axios'
import config from '../config.json'

export const fetchSupport= (
  timeframe,
  start,
  end
) => {
  return axios.get(`${config.base_url}${config.support.path}?timeframe=${timeframe}&start=${start}&end=${end}`).then(response => {
    // Format support data
    return response.data.data.map(element => {
      return {
        time: element[0] / 1000,
        time_ms: element[0],
        bottom_history: element[1].split(',').map(bottom => parseFloat(bottom))
      }
    })
})
  .catch(error => 
    console.log(error)
  )
}