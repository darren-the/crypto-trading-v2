import axios from 'axios'
import config from '../config.json'

export const fetchCandles = (
  timeframe,
  start,
  end
) => {
  return axios.get(`${config.base_url}${config.candles.path}?timeframe=${timeframe}&start=${start}&end=${end}`).then(response => {
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

export const fetchResistance = (
  timeframe,
  start,
  end
) => {
  return axios.get(`${config.base_url}${config.resistance.path}?timeframe=${timeframe}&start=${start}&end=${end}`).then(response => {
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
  timeframe,
  start,
  end
) => {
  return axios.get(`${config.base_url}${config.support.path}?timeframe=${timeframe}&start=${start}&end=${end}`).then(response => {
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
  timeframe,
  start,
  end
) => {
  return axios.get(`${config.base_url}${config.rsi.path}?timeframe=${timeframe}&start=${start}&end=${end}`).then(response => {
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