import { useContext } from 'react'
import config from '../config.json'
import MainContext from '../App'

const {
  chart,
  series,
  isLoading,
  startOfDataFlag,
  endOfDataFlag,
  setLoadMode,
  lastIndex,
} = useContext(MainContext)

export const useVisibleLogicalRangeChange = () => {
  useEffect(() => {
    if (chart == null || series == null) return

    const VLRChangeHandler = (VLR) => {
      if (isLoading.current) return
      
      if (!startOfDataFlag.current && VLR.from < 0) {
        isLoading.current = true
        console.log('need more previous data')
        isLoading.current = true
        setLoadMode(config.loadMode.PREPEND)
      } else if (!endOfDataFlag.current && lastIndex.current != null && VLR.to > lastIndex.current) {
        isLoading.current = true
        console.log('need next data')
        isLoading.current = true
        setLoadMode(config.loadMode.APPEND)
      }
    }
    chart.timeScale().subscribeVisibleLogicalRangeChange(VLRChangeHandler)

  // eslint-disable-next-line
  }, [series])
}
