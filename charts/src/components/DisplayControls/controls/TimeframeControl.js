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
  const timeframeOptions = config.timeframes.map(timeframe =>
    <option key={timeframe} value={timeframe}>{timeframe}</option>
  )

  return (
    <div>
      <span>
        Current timeframe:
        <select onChange={(e) => changeTimeframe(e.target.value)} defaultValue={currentTimeframe}>
          {timeframeOptions}
        </select>
      </span>
    </div>
  )
}

export default TimeframeControl