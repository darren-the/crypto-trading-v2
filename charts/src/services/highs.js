import axios from 'axios'
import config from '../config.json'

export const fetchHighs = (
  timeframe,
  start,
  end
) => {
  return axios.get(`${config.base_url}${config.highs.path}?timeframe=${timeframe}&start=${start}&end=${end}`).then(response => {
    return response.data.data
})
  .catch(error => 
    console.log(error)
  )
}