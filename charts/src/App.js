import Chart from './Chart/'
import { MainContext } from './context'
import { useState, useRef } from 'react'
import config from './config.json'

function App() {
  const [chart, setChart] = useState(null)
  const [series, setSeries] = useState(null)
  const [timeframe, setTimeframe] = useState(config.defaultTimeframe)
  const [timestamp, setTimestamp] = useState(null)
  const [truncTime, setTruncTime] = useState(null)
  const [loadMode, setLoadMode] = useState(config.loadMode.NONE)
  const [candles, setCandles] = useState([])
  const [highs, setHighs] = useState([])
  const [lows, setLows] = useState([])
  const [resistance, setResistance] = useState([])
  const [support, setSupport] = useState([])
  const [toggleHighLow, setToggleHighLow] = useState(true)
  const [toggleResSup, setToggleResSup] = useState(true)
  const [rsiChart, setRsiChart] = useState(null)
  const [rsi, setRsi] = useState([])
  const [pipelineId, setPipelineId] = useState('main')
  const [symbol, setSymbol] = useState('btcusd')
  const [retracement, setRetracement] = useState([])
  const [retracementDisplay, setRetracementDisplay] = useState('No current retracement')

  const variables = {
    mainChartRef: useRef(),
    chart,
    setChart,
    series,
    setSeries,
    timeframe,
    setTimeframe,
    timestamp,
    setTimestamp,
    truncTime,
    setTruncTime,
    loadMode,
    setLoadMode,
    candleStartTime: useRef(true),
    lastIndex: useRef(null),
    startOfDataFlag: useRef(false),
    endOfDataFlag: useRef(false),
    isLoading: useRef(false),
    candles,
    setCandles,
    initialRender: useRef(true),
    highs,
    setHighs,
    lows,
    setLows,
    resistance,
    setResistance,
    support,
    setSupport,
    toggleHighLow,
    setToggleHighLow,
    VTRChangeHandlerRef: useRef(null),
    resSupVisible: useRef(true),
    resPriceLines:useRef([]),
    supPriceLines: useRef([]),
    toggleResSup,
    setToggleResSup,
    rsiChartRef: useRef(),
    rsiChart, 
    setRsiChart,
    rsi,
    setRsi,
    pipelineId,
    setPipelineId,
    symbol,
    setSymbol,
    retracement,
    setRetracement,
    retracementDisplay,
    setRetracementDisplay,
    highLowVisible: useRef(true),
  }

  return (
    <div className="App">
      <MainContext.Provider value={variables}>
        <Chart />
      </MainContext.Provider>
    </div>
  );
}

export default App
