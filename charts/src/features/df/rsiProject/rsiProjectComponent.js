export const updateRsiprojectComponent = (name, setDfComponent, data) => {
    if (data.length === 0) return
    const displayedText = `30 rsi projection = ${data[0].priceProjection}`
    if (setDfComponent) setDfComponent(name, <div>{displayedText}</div>)
  }
  