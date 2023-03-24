import axios from 'axios'
import { getQueryParamsUrl } from '../../../utils/utils'
import config from '../../../config.json'

export const fetchSupport = async ({
  symbol,
  timeframe,
  pipelineId,
  start,
  end
}) => {
  const queryParams = getQueryParamsUrl(symbol, timeframe, pipelineId, start, end)
  return axios.get(`${config.api.base_url}${config.support.path}${queryParams}`).then(response => {
    return response.data.data.map(element => {
      return {
        baseTime: element[0],
        time: element[1] / 1000,
        bottom_history: element[2].split(',').map(top => parseFloat(top)),
        is_complete: element[3],
      }
    })
})
  .catch(error => error)
}