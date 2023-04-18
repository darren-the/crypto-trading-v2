import axios from 'axios'
import { getQueryParamsUrl } from '../../../utils/utils'
import config from '../../../config.json'

export const fetchRetracelong = async ({
  symbol,
  timeframe,
  pipelineId,
  start,
  end,
}) => {
  const queryParams = getQueryParamsUrl(symbol, timeframe, pipelineId, start, end)
  return await axios.get(`${config.api.base_url}${config.retracelong.path}${queryParams}`).then(response => {
    return response.data.data.map(element => {
      return {
        baseTime: element[0],
        retracementTimeframe: element[1],
        highRetracement: element[2],
        oversoldTimeframe: element[3],
        avgRsi: element[4],
      }
    })
  })
  .catch(error => error)
}
