import axios from 'axios'
import { getQueryParamsUrl } from '../../../utils/utils'
import config from '../../../config.json'

export const fetchHighs = async ({
  symbol,
  timeframe,
  pipelineId,
  start,
  end
}) => {
  const queryParams = getQueryParamsUrl(symbol, timeframe, pipelineId, start, end)
  return await axios.get(`${config.api.base_url}${config.highs.path}${queryParams}`).then(response => {
    // Format highs data
    return response.data.data.map(element => {
      return {
        baseTime: element[0],
        time: element[1] / 1000,
        high_history: element[2].split(',').map(high => parseFloat(high)),
        is_complete: element[3]
      }
    })
})
  .catch(error => error)
}