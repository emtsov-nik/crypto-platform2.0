import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { tradingApi, strategyApi } from '../services/api'
import type { StartBotRequest } from '../types'

export default function LiveTradingPage() {
  const queryClient = useQueryClient()
  const [showStartForm, setShowStartForm] = useState(false)
  const [formData, setFormData] = useState<StartBotRequest>({
    strategy_id: 0,
    symbol: 'BTC/USDT',
    timeframe: '1h',
    capital: 1000,
    max_position_size_usd: 100,
    max_daily_loss_percent: 5,
    max_daily_trades: 10,
  })

  // Fetch strategies
  const { data: strategiesData } = useQuery({
    queryKey: ['strategies'],
    queryFn: () => strategyApi.getStrategies(),
  })

  // Fetch bot status (poll every 2 seconds when bot is active)
  const { data: statusData, error: statusError } = useQuery({
    queryKey: ['bot-status'],
    queryFn: () => tradingApi.getStatus(),
    refetchInterval: 2000,
    retry: false,
  })

  // Fetch trade history
  const { data: historyData } = useQuery({
    queryKey: ['trade-history'],
    queryFn: () => tradingApi.getHistory(),
    enabled: !!statusData && statusData.status !== 'stopped',
    refetchInterval: 5000,
  })

  // Start bot mutation
  const startMutation = useMutation({
    mutationFn: (data: StartBotRequest) => tradingApi.startBot(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bot-status'] })
      setShowStartForm(false)
      alert(' Trading bot started!')
    },
    onError: (error: any) => {
      alert(`L Error: ${error.response?.data?.detail || error.message}`)
    },
  })

  // Stop bot mutation
  const stopMutation = useMutation({
    mutationFn: () => tradingApi.stopBot(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bot-status'] })
      alert(' Bot stopped')
    },
  })

  // Pause bot mutation
  const pauseMutation = useMutation({
    mutationFn: () => tradingApi.pauseBot(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bot-status'] })
    },
  })

  // Resume bot mutation
  const resumeMutation = useMutation({
    mutationFn: () => tradingApi.resumeBot(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bot-status'] })
    },
  })

  // Emergency stop mutation
  const emergencyStopMutation = useMutation({
    mutationFn: () => tradingApi.emergencyStop(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bot-status'] })
      alert('=� EMERGENCY STOP ACTIVATED')
    },
  })

  const handleStartBot = () => {
    if (!formData.strategy_id) {
      alert('Please select a strategy')
      return
    }

    const confirmed = confirm(
      '� WARNING: This will start LIVE TRADING with REAL MONEY!\n\n' +
      `Capital: $${formData.capital}\n` +
      `Symbol: ${formData.symbol}\n` +
      `Max Position: $${formData.max_position_size_usd}\n` +
      `Max Daily Loss: ${formData.max_daily_loss_percent}%\n\n` +
      'Are you sure you want to continue?'
    )

    if (confirmed) {
      startMutation.mutate(formData)
    }
  }

  const handleStop = () => {
    if (confirm('Stop the trading bot?')) {
      stopMutation.mutate()
    }
  }

  const handleEmergencyStop = () => {
    if (confirm('=� EMERGENCY STOP: This will immediately stop all trading and close positions. Continue?')) {
      emergencyStopMutation.mutate()
    }
  }

  const botActive = statusData && statusData.status !== 'stopped'
  const hasError = statusError !== null

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Live Trading</h1>
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          � <strong>WARNING:</strong> This page controls REAL MONEY trading. Use with extreme caution!
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bot Control Panel */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Bot Control</h2>

          {hasError && !botActive && (
            <div className="mb-4 p-4 bg-gray-100 border border-gray-300 rounded">
              <p className="text-gray-600 text-center">No active bot</p>
              <button
                onClick={() => setShowStartForm(true)}
                className="mt-3 w-full px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                Start New Bot
              </button>
            </div>
          )}

          {showStartForm && !botActive && (
            <div className="mb-4 p-4 bg-blue-50 border border-blue-300 rounded">
              <h3 className="font-semibold mb-3">Start Live Trading Bot</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-1">Strategy</label>
                  <select
                    value={formData.strategy_id}
                    onChange={(e) => setFormData({ ...formData, strategy_id: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded"
                  >
                    <option value={0}>Select a strategy...</option>
                    {strategiesData?.strategies.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name} ({s.class_name})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium mb-1">Symbol</label>
                    <input
                      type="text"
                      value={formData.symbol}
                      onChange={(e) => setFormData({ ...formData, symbol: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Timeframe</label>
                    <select
                      value={formData.timeframe}
                      onChange={(e) => setFormData({ ...formData, timeframe: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded"
                    >
                      {['1m', '5m', '15m', '1h', '4h', '1d'].map((tf) => (
                        <option key={tf} value={tf}>{tf}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Capital (USD)</label>
                  <input
                    type="number"
                    value={formData.capital}
                    onChange={(e) => setFormData({ ...formData, capital: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded"
                  />
                </div>

                <div className="border-t pt-3">
                  <h4 className="text-sm font-semibold mb-2">Safety Limits</h4>

                  <div className="space-y-2">
                    <div>
                      <label className="block text-xs font-medium mb-1">Max Position Size (USD)</label>
                      <input
                        type="number"
                        value={formData.max_position_size_usd}
                        onChange={(e) => setFormData({ ...formData, max_position_size_usd: Number(e.target.value) })}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium mb-1">Max Daily Loss (%)</label>
                      <input
                        type="number"
                        value={formData.max_daily_loss_percent}
                        onChange={(e) => setFormData({ ...formData, max_daily_loss_percent: Number(e.target.value) })}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                        step="0.1"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium mb-1">Max Daily Trades</label>
                      <input
                        type="number"
                        value={formData.max_daily_trades}
                        onChange={(e) => setFormData({ ...formData, max_daily_trades: Number(e.target.value) })}
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={handleStartBot}
                    disabled={startMutation.isPending}
                    className="flex-1 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-400"
                  >
                    {startMutation.isPending ? 'Starting...' : '=� Start Trading'}
                  </button>
                  <button
                    onClick={() => setShowStartForm(false)}
                    className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          )}

          {botActive && (
            <>
              {/* Status Display */}
              <div className="mb-4 p-4 bg-green-50 border border-green-300 rounded">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <div className="text-lg font-bold">
                      Status: <span className="text-green-600">{statusData.status.toUpperCase()}</span>
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      Capital: ${statusData.capital.toFixed(2)} |
                      Total PnL: <span className={statusData.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                        ${statusData.total_pnl.toFixed(2)} ({statusData.total_pnl_percent.toFixed(2)}%)
                      </span> |
                      Trades: {statusData.total_trades}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {statusData.status === 'running' && (
                      <button
                        onClick={() => pauseMutation.mutate()}
                        disabled={pauseMutation.isPending}
                        className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-yellow-600 text-sm"
                      >
                        � Pause
                      </button>
                    )}
                    {statusData.status === 'paused' && (
                      <button
                        onClick={() => resumeMutation.mutate()}
                        disabled={resumeMutation.isPending}
                        className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                      >
                        � Resume
                      </button>
                    )}
                    <button
                      onClick={handleStop}
                      disabled={stopMutation.isPending}
                      className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm"
                    >
                      � Stop
                    </button>
                  </div>
                </div>

                {/* Current Position */}
                {statusData.position && (
                  <div className="p-3 bg-white border border-gray-300 rounded">
                    <h4 className="font-semibold text-sm mb-2">Current Position</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>Side: <span className="font-medium">{statusData.position.side.toUpperCase()}</span></div>
                      <div>Entry: ${statusData.position.entry_price.toFixed(2)}</div>
                      <div>Quantity: {statusData.position.quantity.toFixed(6)}</div>
                      <div>Steps: {statusData.position.steps}</div>
                      {statusData.position.current_price && (
                        <>
                          <div>Current: ${statusData.position.current_price.toFixed(2)}</div>
                          <div>
                            PnL: <span className={statusData.position.pnl && statusData.position.pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                              ${statusData.position.pnl?.toFixed(2)} ({statusData.position.pnl_percent?.toFixed(2)}%)
                            </span>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                )}

                {/* Safety Status */}
                <div className="mt-3 p-3 bg-white border border-gray-300 rounded">
                  <h4 className="font-semibold text-sm mb-2">Safety Status</h4>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>Open Positions: {statusData.safety_status.open_positions_count}</div>
                    <div>Daily Trades: {statusData.safety_status.daily_trades_count}</div>
                    <div>Daily PnL: <span className={statusData.safety_status.daily_pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                      ${statusData.safety_status.daily_pnl.toFixed(2)}
                    </span></div>
                    <div>Can Trade: {statusData.safety_status.can_trade ? '' : 'L'}</div>
                  </div>
                  {statusData.safety_status.warnings.length > 0 && (
                    <div className="mt-2 text-xs text-orange-600">
                      � {statusData.safety_status.warnings.join(', ')}
                    </div>
                  )}
                </div>
              </div>

              {/* Emergency Stop Button */}
              <div className="mb-4">
                <button
                  onClick={handleEmergencyStop}
                  disabled={emergencyStopMutation.isPending}
                  className="w-full px-4 py-3 bg-red-600 text-white rounded hover:bg-red-700 font-bold"
                >
                  =� EMERGENCY STOP
                </button>
                <p className="text-xs text-gray-600 text-center mt-1">
                  Immediately stops all trading and closes positions
                </p>
              </div>
            </>
          )}
        </div>

        {/* Trade History */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Trade History</h2>

          {historyData && historyData.trades.length > 0 ? (
            <>
              <div className="mb-4 p-3 bg-gray-50 rounded">
                <div className="text-sm">
                  <div>Total Trades: {historyData.total}</div>
                  <div className={`font-bold ${historyData.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    Total PnL: ${historyData.total_pnl.toFixed(2)}
                  </div>
                </div>
              </div>

              <div className="space-y-2 max-h-96 overflow-y-auto">
                {historyData.trades.slice(0, 20).map((trade, idx) => (
                  <div key={idx} className="p-2 border border-gray-200 rounded text-xs">
                    <div className="flex justify-between mb-1">
                      <span className="font-medium">{trade.side.toUpperCase()}</span>
                      <span className={trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                        ${trade.pnl.toFixed(2)} ({trade.pnl_percent.toFixed(2)}%)
                      </span>
                    </div>
                    <div className="text-gray-600">
                      Entry: ${trade.entry_price.toFixed(2)} � Exit: ${trade.exit_price.toFixed(2)}
                    </div>
                    <div className="text-gray-500 text-xs">
                      {trade.exit_reason}
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="text-gray-500 text-center py-8">
              {botActive ? 'No trades yet' : 'Start bot to see trades'}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
