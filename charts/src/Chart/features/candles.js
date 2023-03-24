import { BaseFeature } from './base/base'
import config from '../../config.json'
import { get_query_params_url } from '../../utils'
import axios from 'axios'

export class Candles extends BaseFeature {
    constructor({ context, featureState, setFeatureState} ) {
        super({ featureState, setFeatureState })
        this.context = context
    }

    fetch = async ({
        start,
        end,
        concatMethod,
    }) => {
        const {
            symbol,
            timeframe,
            pipelineId,
            loadMode,
            liveIndex,
            truncTime,
            startOfDataFlag,
            endOfDataFlag,
        } = this.context

        // Fetch data
        const query_params = get_query_params_url(symbol, timeframe, pipelineId, start, end)
        const base_url = config.live_base_url
        const data = await axios.get(`${base_url}${config.candles.path}${query_params}`).then(response => {
            // Format candle data
            return response.data.data.map(element => {
                return {
                    base_time: element[0] / 1000,
                    time: element[1] / 1000,
                    time_ms: element[1],
                    open: element[2],
                    close: element[3],
                    high: element[4],
                    low: element[5],
                    is_complete: element[6],
                }
            })
        })
        .catch(error => 
            console.log(error)
        )
        
        const newData = concatMethod(this.state, data)
        this.setState(newData)
        
        // Determine live index
        if (loadMode === config.loadMode.TRUNCATE_ALL) {
            liveIndex.current = newData.findIndex(candle => candle.base_time === truncTime / 1000) - 1
        } else if (loadMode === config.loadMode.PREPEND) {
            liveIndex.current = liveIndex.current + data.length
        }

        // Check whether there is anymore data to be fetched
        if (data.length === 0) {
            if (loadMode === config.loadMode.PREPEND) {
                console.log('start of data')
                startOfDataFlag.current = true
            }
            if (loadMode === config.loadMode.APPEND) {
                console.log('end of data')
                endOfDataFlag.current = true
            }
            if (loadMode === config.loadMode.TRUNCATE_ALL) console.log('Invalid range: No data in database for this range')
        }

        return newData
    }

    updateSeries = ({ data }) => {
        const {
            liveIndex,
            liveCandles,
            series,
        } = this.context

        const histData = data.slice(0, liveIndex.current + 1)
        liveCandles.current = histData.filter(candle => candle.is_complete)  // aggregate history

        // append last candle if incomplete
        const lastCandle = histData[histData.length - 1]
        if (!lastCandle.is_complete) liveCandles.current.push(lastCandle)
        series.candleSeries.setData(liveCandles.current)
    }

    incrementSeries = ({ direction }) => {
        const {
            liveIndex,
            liveCandles,
            series,
        } = this.context

        if (direction === 1) {
            liveIndex.current++
            if (this.state[liveIndex.current - 1].time < this.state[liveIndex.current].time) {
                liveCandles.current.push(this.state[liveIndex.current])
            } else if (this.state[liveIndex.current - 1].time === this.state[liveIndex.current].time) {
                liveCandles.current[liveCandles.current.length - 1] = this.state[liveIndex.current]
            }
            series.candleSeries.setData(liveCandles.current)
        } else if (direction === 0) {
            liveIndex.current--
            if (this.state[liveIndex.current].time < this.state[liveIndex.current + 1].time) {
            liveCandles.current.pop()
            } else if (this.state[liveIndex.current].time === this.state[liveIndex.current + 1].time) {
            liveCandles.current[liveCandles.current.length - 1] = this.state[liveIndex.current]
            }
            series.candleSeries.setData(liveCandles.current)
        }
    }
}