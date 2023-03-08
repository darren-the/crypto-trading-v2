import axios from 'axios'
import config from '../config.json'
import { get_query_params_url } from '../utils'

export const fetchCandles = (
  symbol,
  timeframe,
  pipelineId,
  start,
  end
) => {
  const query_params = get_query_params_url(symbol, timeframe, pipelineId, start, end)
  return axios.get(`${config.base_url}${config.candles.path}${query_params}`).then(response => {
    // Format candle data
    return response.data.data.map(element => {
      return {
        time: element[0] / 1000,
        time_ms: element[0],
        open: element[1],
        close: element[2],
        high: element[3],
        low: element[4],
      }
    })
})
  .catch(error => 
    console.log(error)
  )
}

export const fetchHighs = (
  symbol,
  timeframe,
  pipelineId,
  start,
  end
) => {
  const query_params = get_query_params_url(symbol, timeframe, pipelineId, start, end)
  return axios.get(`${config.base_url}${config.highs.path}${query_params}`).then(response => {
    return response.data.data.map(element => element[0])
})
  .catch(error => 
    console.log(error)
  )
}

export const fetchLows = (
  symbol,
  timeframe,
  pipelineId,
  start,
  end
) => {
  const query_params = get_query_params_url(symbol, timeframe, pipelineId, start, end)
  return axios.get(`${config.base_url}${config.lows.path}${query_params}`).then(response => {
    return response.data.data.map(element => element[0])
})
  .catch(error => 
    console.log(error)
  )
}

export const fetchResistance = (
  symbol,
  timeframe,
  pipelineId,
  start,
  end
) => {
  const query_params = get_query_params_url(symbol, timeframe, pipelineId, start, end)
  return axios.get(`${config.base_url}${config.resistance.path}${query_params}`).then(response => {
    // Format resistance data
    return response.data.data.map(element => {
      return {
        time: element[0] / 1000,
        time_ms: element[0],
        top_history: element[1].split(',').map(top => parseFloat(top))
      }
    })
})
  .catch(error => 
    console.log(error)
  )
}

export const fetchSupport = (
  symbol,
  timeframe,
  pipelineId,
  start,
  end
) => {
  const query_params = get_query_params_url(symbol, timeframe, pipelineId, start, end)
  return axios.get(`${config.base_url}${config.support.path}${query_params}`).then(response => {
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

export const fetchRsi = (
  symbol,
  timeframe,
  pipelineId,
  start,
  end
) => {
  const query_params = get_query_params_url(symbol, timeframe, pipelineId, start, end)
  return axios.get(`${config.base_url}${config.rsi.path}${query_params}`).then(response => {
    // Format support data
    return response.data.data.map(element => {
      return {
        time: element[0] / 1000,
        time_ms: element[0],
        value: element[1],
      }
    })
})
  .catch(error => 
    console.log(error)
  )
}