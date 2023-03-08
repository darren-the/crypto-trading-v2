export const get_query_params_url = (
    symbol='BTCUSD',
    timeframe,
    pipelineId,
    start,
    end
) => {
    return `?symbol=${symbol}&timeframe=${timeframe}&pipeline_id=${pipelineId}&start=${start}&end=${end}`
}