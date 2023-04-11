import { Context } from '../../context'
import { useContext } from 'react'

const RsiProject = () => {
  const { dfComponents } = useContext(Context)
  return dfComponents.rsiproject
} 

export default RsiProject