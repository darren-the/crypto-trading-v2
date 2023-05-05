export const updateRiskComponent = (name, setDfComponent, data) => {
  if (data.length === 0) return
  const displayedText = `recent_sup_top = ${data[0].recent_sup_top}, ` +
    `recent_sup_bottom = ${data[0].recent_sup_bottom}, ` +
    `risk = ${data[0].risk}`
  if (setDfComponent) setDfComponent(name, <div>{displayedText}</div>)
}
