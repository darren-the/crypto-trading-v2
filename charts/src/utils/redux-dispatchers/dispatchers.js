import config from '../../config.json'
import { store } from '../../app/store'
import {
  setDisplayTime,
  setTimeframe,
  resetAll,
  updateStore,
  updateDisplay,
  dispatchChangeIncrement,
} from './dispatch-utils'
import { horizontalDispatcher } from './base-dispatchers'
import { selectDisplayedData } from './dispatch-utils'
import { updateDfSeries } from '../../features/df/dfSeries'
import { updateDfComponent } from '../../features/df/dfComponents'

export const incrementDisplay = horizontalDispatcher([
  async ({ name, series, setDfComponent }) => {
    const state = store.getState()
    if (state[name].displayIndex + state[name].incrementIndex >= state[name].storedData.length) {
      await updateStore({ name, updateMethod: config.updateMethod.APPEND })
    }
    if (state[name].displayIndex + state[name].incrementIndex < store.getState()[name].storedData.length) {
      store.dispatch({ type: `${name}/incrementDisplay` })
      const displayedData = selectDisplayedData(name)
      updateDfSeries(name, series, displayedData)
      updateDfComponent(name, setDfComponent, displayedData)

    }
  }
], ['loading', 'display'])

export const decrementDisplay = horizontalDispatcher([
  async ({ name, series, setDfComponent }) => {
    const state = store.getState()
    if (state[name].displayIndex - state[name].incrementIndex < 0) {
      await updateStore({ name, updateMethod: config.updateMethod.PREPEND })
    }
    if (store.getState()[name].displayIndex - state[name].incrementIndex >= 0) {
      store.dispatch({ type: `${name}/decrementDisplay` })
      const displayedData = selectDisplayedData(name)
      updateDfSeries(name, series, displayedData)
      updateDfComponent(name, setDfComponent, displayedData)

    }
  }
], ['loading', 'display'])

export const updateTimeStoreDisplay = horizontalDispatcher([
  resetAll,
  setDisplayTime,
  updateStore,
  updateDisplay,
], ['loading'])

export const updateTimeframeStoreDisplay = horizontalDispatcher([
  resetAll,
  setTimeframe,
  updateStore,
  updateDisplay,
], ['loading'])

export const updateVisibleRange = horizontalDispatcher(
  [updateStore, updateDisplay],
  ['loading', 'pendable'],
)

export const changeIncrement = horizontalDispatcher([
  dispatchChangeIncrement,
  updateDisplay,
], ['loading'])
