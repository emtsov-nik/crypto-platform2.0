import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { backtestApi, strategyApi } from '../services/api'
import type { RunBacktestRequest } from '../types'

export default function BacktestPage() {
  const queryClient = useQueryClient()
  const [selectedBacktest, setSelectedBacktest] = useState<number | null>(null)
  const [formData, setFormData] = useState<RunBacktestRequest>({
    strategy_id: 0,
    symbol: 'BTC/USDT',
    timeframe: '1h',
    initial_capital: 10000,
    fee_rate: 0.001,
    slippage: 0.0005,
  })

  // Fetch strategies
  const { data: strategiesData } = useQuery({
    queryKey: ['strategies'],
    queryFn: () => strategyApi.getStrategies(),
  })

  // Fetch backtests
  const { data: backtestsData, isLoading: backtestsLoading } = useQuery({
    queryKey: ['backtests'],
    queryFn: () => backtestApi.getBacktests(),
  })

  // Fetch backtest results
  const { data: resultsData } = useQuery({
    queryKey: ['backtest-results', selectedBacktest],
    queryFn: () => backtestApi.getResults(selectedBacktest!),
    enabled: !!selectedBacktest,
  })

  // Run backtest mutation
  const runMutation = useMutation({
    mutationFn: (data: RunBacktestRequest) => backtestApi.runBacktest(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backtests'] })
      alert('Backtest started!')
    },
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => backtestApi.deleteBacktest(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['backtests'] })
      if (selectedBacktest) setSelectedBacktest(null)
    },
  })

  const handleRunBacktest = () => {
    if (!formData.strategy_id) {
      alert('Please select a strategy')
      return
    }
    runMutation.mutate(formData)
  }

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Backtesting</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Run Backtest Form */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Run New Backtest</h2>
          <div className="space-y-4">
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

            <div>
              <label className="block text-sm font-medium mb-1">Initial Capital</label>
              <input
                type="number"
                value={formData.initial_capital}
                onChange={(e) => setFormData({ ...formData, initial_capital: Number(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded"
              />
            </div>

            <button
              onClick={handleRunBacktest}
              disabled={runMutation.isPending || !formData.strategy_id}
              className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
            >
              {runMutation.isPending ? 'Starting...' : 'Run Backtest'}
            </button>
          </div>
        </div>

        {/* Backtests List */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Backtests</h2>
          {backtestsLoading ? (
            <div>Loading...</div>
          ) : backtestsData?.backtests.length === 0 ? (
            <div className="text-gray-500 text-center py-8">No backtests yet</div>
          ) : (
            <div className="space-y-2">
              {backtestsData?.backtests.map((bt) => (
                <div
                  key={bt.id}
                  className={`p-3 border rounded cursor-pointer hover:bg-gray-50 ${
                    selectedBacktest === bt.id ? 'border-blue-500' : ''
                  }`}
                  onClick={() => setSelectedBacktest(bt.id)}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium">
                        {bt.symbol} - {bt.timeframe}
                      </div>
                      <div className="text-sm text-gray-600">
                        Status: {bt.status}
                      </div>
                      {bt.status === 'completed' && (
                        <div className="text-sm">
                          PnL: {bt.total_pnl_percent?.toFixed(2)}% | Trades: {bt.total_trades}
                        </div>
                      )}
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        if (confirm('Delete this backtest?')) {
                          deleteMutation.mutate(bt.id)
                        }
                      }}
                      className="text-red-500 hover:text-red-700 text-sm"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Results Panel */}
      {selectedBacktest && resultsData && (
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Results</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-gray-600">Total PnL</div>
              <div className={`text-2xl font-bold ${resultsData.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                ${resultsData.total_pnl.toFixed(2)} ({resultsData.total_pnl_percent.toFixed(2)}%)
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Win Rate</div>
              <div className="text-2xl font-bold">{resultsData.win_rate.toFixed(2)}%</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Total Trades</div>
              <div className="text-2xl font-bold">{resultsData.total_trades}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Max Drawdown</div>
              <div className="text-2xl font-bold text-red-600">{resultsData.max_drawdown_percent.toFixed(2)}%</div>
            </div>
          </div>

          {/* Trades Table (?5@2K5 10) */}
          <div className="mt-6">
            <h3 className="text-lg font-semibold mb-3">Trades (showing first 10 of {resultsData.trades.length})</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full border">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 border">Side</th>
                    <th className="px-4 py-2 border">Entry</th>
                    <th className="px-4 py-2 border">Exit</th>
                    <th className="px-4 py-2 border">PnL</th>
                    <th className="px-4 py-2 border">PnL %</th>
                  </tr>
                </thead>
                <tbody>
                  {resultsData.trades.slice(0, 10).map((trade) => (
                    <tr key={trade.id}>
                      <td className="px-4 py-2 border text-sm">{trade.side}</td>
                      <td className="px-4 py-2 border text-sm">${trade.entry_price.toFixed(2)}</td>
                      <td className="px-4 py-2 border text-sm">${trade.exit_price.toFixed(2)}</td>
                      <td className={`px-4 py-2 border text-sm font-medium ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        ${trade.pnl.toFixed(2)}
                      </td>
                      <td className={`px-4 py-2 border text-sm font-medium ${trade.pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {trade.pnl_percent.toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
