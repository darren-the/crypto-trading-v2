import { useRef, useContext, useEffect } from 'react'
import { Context } from '../../context'
import { createChart } from 'lightweight-charts'

const MainChart = () => {
  const chartRef = useRef()
  const { setMainChart } = useContext(Context)
  
  useEffect(() => {
    const chart = createChart(chartRef.current, {
      width: chartRef.current.clientWidth,
      height: chartRef.current.clientHeight,
    })

    setMainChart(chart)
    
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
  }, [])

  return <div style={{ width: '100%', height: 300 }} ref={chartRef} />
}

export default MainChart