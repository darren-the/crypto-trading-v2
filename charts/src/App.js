import { useState } from 'react'
import { Context } from './context'
import { useCreateSeries } from './hooks/useCreateSeries'
import ChartContainer from './components/ChartContainer'
import DisplayControls from './components/DisplayControls/DisplayControls'
import { useCreateDfComponents } from './hooks/useCreateDfComponents'
import DfContainer from './components/DfContainer/DfContainer'

const App = () => {
  const [mainChart, setMainChart] = useState(null)
  const [rsiChart, setRsiChart] = useState(null)
  const [tradeChart, setTradeChart] = useState(null)
  const variables = {
    mainChart,
    setMainChart,
    rsiChart,
    setRsiChart,
    tradeChart,
    setTradeChart,
    series: useCreateSeries(mainChart, rsiChart, tradeChart),
    ...useCreateDfComponents(),
  }

  return (
    <div className="App" style={{ height: '100vh' }}>
      <Context.Provider value={variables}>
        <ChartContainer />
        <div style={{ display: 'flex', width: '100%' }}>
          <DisplayControls />
          <DfContainer />
        </div>
      </Context.Provider>
    </div>
  );
}

export default App;
