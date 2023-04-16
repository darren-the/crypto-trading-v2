import { current } from "@reduxjs/toolkit"
import config from '../../config.json'

export const updateDisplayedDataSingle = (state) => {
  if (state.storedData.length === 0) return
  const storedData = current(state.storedData)
  const newDisplayIndex = storedData.findIndex(data => data.baseTime === state.displayTime) - 1
  state.displayIndex = Math.max(newDisplayIndex, 0)  // edge case: new display index is negative
  state.displayedData = [storedData[state.displayIndex]]
}

export const incrementDisplaySingle = (state) => {
  const storedData = current(state.storedData)
  const newDisplayIndex = state.displayIndex + state.incrementIndex
  if (newDisplayIndex >= storedData.length) return
  state.displayedData = [storedData[newDisplayIndex]]
  state.displayIndex = newDisplayIndex
  state.displayTime = storedData[newDisplayIndex].baseTime + config.baseMs
}

export const decrementDisplaySingle = (state) => {
  const storedData = current(state.storedData)
  const newDisplayIndex = state.displayIndex - state.incrementIndex
  if (newDisplayIndex < 0) return
  state.displayedData = [storedData[newDisplayIndex]]
  state.displayIndex = newDisplayIndex
  state.displayTime = storedData[newDisplayIndex].baseTime + config.baseMs
}

export const singleReducers = {
  updateDisplayedData: updateDisplayedDataSingle,
  incrementDisplay: incrementDisplaySingle,
  decrementDisplay: decrementDisplaySingle,
}
