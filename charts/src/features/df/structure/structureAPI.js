import axios from 'axios'
import { getQueryParamsUrl } from '../../../utils/utils'
import config from '../../../config.json'

export const fetchStructure = async ({
  symbol,
  timeframe,
  pipelineId,
  start,
  end
}) => {
  const queryParams = getQueryParamsUrl(symbol, timeframe, pipelineId, start, end)
  return axios.get(`${config.api.base_url}${config.structure.path}${queryParams}`).then(response => {
    return response.data.data.map(element => {
      return {
        baseTime: element[0],
        time: element[1] / 1000,
        structTop: element[2],
        equilTop: element[3],
        structBottom: element[4],
        equilBottom: element[5],
        is_complete: element[6],
      }
    })
})
  .catch(error => error)
}