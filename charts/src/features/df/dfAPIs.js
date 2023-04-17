import { createAsyncThunk } from '@reduxjs/toolkit'
import { fetchCandles } from './candles/candlesAPI'
import { fetchRsi } from './rsi/rsiAPI'
import { fetchHighs } from './highs/highsAPI'
import { fetchLows } from './lows/lowsAPI'
import { fetchResistance } from './resistance/resistanceAPI'
import { fetchSupport } from './support/supportAPI'
import { fetchRetracement } from './retracement/retracementAPI'
import { fetchAvgrsi } from './avgRsi/avgRsiAPI'

// ================ ADD FETCH DATA HERE ================
const fetchDataFeatures = {
  fetchCandles,
  fetchRsi,
  fetchHighs,
  fetchLows,
  fetchResistance,
  fetchSupport,
  fetchRetracement,
  fetchAvgrsi,
}
// =====================================================

export const fetchDataFeatureThunk = Object.fromEntries(Object.keys(fetchDataFeatures).map(key => {
  const nameUpper = key.replace('fetch', '')
  const nameLower = nameUpper.toLowerCase()
  const actionType = `${nameLower}/fetch${nameUpper}`
  const fetchDataFeature = fetchDataFeatures[key]
  const thunk = createAsyncThunk(actionType, async(payload) => {
    const data = await fetchDataFeature(payload)
    return data
  })
  return [nameLower, thunk]
}))

// TODO define each async thunk here instead

// one async thunk which has a type parameter to call the specific fetchFeature function

/*
    const updateStoreAndDisplay = () => {

    }
*/
