import { updateTimeStoreDisplay } from '../../../utils/redux-dispatchers/dispatchers'
import { Context } from '../../../context'
import { useContext } from 'react'
import config from '../../../config.json'

const DateControl = () => {
  const { series, setDfComponent } = useContext(Context)

  const submitDate = async (e) => {
    e.preventDefault()
    const timestamp = (new Date(e.target.date.value)).getTime()
    
    await updateTimeStoreDisplay({
      timestamp,
      series,
      setDfComponent,
      updateMethod: config.updateMethod.TRUNCATE_ALL,
      exceptions: ['timeframe']
    })

    e.target.reset()
  }
  return (
    <form onSubmit={submitDate}>
      <label>
        Date
        <input type="text" name="date"></input>
      </label>
    </form>
  )
}

export default DateControl