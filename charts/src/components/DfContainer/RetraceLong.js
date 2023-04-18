import { Context } from '../../context'
import { useContext } from 'react'

const RetraceLong = () => {
  const { dfComponents } = useContext(Context)
  return dfComponents.retracelong
} 

export default RetraceLong