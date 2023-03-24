import { BaseFeature } from './base/base'

export class Rsi extends BaseFeature {
    constructor(context) {
        super(context)
    }

    fetch = async ({
        start,
        end,
        concatMethod,
    }) => {
        // Fetch data
        const query_params = get_query_params_url(symbol, timeframe, pipelineId, start, end)
        const base_url = config.live_base_url
        const data = await axios.get(`${base_url}${config.candles.path}${query_params}`).then(response => {
            // Format rsi data
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
        
        const newData = concatMethod(this.state, data)
        this.setState(newData)
    }

    // TODO: complete once liveCandles/candleSeries etc have been refactored as a part of classes
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
        series.rsiSeries.setData(liveCandles.current)
    }
}