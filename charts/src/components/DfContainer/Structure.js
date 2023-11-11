import { Context } from '../../context'
import { useContext } from 'react'

const Structure = () => {
  const { dfComponents } = useContext(Context)
  return dfComponents.structure
} 

export default Structure