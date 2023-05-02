import MainChart from './charts/MainChart'
import RsiChart from './charts/RsiChart'
import TradeChart from './charts/TradeChart'

const ChartContainer = () => {
  return (
    <div>
      <TradeChart />
      <MainChart />
      <RsiChart />
    </div>
  )
}

export default ChartContainer