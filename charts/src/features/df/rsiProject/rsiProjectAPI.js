import axios from 'axios'
import { getQueryParamsUrl } from '../../../utils/utils'
import config from '../../../config.json'

export const fetchRsiproject = async ({
  symbol,
  timeframe,
  pipelineId,
  start,
  end,
}) => {
  const queryParams = getQueryParamsUrl(symbol, timeframe, pipelineId, start, end)
  return await axios.get(`${config.api.base_url}${config.rsiproject.path}${queryParams}`).then(response => {
    return response.data.data.map(element => {
      return {
        baseTime: element[0],
        time: element[1],
        priceProjection: element[2],
        is_complete: element[3],
      }
    })
  })
  .catch(error => error)
}
