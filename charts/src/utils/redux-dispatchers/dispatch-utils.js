import { store } from '../../app/store'
import config from '../../config.json'
import { fetchDataFeatureThunk } from '../../features/df/dfAPIs'
import { updateDfComponent } from '../../features/df/dfComponents'
import { updateDfSeries } from '../../features/df/dfSeries'

export const selectDfNames = () => Object.keys(store.getState())

export const selectDisplayedData = (name) => {
  return store.getState()[name].displayedData.map(data => Object.assign({}, data))
}

export const createPayload = (name, updateMethod) => {
  const state = store.getState()[name]
  var start = -1
  var end = -1
  if (updateMethod === config.updateMethod.TRUNCATE_ALL) {
    start = state.displayTime - (config.baseMs * config.api.fetchWindow / 2)
    end = state.displayTime + config.baseMs + (config.baseMs * config.api.fetchWindow / 2)
  } else if (updateMethod === config.updateMethod.PREPEND) {
    end = state.storedData[0].baseTime
    start = end - (config.baseMs * config.api.fetchWindow)
  } else if (updateMethod === config.updateMethod.APPEND) {
    start = state.storedData.at(-1).baseTime + config.baseMs
    end = start + (config.baseMs * config.api.fetchWindow)
  }
  return {
    pipelineId: state.pipelineId,
    symbol: state.symbol,
    timeframe: state.timeframe,
    start,
    end,
  }
}

export const setDisplayTime = ({ name, timestamp }) => {
  store.dispatch({ type: `${name}/setDisplayTime`, payload: timestamp })
}

export const setTimeframe = ({ name, timeframe, }) => {
  store.dispatch({ type: `${name}/setTimeframe`, payload: timeframe })
}

export const resetAll = ({ name, series, exceptions = [] }) => {
  if (series[name]) series[name].setData([])
  store.dispatch({ type: `${name}/resetState`, payload: exceptions })
}

export const updateStore = async ({
  name,
  updateMethod = config.updateMethod.TRUNCATE_ALL,
}) => {
  const payload = createPayload(name, updateMethod)
  const storedData = (await store.dispatch(fetchDataFeatureThunk[name](payload))).payload
  if (storedData.length === 0) store.dispatch({ type: `${name}/falsifyPendable`, payload: updateMethod })
}

export const updateDisplay = ({ name, series, setDfComponent }) => {
  store.dispatch({ type: `${name}/updateDisplayedData` })
  const displayedData = selectDisplayedData(name)
  updateDfSeries(name, series, displayedData)
  updateDfComponent(name, setDfComponent, displayedData)
}
