import axios from 'axios'
import config from '../config.json'

export const fetchLows = (
  timeframe,
  start,
  end
) => {
  return axios.get(`${config.base_url}${config.lows.path}?timeframe=${timeframe}&start=${start}&end=${end}`).then(response => {
    return response.data.data
})
  .catch(error => 
    console.log(error)
  )
}