import axios from 'axios'
import { getQueryParamsUrl } from '../../../utils/utils'
import config from '../../../config.json'

export const fetchRisk = async ({
  symbol,
  timeframe,
  pipelineId,
  start,
  end,
}) => {
  const queryParams = getQueryParamsUrl(symbol, timeframe, pipelineId, start, end)
  return await axios.get(`${config.api.base_url}${config.risk.path}${queryParams}`).then(response => {
    return response.data.data.map(element => {
      return {
        baseTime: element[0],
        recent_sup_top: element[1],
        recent_sup_bottom: element[2],
        risk: element[3],
      }
    })
  })
  .catch(error => error)
}
