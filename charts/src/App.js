import Chart from './Chart/'
import { MainContext } from './context'
import { useState, useRef } from 'react'
import config from './config.json'
import { Candles } from './Chart/features/candles'

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

  // ====== LIST ALL FEATURES HERE ======
  const featureClasses = [
    Candles,
  ]
  // ====================================

  const [featureState, setFeatureState] = useState(Object.fromEntries(featureClasses.map(featureClass => [featureClass.name, []])))
  
  const context = {
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
    liveRef: useRef(true),
    liveIndex: useRef(0),
    liveCandles: useRef([]),

    // new stuff
  }
  context.features = Object.fromEntries(featureClasses.map(featureClass => [featureClass.name, new featureClass({ context, featureState, setFeatureState} )]))

  return (
    <div className="App">
      <MainContext.Provider value={context}>
        <Chart />
      </MainContext.Provider>
    </div>
  );
}

export default App
