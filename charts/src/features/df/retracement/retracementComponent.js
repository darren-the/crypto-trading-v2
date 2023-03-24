export const updateRetracementComponent = (name, setDfComponent, data) => {
  if (data.length === 0) return
  const displayedText = `High retracement = ${Math.round(data[0].highRetracement * 100)}%, ` +
    `Low retracement = ${Math.round(data[0].lowRetracement * 100)}%`
    setDfComponent(name, <span>{displayedText}</span>)
}
