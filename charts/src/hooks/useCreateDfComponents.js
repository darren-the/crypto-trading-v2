import { useState } from 'react'

export const useCreateDfComponents = () => {
  const [dfComponents, setDfComponents] = useState({})
  const setDfComponent = (name, newComponent) => {
    setDfComponents(oldDfComponents => ({ ...oldDfComponents, [name]: newComponent }))
  }
  return { dfComponents, setDfComponent }
}
