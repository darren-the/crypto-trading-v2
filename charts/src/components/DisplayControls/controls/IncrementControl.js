import { Context } from '../../../context'
import { useContext } from 'react'
import { incrementDisplay, decrementDisplay } from '../../../utils/redux-dispatchers/dispatchers'

const IncrementControl = () => {
  const { series, setDfComponent } = useContext(Context)
  return (
    <div>
      <button onClick={() => decrementDisplay({ series, setDfComponent })}>Decrement</button>
      <button onClick={() => incrementDisplay({ series, setDfComponent })}>Increment</button>
    </div>
  )
}

export default IncrementControl