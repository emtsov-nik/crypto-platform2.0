// Market Data Types

export interface SymbolInfo {
  symbol: string
  baseAsset: string
  quoteAsset: string
  status: string
}

export interface SymbolListResponse {
  symbols: SymbolInfo[]
  count: number
}

export interface KlineData {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface KlineResponse {
  symbol: string
  timeframe: string
  data: KlineData[]
  count: number
}

export interface IndicatorData extends KlineData {
  rsi?: number
  bb_upper?: number
  bb_middle?: number
  bb_lower?: number
  bb_width?: number
  sma_7?: number
  sma_25?: number
  sma_99?: number
  ema_12?: number
  ema_26?: number
  macd?: number
  macd_signal?: number
  macd_diff?: number
  atr?: number
  vwap?: number
  [key: string]: any
}

export interface IndicatorResponse {
  symbol: string
  timeframe: string
  data: IndicatorData[]
  indicators: string[]
  count: number
}

export interface TickerInfo {
  symbol: string
  last: number
  bid: number
  ask: number
  high: number
  low: number
  volume: number
  quoteVolume: number
  change?: number
  percentage?: number
  timestamp: number
}

export interface PriceResponse {
  symbol: string
  price: number
}

// Chart Types
export type Timeframe = '1m' | '5m' | '15m' | '1h' | '4h' | '1d' | '1w'

export interface ChartSettings {
  symbol: string
  timeframe: Timeframe
  indicators: string[]
}

// Strategy Types

export interface StrategyBase {
  name: string
  description?: string
  class_name: string
  params: Record<string, any>
  is_active: boolean
}

export interface Strategy extends StrategyBase {
  id: number
  created_at: string
  updated_at: string
}

export interface StrategyCreate extends StrategyBase {}

export interface StrategyUpdate {
  name?: string
  description?: string
  params?: Record<string, any>
  is_active?: boolean
}

export interface StrategyListResponse {
  strategies: Strategy[]
  total: number
}

// Strategy Metadata Types

export interface StrategyMetadata {
  name: string
  class_name: string
  description?: string
  indicators: string[]
  timeframes: string[]
  risk_level?: string
  strategy_type?: string
  author?: string
  version?: string
  default_params: Record<string, any>
}

export interface AvailableStrategyInfo {
  name: string
  class_name: string
  metadata: StrategyMetadata
  default_params: Record<string, any>
  doc: string
}

export interface AvailableStrategiesResponse {
  strategies: AvailableStrategyInfo[]
  total: number
}

// Strategy Testing Types

export interface StrategyTestRequest {
  class_name: string
  params: Record<string, any>
  symbol?: string
  timeframe?: string
  limit?: number
}

export interface SignalInfo {
  timestamp: string
  signal: string
  price: number
  indicators: Record<string, any>
}

export interface StrategyTestResponse {
  success: boolean
  message: string
  signals: SignalInfo[]
  total_signals: number
  long_signals: number
  short_signals: number
  close_signals: number
}

// Strategy Validation Types

export interface StrategyValidationRequest {
  class_name: string
  params: Record<string, any>
}

export interface StrategyValidationResponse {
  valid: boolean
  errors: string[]
  warnings: string[]
}

// Signal Generation Types

export interface GenerateSignalRequest {
  strategy_id: number
  symbol?: string
  timeframe?: string
}

export interface GenerateSignalResponse {
  strategy_id: number
  strategy_name: string
  symbol: string
  timeframe: string
  signal?: string
  timestamp: string
  current_price: number
  indicators: Record<string, any>
  message: string
}

// Backtest Types

export interface BacktestBase {
  strategy_id: number
  symbol: string
  timeframe: string
  start_date?: string
  end_date?: string
  initial_capital: number
  params: Record<string, any>
}

export interface Backtest extends BacktestBase {
  id: number
  status: string  // 'pending', 'running', 'completed', 'failed'
  created_at: string
  updated_at: string
  completed_at?: string

  // Results
  final_capital?: number
  total_pnl?: number
  total_pnl_percent?: number
  total_trades?: number
  winning_trades?: number
  losing_trades?: number
  win_rate?: number
  profit_factor?: number
  max_drawdown?: number
  max_drawdown_percent?: number
  sharpe_ratio?: number
  results?: Record<string, any>
}

export interface BacktestCreate extends BacktestBase {}

export interface BacktestListResponse {
  backtests: Backtest[]
  total: number
}

// Trade Types

export interface TradeInfo {
  id: number
  entry_time: string
  exit_time: string
  side: string  // 'long' or 'short'
  entry_price: number
  exit_price: number
  quantity: number
  pnl: number
  pnl_percent: number
  fees: number
  exit_reason: string
  steps: number
}

export interface TradeListResponse {
  trades: TradeInfo[]
  total: number
}

// Results Types

export interface BacktestMetrics {
  symbol: string
  initial_capital: number
  final_capital: number
  total_pnl: number
  total_pnl_percent: number
  total_trades: number
  winning_trades: number
  losing_trades: number
  win_rate: number
  profit_factor: number
  max_drawdown: number
  max_drawdown_percent: number
  sharpe_ratio: number
  avg_trade_pnl: number
  avg_win: number
  avg_loss: number
  largest_win: number
  largest_loss: number
}

export interface BacktestResults extends BacktestMetrics {
  trades: TradeInfo[]
  equity_curve: number[]
  timestamps: string[]
}

// Progress Types

export interface BacktestProgress {
  backtest_id: number
  status: string
  current: number
  total: number
  message: string
}

// Run Backtest Types

export interface RunBacktestRequest {
  strategy_id: number
  symbol?: string
  timeframe?: string
  start_date?: string
  end_date?: string
  initial_capital?: number
  fee_rate?: number
  slippage?: number
}

export interface RunBacktestResponse {
  backtest_id: number
  status: string
  message: string
  task_id?: string
}

// Equity Curve Types

export interface EquityCurveResponse {
  timestamps: string[]
  equity: number[]
}

// Comparison Types

export interface BacktestComparisonItem {
  id: number
  strategy_id: number
  symbol: string
  timeframe: string
  total_pnl_percent?: number
  win_rate?: number
  profit_factor?: number
  max_drawdown_percent?: number
  sharpe_ratio?: number
  total_trades?: number
}

export interface BacktestComparisonResponse {
  backtests: BacktestComparisonItem[]
  metrics: string[]
}

// Live Trading Types

export interface StartBotRequest {
  strategy_id: number
  symbol?: string
  timeframe?: string
  capital: number
  max_position_size_usd: number
  max_daily_loss_percent: number
  max_daily_trades: number
}

export interface BotActionResponse {
  success: boolean
  message: string
  status?: string
}

export interface PositionInfo {
  side: string
  entry_price: number
  quantity: number
  current_price?: number
  pnl?: number
  pnl_percent?: number
  entry_time: string
  steps: number
  tp_price?: number
  sl_price?: number
}

export interface SafetyStatus {
  emergency_stopped: boolean
  open_positions_count: number
  daily_trades_count: number
  daily_pnl: number
  can_trade: boolean
  warnings: string[]
}

export interface BotStatusResponse {
  status: string  // 'stopped', 'starting', 'running', 'paused'
  position?: PositionInfo
  capital: number
  total_pnl: number
  total_pnl_percent: number
  total_trades: number
  safety_status: SafetyStatus
  uptime?: number
}

export interface TradeHistoryItem {
  entry_time: string
  exit_time: string
  side: string
  entry_price: number
  exit_price: number
  quantity: number
  pnl: number
  pnl_percent: number
  exit_reason: string
}

export interface TradeHistoryResponse {
  trades: TradeHistoryItem[]
  total: number
  total_pnl: number
}
