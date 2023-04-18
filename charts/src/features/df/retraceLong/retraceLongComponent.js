export const updateRetracelongComponent = (name, setDfComponent, data) => {
    if (data.length === 0) return
    const displayedText = `Retracement timeframe = ${data[0].retracementTimeframe}, ` +
      `High retracement = ${Math.round(data[0].highRetracement * 100)}%, ` +
      `Oversold timeframe = ${data[0].oversoldTimeframe}`
    if (setDfComponent) setDfComponent(name, <div>{displayedText}</div>)
  }
  