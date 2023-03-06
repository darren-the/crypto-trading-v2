import { useContext, useEffect } from 'react'
import { MainContext } from '../../context'
import { createChart } from 'lightweight-charts'


export const useCreateChart = () => {
  const {
    chart,
    rsiChart,
    mainChartRef,
    setChart,
    rsiChartRef,
    setRsiChart,
  } = useContext(MainContext)

  const charts = [
    [mainChartRef, setChart],
    [rsiChartRef, setRsiChart],
  ]

  useEffect(() => {
    charts.forEach(([chartRef, setChart]) => {

      const chart = createChart(chartRef.current, {
        width: chartRef.current.clientWidth,
        height: chartRef.current.clientHeight,
      })
      setChart(chart)

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

      /* ==================== RESIZE HANDLING ==================== */

      const handleResize = () => {
        chart.applyOptions({ width: chartRef.current.clientWidth })
      }
      window.addEventListener('resize', handleResize)
      return () => {
        window.removeEventListener('resize', handleResize)
        chart.remove()
      }
    })

    // eslint-disable-next-line
  }, [])

  useEffect(() => {
    if (chart == null || rsiChart == null) return

    // sync chart and rsiChart
    chart.timeScale().subscribeVisibleLogicalRangeChange((VLR) => {
      rsiChart.timeScale().setVisibleLogicalRange({ from: VLR.from, to: VLR.to })
    })

    // CURRENTLY DISABLED - creates too much lag
    // rsiChart.timeScale().subscribeVisibleLogicalRangeChange((VLR) => {
    //   chart.timeScale().setVisibleLogicalRange({ from: VLR.from, to: VLR.to })
    // })
  }, [chart, rsiChart])
}