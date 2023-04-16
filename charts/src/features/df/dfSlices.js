import { createSlice, current } from '@reduxjs/toolkit'
import { fetchDataFeatureThunk } from './dfAPIs'
import config from '../../config.json'
import { singleReducers } from './commonReducers'

// =============== ADD SLICE NAMES HERE ===============
const sliceNames = [
  'candles',
  'rsi',
  'highs',
  'lows',
  'resistance',
  'support',
  'retracement',
]
// ====================================================

// ============ ADD OVERRIDE REDUCERS HERE ============
const overrideReducers = {
  'highs': singleReducers,
  'lows': singleReducers,
  'resistance': singleReducers,
  'support': singleReducers,
  'retracement': singleReducers,
}
// ====================================================

export const dfSlices = sliceNames.map(sliceName => {
  const initialState = {
    pipelineId: config.defaultPipelineId,
    symbol: config.defaultSymbol,
    timeframe: config.defaultTimeframe,
    storedData: [],
    displayedData: [],
    displayIndex: -1,
    displayTime: -1,
    status: 'idle',
    prependable: true,
    appendable: true,
    incrementMs: config.baseMs,
    incrementIndex: 1,
  }
  const slice = createSlice({
    name: sliceName,
    initialState,
    reducers: {
      setDisplayTime: (state, action) => void(state.displayTime = action.payload),
      setTimeframe: (state, action) => void(state.timeframe = action.payload),
      startLoading: (state) => void(state.status = 'loading'),
      finishLoading: (state) => void(state.status = 'idle'),
      resetState: (state, action) => {
        const newState = Object.assign({}, initialState)
        const exceptions = action.payload
        exceptions.forEach(exception => newState[exception] = state[exception])
        return newState
      },
      falsifyPendable: (state, action) => {
        const updateMethod = action.payload
        if (updateMethod === config.updateMethod.PREPEND) state.prependable = false
        else if (updateMethod === config.updateMethod.APPEND) state.appendable = false
      },
      updateDisplayedData: (state) => {
        if (state.storedData.length === 0) return

        const storedData = current(state.storedData)
        const displayedData = current(state.displayedData)

        if (state.displayedData.length === 0) {
          // TRUNCATE
          const newDisplayIndex = storedData.findIndex(data => data.baseTime === state.displayTime) - 1
          state.displayIndex = Math.max(newDisplayIndex, 0)  // edge case: new display index is negative
          const slicedData = storedData.slice(0, state.displayIndex + 1)
          const aggregatedData = slicedData.filter(data => data.is_complete)
          const lastCandle = slicedData[slicedData.length - 1]
          if (!lastCandle.is_complete) aggregatedData.push(lastCandle)
          state.displayedData = aggregatedData

        } else if (storedData[0].baseTime < displayedData[0].baseTime) {
          // PREPEND
          const sliceEndIndex = storedData.findIndex(data =>
            data.baseTime === displayedData[0].baseTime
          )
          const slicedData = storedData.slice(0, sliceEndIndex)
          const aggregatedData = slicedData.filter(data => data.is_complete)
          state.displayedData = aggregatedData.concat(displayedData)

        } else if (displayedData[displayedData.length - 1].baseTime < storedData[storedData.length - 1].baseTime) {
          // APPEND
          // const sliceStartIndex = storedData.findIndex(data =>
          //   data.baseTime === displayedData[displayedData.length - 1].baseTime
          // )
          // const slicedData = storedData.slice(sliceStartIndex)
          // const aggregateData = slicedData.filter(data => data.is_complete)

          // TODO: need to figure out how to properly implement this with regards to displayIndex
        }
      },
      incrementDisplay: (state) => {
        const storedData = current(state.storedData)
        const newDisplayIndex = state.displayIndex + state.incrementIndex
        if (newDisplayIndex >= storedData.length) return
        const newDisplaySlice = storedData.slice(state.displayIndex + 1, newDisplayIndex)
        const newDisplaySliceFiltered = newDisplaySlice.filter(data => data.is_complete)
        const displayedData = current(state.displayedData).concat(newDisplaySliceFiltered)
        if (displayedData[displayedData.length - 1].time < storedData[newDisplayIndex].time) {
          state.displayedData = displayedData.concat(storedData[newDisplayIndex])
        } else if (displayedData[displayedData.length - 1].time === storedData[newDisplayIndex].time) {
          state.displayedData = displayedData.slice(0, displayedData.length - 1).concat(storedData[newDisplayIndex])
        }
        state.displayIndex = newDisplayIndex
        state.displayTime = storedData[newDisplayIndex].baseTime + config.baseMs
      },
      decrementDisplay: (state) => {
        const displayedData = current(state.displayedData)
        const storedData = current(state.storedData)
        const newDisplayIndex = state.displayIndex - state.incrementIndex
        
        if (newDisplayIndex < 0) return

        if (storedData[newDisplayIndex].time < displayedData[displayedData.length - 1].time) {
          const decrementIndex = Math.max(state.incrementMs / config.timeframeToMs[state.timeframe] - 1, 0)
          state.displayedData = displayedData.slice(0, displayedData.length - 1 - decrementIndex)
        } else if (storedData[newDisplayIndex].time === displayedData[displayedData.length - 1].time) {
          state.displayedData = displayedData.slice(0, displayedData.length - 1).concat(storedData[newDisplayIndex])
        }
        state.displayIndex = newDisplayIndex
        state.displayTime = storedData[newDisplayIndex].baseTime + config.baseMs
      },
      changeIncrement: (state, action) => {
        const newIncrementMs = action.payload
        if (
          newIncrementMs === state.incrementMs
          || (
            newIncrementMs > config.timeframeToMs[state.timeframe]
            && newIncrementMs % config.timeframeToMs[state.timeframe] !== 0
          )
          || (
            newIncrementMs < config.timeframeToMs[state.timeframe]
            && config.timeframeToMs[state.timeframe] % newIncrementMs !== 0
          )
        ) return
        state.incrementMs = newIncrementMs
        state.incrementIndex = newIncrementMs / config.baseMs
        state.displayTime = state.displayTime - (state.displayTime % state.incrementMs)
        state.displayedData = []
      },
      ...overrideReducers[sliceName]
    },
    extraReducers: (builder) => {
    builder
      .addCase(fetchDataFeatureThunk[sliceName].fulfilled, (state, action) => {
        const data = action.payload
        if (data.length === 0) return
        const storedData = current(state.storedData)
        if (storedData.length === 0) state.storedData = data  // TRUNCATE
        else if (data[data.length - 1].baseTime + config.baseMs === storedData[0].baseTime) {
          // PREPEND
          state.storedData = data.concat(storedData)
          if (state.displayIndex !== -1) state.displayIndex += data.length
        } else if (storedData[storedData.length - 1].baseTime + config.baseMs === data[0].baseTime) {
          // APPEND
          state.storedData = storedData.concat(data)
        }
      })
    },
  })
  return slice
})

export const dfReducers = Object.fromEntries(dfSlices.map(slice => [slice.name, slice.reducer]))
