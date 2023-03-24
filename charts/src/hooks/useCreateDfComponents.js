import { useState } from 'react'

export const useCreateDfComponents = () => {
  const [dfComponents, setDfComponents] = useState({})
  const setDfComponent = (name, newComponent) => {
    setDfComponents({ ...dfComponents, [name]: newComponent })
  }
  return { dfComponents, setDfComponent}
}
