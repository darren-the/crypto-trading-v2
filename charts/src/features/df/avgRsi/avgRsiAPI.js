import axios from 'axios'
import { getQueryParamsUrl } from '../../../utils/utils'
import config from '../../../config.json'

export const fetchAvgrsi = async ({
  symbol,
  timeframe,
  pipelineId,
  start,
  end,
}) => {
  const queryParams = getQueryParamsUrl(symbol, timeframe, pipelineId, start, end)
  return await axios.get(`${config.api.base_url}${config.avgrsi.path}${queryParams}`).then(response => {
    return response.data.data.map(element => {
      return {
        baseTime: element[0],
        time: element[1] / 1000,
        value: element[2],
        is_complete: element[3],
      }
    })
  })
  .catch(error => error)
}