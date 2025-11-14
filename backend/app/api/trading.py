"""
  WARNING: These endpoints control REAL MONEY trading  
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.trading import (
    StartBotRequest,
    BotStatusResponse,
    BotActionResponse,
    TradeHistoryResponse
)

router = APIRouter()

# Global bot instance (in production, use proper state management)
_active_bot = None


@router.post("/start", response_model=BotActionResponse)
async def start_trading(
    request: StartBotRequest,
    db: Session = Depends(get_db)
):
    """
    =¨ START LIVE TRADING =¨

    This endpoint starts real trading with real money.
    Make sure you understand the risks!
    """
    global _active_bot

    try:
        if _active_bot and _active_bot.status.value == 'running':
            return BotActionResponse(
                success=False,
                message="Bot is already running"
            )

        # Import here to avoid circular imports
        from app.services.strategy_loader import get_strategy_loader
        from app.models.strategy import Strategy
        from app.trading.live_trading_engine import LiveTradingEngine
        from app.trading.safety_manager import SafetyLimits
        import ccxt

        # Get strategy
        strategy_model = db.query(Strategy).filter(Strategy.id == request.strategy_id).first()
        if not strategy_model:
            raise HTTPException(status_code=404, detail="Strategy not found")

        loader = get_strategy_loader()
        strategy = loader.get_strategy(strategy_model.class_name, strategy_model.params)

        if not strategy:
            raise HTTPException(status_code=400, detail="Failed to load strategy")

        # Create exchange (testnet recommended for testing!)
        exchange = ccxt.binance({
            'apiKey': 'YOUR_API_KEY',  # Should come from config
            'secret': 'YOUR_SECRET',
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}  # or 'spot'
        })

        # Safety limits
        limits = SafetyLimits(
            max_position_size_usd=request.max_position_size_usd,
            max_daily_loss_percent=request.max_daily_loss_percent,
            max_daily_trades=request.max_daily_trades
        )

        # Create bot
        _active_bot = LiveTradingEngine(
            strategy=strategy,
            exchange=exchange,
            symbol=request.symbol,
            timeframe=request.timeframe,
            capital=request.capital,
            safety_limits=limits
        )

        # Start bot
        await _active_bot.start()

        return BotActionResponse(
            success=True,
            message="Trading bot started",
            status="running"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", response_model=BotActionResponse)
async def stop_trading():
    """Stop the trading bot"""
    global _active_bot

    if not _active_bot:
        return BotActionResponse(
            success=False,
            message="No active bot"
        )

    try:
        await _active_bot.stop()
        return BotActionResponse(
            success=True,
            message="Trading bot stopped",
            status="stopped"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pause", response_model=BotActionResponse)
async def pause_trading():
    """Pause the trading bot"""
    global _active_bot

    if not _active_bot:
        return BotActionResponse(success=False, message="No active bot")

    try:
        await _active_bot.pause()
        return BotActionResponse(success=True, message="Bot paused", status="paused")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resume", response_model=BotActionResponse)
async def resume_trading():
    """Resume the trading bot"""
    global _active_bot

    if not _active_bot:
        return BotActionResponse(success=False, message="No active bot")

    try:
        await _active_bot.resume()
        return BotActionResponse(success=True, message="Bot resumed", status="running")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=BotStatusResponse)
async def get_bot_status():
    """Get current bot status"""
    global _active_bot

    if not _active_bot:
        raise HTTPException(status_code=404, detail="No active bot")

    status = _active_bot.get_status()
    return BotStatusResponse(**status)


@router.get("/history", response_model=TradeHistoryResponse)
async def get_trade_history():
    """Get trade history"""
    global _active_bot

    if not _active_bot:
        raise HTTPException(status_code=404, detail="No active bot")

    trades = _active_bot.trades_history
    total_pnl = sum(t['pnl'] for t in trades)

    return TradeHistoryResponse(
        trades=[{
            **t,
            'entry_time': t['entry_time'].isoformat(),
            'exit_time': t['exit_time'].isoformat()
        } for t in trades],
        total=len(trades),
        total_pnl=total_pnl
    )


@router.post("/emergency-stop", response_model=BotActionResponse)
async def emergency_stop():
    """
    =¨ EMERGENCY STOP =¨

    Immediately stops all trading and closes positions
    """
    global _active_bot

    if not _active_bot:
        return BotActionResponse(success=False, message="No active bot")

    try:
        _active_bot.safety.trigger_emergency_stop("Manual emergency stop")
        await _active_bot.stop()

        return BotActionResponse(
            success=True,
            message="EMERGENCY STOP activated",
            status="stopped"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
