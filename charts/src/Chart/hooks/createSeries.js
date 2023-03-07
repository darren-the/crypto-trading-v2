import { useContext, useEffect } from 'react'
import { MainContext } from '../../context'


export const useCreateSeries = () => {
  const { chart, rsiChart, setSeries } = useContext(MainContext)

  useEffect(() => {
    if (chart == null || rsiChart == null) return

    const candleSeries = chart.addCandlestickSeries({})

    const highSeries = chart.addCandlestickSeries({})
    highSeries.applyOptions({
      wickUpColor: '#3674d9',
      upColor: '#3674d9',
      wickDownColor: '#3674d9',
      downColor: '#3674d9',
      borderVisible: false,
      priceLineVisible: false,
    })

    const lowSeries = chart.addCandlestickSeries({})
    lowSeries.applyOptions({
      wickUpColor: '#fccb19',
      upColor: '#fccb19',
      wickDownColor: '#fccb19',
      downColor: '#fccb19',
      borderVisible: false,
      priceLineVisible: false,
    })

    const rsiSeries = rsiChart.addLineSeries({})
    rsiSeries.applyOptions({
      lineWidth: 2,
    })

    // 70 rsi bound
    rsiSeries.createPriceLine({
      price: 70,
      color: '#000000',
      lineWidth: 2,
      lineStyle: 2,
    })

    // 30 rsi bound
    rsiSeries.createPriceLine({
      price: 30,
      color: '#000000',
      lineWidth: 2,
      lineStyle: 2,
    })

    setSeries({ candleSeries, highSeries, lowSeries, rsiSeries })
    
    // eslint-disable-next-line
  }, [chart, rsiChart])
}