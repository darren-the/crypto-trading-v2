import { useEffect } from 'react'
import config from '../../config.json'
import { fetchCandles, fetchHighs, fetchLows, fetchResistance, fetchRetracement, fetchRsi, fetchSupport } from '../../services/fetch_data'
import { useContext } from 'react'
import { MainContext } from '../../context'


export const useUpdateLiveSeries = () => {
  const context = useContext(MainContext)
  const {
    chart,
    series,
    timeframe,
    truncTime,
    loadMode,
    setLoadMode,
    endOfDataFlag,
    isLoading,
    rsi,
    // new stuff
    features,
  } = context

  useEffect(() => {
    if (loadMode === config.loadMode.NONE || series == null) return
    setLoadMode(config.loadMode.NONE)  // set here to immediately prevent consecutive calls

    var start = null
    var end = null
    var concatMethod = (data) => data

    // configure start/end window for fetching data and configure concatenation method.
    if (loadMode === config.loadMode.PREPEND) {
      end = features.Candles.state[0].time_ms
      start = end - (config.timeframe_to_ms[timeframe] * config.candles.liveFetchWindow)
      concatMethod = (oldData, newData) => newData.concat(oldData)

    } else if (loadMode === config.loadMode.APPEND) {
      // APPEND is disabled for live chart
      console.log('APPEND is disabled for live chart')
      endOfDataFlag.current = true
      isLoading.current = false
      return
    } else if (loadMode === config.loadMode.TRUNCATE_ALL) {
      start = truncTime - (config.timeframe_to_ms[timeframe] * config.candles.liveFetchWindow / 2)
      end = truncTime + (config.timeframe_to_ms[timeframe] * config.candles.liveFetchWindow / 2)
      concatMethod = (oldData, newData) => newData
    }

    const updateSeries = async () => {
      await features.Candles.update({ start, end, concatMethod })

      // set visible range
      if (loadMode === config.loadMode.TRUNCATE_ALL) {
        chart.timeScale().setVisibleRange({
          from: (truncTime - config.timeframe_to_ms[timeframe] * config.candles.defaultVisibleWindow) / 1000,
          to: truncTime
        })
      }

      // Show all data
      Object.entries(series).forEach(([k,v]) => {
        v.applyOptions({
          visible: true
        })
      })

      isLoading.current = false
    }

    updateSeries()

  // eslint-disable-next-line
  }, [loadMode, features, rsi])
}
