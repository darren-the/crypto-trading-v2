import { useEffect, useState } from 'react'
import { createDfSeries } from '../features/df/dfSeries'
import config from '../config.json'
import { updateVisibleRange } from '../utils/redux-dispatchers/dispatchers'

export const useCreateSeries = (mainChart, rsiChart) => {
  const [seriesState, setSeriesState] = useState({})

  useEffect(() => {
    if (mainChart === null || rsiChart === null) return
    
    const series = createDfSeries({ main: mainChart, rsi: rsiChart })
    setSeriesState(series)

    // Handle fetching data based on visible local range change
    const VLRChangeHandler = (VLR) => {
      if (VLR === null) return
      if (VLR.from < 0) updateVisibleRange({ series, updateMethod: config.updateMethod.PREPEND })
    }
    mainChart.timeScale().subscribeVisibleLogicalRangeChange(VLRChangeHandler)
  }, [mainChart, rsiChart])
  
  return seriesState
}
