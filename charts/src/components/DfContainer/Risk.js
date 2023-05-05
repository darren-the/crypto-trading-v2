import { Context } from '../../context'
import { useContext } from 'react'

const Risk = () => {
  const { dfComponents } = useContext(Context)
  return dfComponents.risk
} 

export default Risk