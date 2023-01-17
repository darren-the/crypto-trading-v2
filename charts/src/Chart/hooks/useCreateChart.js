import { useEffect, useState, useRef } from 'react'
import { createChart } from 'lightweight-charts'

export const useCreateChart = () => {
  const chartRef = useRef()
  const [chartState, setChartState] = useState(null)
  const [seriesState, setSeriesState] = useState(null)

  useEffect(() => {
    /* ==================== CHART OPTIONS ==================== */

    const chart = createChart(chartRef.current, {
      width: chartRef.current.clientWidth,
      height: chartRef.current.clientHeight,
    })
    setChartState(chart)

    // Adjust timescale to show hours and minutes
    chart.timeScale().applyOptions({
      timeVisible: true,
      shiftVisibleRangeOnNewBar: false,
    })
		
    // Customizing the Crosshair
    chart.applyOptions({
      crosshair: {
        // Change mode from default 'magnet' to 'normal'.
        // Allows the crosshair to move freely without snapping to datapoints
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

    /* ==================== SERIES OPTIONS ==================== */

    const series = chart.addCandlestickSeries({})
    setSeriesState(series)


    /* ==================== RESIZE HANDLING ==================== */

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

  return { chart: chartState, chartRef , series: seriesState }
}