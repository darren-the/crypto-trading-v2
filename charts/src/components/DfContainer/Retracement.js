import { Context } from '../../context'
import { useContext } from 'react'

const Retracement = () => {
  const { dfComponents } = useContext(Context)
  return dfComponents.retracement
} 

export default Retracement