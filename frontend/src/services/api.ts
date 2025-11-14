import axios from 'axios'
import type {
  SymbolListResponse,
  KlineResponse,
  IndicatorResponse,
  TickerInfo,
  PriceResponse,
  Timeframe,
  StrategyListResponse,
  StrategyCreate,
  StrategyUpdate,
  Strategy,
  AvailableStrategiesResponse,
  AvailableStrategyInfo,
  StrategyTestRequest,
  StrategyTestResponse,
  StrategyValidationRequest,
  StrategyValidationResponse,
  GenerateSignalRequest,
  GenerateSignalResponse,
  BacktestListResponse,
  BacktestCreate,
  Backtest,
  RunBacktestRequest,
  RunBacktestResponse,
  BacktestResults,
  TradeListResponse,
  EquityCurveResponse,
  BacktestProgress,
  StartBotRequest,
  BotActionResponse,
  BotStatusResponse,
  TradeHistoryResponse,
} from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Market Data API
export const marketApi = {
  // Get list of available symbols
  getSymbols: async (quote: string = 'USDT'): Promise<SymbolListResponse> => {
    const response = await api.get(`/api/market/symbols`, {
      params: { quote },
    })
    return response.data
  },

  // Get OHLCV data
  getKlines: async (
    symbol: string,
    timeframe: Timeframe = '1h',
    limit: number = 500,
    startTime?: string,
    endTime?: string
  ): Promise<KlineResponse> => {
    const response = await api.get(`/api/market/klines`, {
      params: {
        symbol,
        timeframe,
        limit,
        start_time: startTime,
        end_time: endTime,
      },
    })
    return response.data
  },

  // Get data with indicators
  getIndicators: async (
    symbol: string,
    timeframe: Timeframe = '1h',
    indicators: string[] = ['all'],
    limit: number = 500,
    startTime?: string,
    endTime?: string
  ): Promise<IndicatorResponse> => {
    const response = await api.get(`/api/market/indicators`, {
      params: {
        symbol,
        timeframe,
        indicators: indicators.join(','),
        limit,
        start_time: startTime,
        end_time: endTime,
      },
    })
    return response.data
  },

  // Get ticker info
  getTicker: async (symbol: string): Promise<TickerInfo> => {
    const response = await api.get(`/api/market/ticker/${symbol}`)
    return response.data
  },

  // Get current price
  getPrice: async (symbol: string): Promise<PriceResponse> => {
    const response = await api.get(`/api/market/price/${symbol}`)
    return response.data
  },

  // Test connection
  testConnection: async (): Promise<{ status: string }> => {
    const response = await api.get(`/api/market/test`)
    return response.data
  },
}

// Strategy API
export const strategyApi = {
  // Get available strategy classes
  getAvailableStrategies: async (): Promise<AvailableStrategiesResponse> => {
    const response = await api.get('/api/strategies/available')
    return response.data
  },

  // Get info about specific strategy class
  getAvailableStrategyInfo: async (className: string): Promise<AvailableStrategyInfo> => {
    const response = await api.get(`/api/strategies/available/${className}`)
    return response.data
  },

  // Create new strategy
  createStrategy: async (data: StrategyCreate): Promise<Strategy> => {
    const response = await api.post('/api/strategies/', data)
    return response.data
  },

  // Get all user strategies
  getStrategies: async (
    skip: number = 0,
    limit: number = 100,
    activeOnly: boolean = false
  ): Promise<StrategyListResponse> => {
    const response = await api.get('/api/strategies/', {
      params: { skip, limit, active_only: activeOnly },
    })
    return response.data
  },

  // Get specific strategy
  getStrategy: async (strategyId: number): Promise<Strategy> => {
    const response = await api.get(`/api/strategies/${strategyId}`)
    return response.data
  },

  // Update strategy
  updateStrategy: async (strategyId: number, data: StrategyUpdate): Promise<Strategy> => {
    const response = await api.put(`/api/strategies/${strategyId}`, data)
    return response.data
  },

  // Delete strategy
  deleteStrategy: async (strategyId: number): Promise<void> => {
    await api.delete(`/api/strategies/${strategyId}`)
  },

  // Toggle strategy active status
  toggleStrategyActive: async (strategyId: number): Promise<Strategy> => {
    const response = await api.post(`/api/strategies/${strategyId}/toggle`)
    return response.data
  },

  // Test strategy
  testStrategy: async (data: StrategyTestRequest): Promise<StrategyTestResponse> => {
    const response = await api.post('/api/strategies/test', data)
    return response.data
  },

  // Validate strategy parameters
  validateStrategy: async (
    data: StrategyValidationRequest
  ): Promise<StrategyValidationResponse> => {
    const response = await api.post('/api/strategies/validate', data)
    return response.data
  },

  // Generate signal
  generateSignal: async (data: GenerateSignalRequest): Promise<GenerateSignalResponse> => {
    const response = await api.post('/api/strategies/signal', data)
    return response.data
  },
}

// Backtest API
export const backtestApi = {
  // Run backtest
  runBacktest: async (data: RunBacktestRequest): Promise<RunBacktestResponse> => {
    const response = await api.post('/api/backtests/run', data)
    return response.data
  },

  // Get all backtests
  getBacktests: async (skip: number = 0, limit: number = 100, strategyId?: number): Promise<BacktestListResponse> => {
    const response = await api.get('/api/backtests/', {
      params: { skip, limit, strategy_id: strategyId },
    })
    return response.data
  },

  // Get specific backtest
  getBacktest: async (backtestId: number): Promise<Backtest> => {
    const response = await api.get(`/api/backtests/${backtestId}`)
    return response.data
  },

  // Delete backtest
  deleteBacktest: async (backtestId: number): Promise<void> => {
    await api.delete(`/api/backtests/${backtestId}`)
  },

  // Get backtest results
  getResults: async (backtestId: number): Promise<BacktestResults> => {
    const response = await api.get(`/api/backtests/${backtestId}/results`)
    return response.data
  },

  // Get backtest trades
  getTrades: async (backtestId: number): Promise<TradeListResponse> => {
    const response = await api.get(`/api/backtests/${backtestId}/trades`)
    return response.data
  },

  // Get equity curve
  getEquityCurve: async (backtestId: number): Promise<EquityCurveResponse> => {
    const response = await api.get(`/api/backtests/${backtestId}/equity`)
    return response.data
  },

  // Get backtest progress
  getProgress: async (backtestId: number): Promise<BacktestProgress> => {
    const response = await api.get(`/api/backtests/${backtestId}/progress`)
    return response.data
  },
}

// Trading API
export const tradingApi = {
  // Start live trading
  startBot: async (data: StartBotRequest): Promise<BotActionResponse> => {
    const response = await api.post('/api/trading/start', data)
    return response.data
  },

  // Stop trading bot
  stopBot: async (): Promise<BotActionResponse> => {
    const response = await api.post('/api/trading/stop')
    return response.data
  },

  // Pause trading bot
  pauseBot: async (): Promise<BotActionResponse> => {
    const response = await api.post('/api/trading/pause')
    return response.data
  },

  // Resume trading bot
  resumeBot: async (): Promise<BotActionResponse> => {
    const response = await api.post('/api/trading/resume')
    return response.data
  },

  // Get bot status
  getStatus: async (): Promise<BotStatusResponse> => {
    const response = await api.get('/api/trading/status')
    return response.data
  },

  // Get trade history
  getHistory: async (): Promise<TradeHistoryResponse> => {
    const response = await api.get('/api/trading/history')
    return response.data
  },

  // Emergency stop
  emergencyStop: async (): Promise<BotActionResponse> => {
    const response = await api.post('/api/trading/emergency-stop')
    return response.data
  },
}

// Health check
export const healthCheck = async () => {
  const response = await api.get('/api/health')
  return response.data
}

export default api
