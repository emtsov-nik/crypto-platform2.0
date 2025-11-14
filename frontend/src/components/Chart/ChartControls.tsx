import { useState } from 'react'
import type { Timeframe } from '../../types'

interface ChartControlsProps {
  symbol: string
  timeframe: Timeframe
  indicators: { rsi?: boolean; bb?: boolean; sma?: boolean; ema?: boolean }
  onSymbolChange: (symbol: string) => void
  onTimeframeChange: (timeframe: Timeframe) => void
  onIndicatorsChange: (indicators: any) => void
}

const TIMEFRAMES: Timeframe[] = ['1m', '5m', '15m', '1h', '4h', '1d', '1w']
const POPULAR_SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT']

export default function ChartControls(props: ChartControlsProps) {
  const [customSymbol, setCustomSymbol] = useState(props.symbol)

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Trading Pair</label>
          <select value={props.symbol} onChange={(e) => props.onSymbolChange(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-md">
            {POPULAR_SYMBOLS.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Timeframe</label>
          <div className="grid grid-cols-4 gap-2">
            {TIMEFRAMES.map(tf => (
              <button key={tf} onClick={() => props.onTimeframeChange(tf)}
                className={`px-3 py-2 rounded-md text-sm font-medium ${props.timeframe === tf ? 'bg-blue-500 text-white' : 'bg-gray-100'}`}>
                {tf}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Indicators</label>
          <div className="space-y-2">
            <label className="flex items-center">
              <input type="checkbox" checked={props.indicators.sma} onChange={(e) => props.onIndicatorsChange({ ...props.indicators, sma: e.target.checked })} className="mr-2" />
              <span className="text-sm">SMA</span>
            </label>
            <label className="flex items-center">
              <input type="checkbox" checked={props.indicators.bb} onChange={(e) => props.onIndicatorsChange({ ...props.indicators, bb: e.target.checked })} className="mr-2" />
              <span className="text-sm">Bollinger Bands</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  )
}
