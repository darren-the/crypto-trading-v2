export const updateStructureComponent = (name, setDfComponent, data) => {
  if (data.length === 0) return
  const displayedText = `Structure top break = ${data[0].structTopBreak}, ` +
    `Structure bottom break = ${data[0].structBottomBreak}`
  if (setDfComponent) setDfComponent(name, <div>{displayedText}</div>)
}
  