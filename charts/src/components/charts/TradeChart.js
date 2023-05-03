import { useRef, useContext, useEffect } from 'react'
import { Context } from '../../context'
import { createChart } from 'lightweight-charts'

const TradeChart = () => {
  const chartRef = useRef()
  const { mainChart, setTradeChart } = useContext(Context)
  
  useEffect(() => {
    if (mainChart === null) return
    const chart = createChart(chartRef.current, {
      width: chartRef.current.clientWidth,
      height: chartRef.current.clientHeight,
    })
    setTradeChart(chart)
    
    // Adjust timescale to show hours and minutes
    chart.timeScale().applyOptions({
      timeVisible: true,
      shiftVisibleRangeOnNewBar: false,
    })

    // Customizing the Crosshair
    chart.applyOptions({
      crosshair: {
      mode: 0,

      // Vertical crosshair line (showing Date in Label)
      vertLine: {
        width: 8,
        color: '#C3BCDB44',
        style: 0,
        labelBackgroundColor: '#9B7DFF',
      },

      // Horizontal crosshair line (showing Price in Label)
      horzLine: {
        color: '#9B7DFF',
        labelBackgroundColor: '#9B7DFF',
      },
      },
    })

    // sync chart and TradeChart
    mainChart.timeScale().subscribeVisibleLogicalRangeChange((VLR) => {
      if (mainChart === null || chart === null || VLR === null) return
      chart.timeScale().setVisibleLogicalRange({ from: VLR.from, to: VLR.to })
    })

    // Handle resizing
    const handleResize = () => {
      chart.applyOptions({ width: chartRef.current.clientWidth })
    }
    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
    // eslint-disable-next-line
  }, [mainChart])

  return <div style={{ width: '98.5%', height: 150 }} ref={chartRef} />
}

export default TradeChart