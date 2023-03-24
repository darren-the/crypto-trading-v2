import { updateTimeframeStoreDisplay } from '../../../utils/redux-dispatchers/dispatchers'
import config from '../../../config.json'
import { useContext, useState } from 'react'
import { Context } from '../../../context'

const TimeframeControl = () => {
  const { series, setDfComponent } = useContext(Context)
  const [currentTimeframe, setCurrentTimeframe] = useState(config.defaultTimeframe)

  const changeTimeframe = async (timeframe) => {
    await updateTimeframeStoreDisplay({
      timeframe,
      series,
      setDfComponent,
      updateMethod: config.updateMethod.TRUNCATE_ALL,
      exceptions: ['displayTime'],
    })
    setCurrentTimeframe(timeframe)
  }
  const timeframeButtons = config.timeframes.map(timeframe => 
    <button key={timeframe} onClick={() => changeTimeframe(timeframe)}>{timeframe}</button>  
  )
  return (
    <div>
      {timeframeButtons}
      <span>Current timeframe: {currentTimeframe}</span>
    </div>
  )
}

export default TimeframeControl