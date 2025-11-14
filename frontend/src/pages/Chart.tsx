import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { marketApi } from '../services/api'
import TradingChart from '../components/Chart/TradingChart'
import ChartControls from '../components/Chart/ChartControls'
import type { Timeframe } from '../types'

export default function ChartPage() {
  const [symbol, setSymbol] = useState('BTC/USDT')
  const [timeframe, setTimeframe] = useState<Timeframe>('1h')
  const [indicators, setIndicators] = useState({ sma: true, bb: false })

  const indicatorList = Object.keys(indicators).filter((k) => indicators[k as keyof typeof indicators])

  const { data, isLoading, error } = useQuery({
    queryKey: ['indicators', symbol, timeframe, indicatorList],
    queryFn: () => marketApi.getIndicators(symbol, timeframe, indicatorList.length > 0 ? indicatorList : ['all'], 500),
    refetchInterval: 60000,
  })

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Trading Chart</h1>
      <ChartControls
        symbol={symbol}
        timeframe={timeframe}
        indicators={indicators}
        onSymbolChange={setSymbol}
        onTimeframeChange={setTimeframe}
        onIndicatorsChange={setIndicators}
      />
      {isLoading && <div className="text-center py-8">Loading chart data...</div>}
      {error && <div className="text-center py-8 text-red-500">Error loading data: {String(error)}</div>}
      {data && data.data && data.data.length > 0 && (
        <div className="bg-white rounded-lg shadow p-4">
          <TradingChart data={data.data} symbol={symbol} timeframe={timeframe} showIndicators={indicators} />
        </div>
      )}
    </div>
  )
}
