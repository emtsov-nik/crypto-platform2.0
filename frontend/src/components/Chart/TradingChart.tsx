import { useEffect, useRef } from 'react'
import { createChart, IChartApi, ISeriesApi, CandlestickData, LineData } from 'lightweight-charts'
import type { IndicatorData, Timeframe } from '../../types'

interface TradingChartProps {
  data: IndicatorData[]
  symbol: string
  timeframe: Timeframe
  showIndicators?: {
    rsi?: boolean
    bb?: boolean
    sma?: boolean
    ema?: boolean
  }
}

export default function TradingChart({ data, symbol, timeframe, showIndicators }: TradingChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)

  useEffect(() => {
    if (!chartContainerRef.current || data.length === 0) return

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#ffffff' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 600,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        mode: 1,
      },
    })

    chartRef.current = chart

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    })

    candlestickSeriesRef.current = candlestickSeries

    // Prepare candlestick data
    const candleData: CandlestickData[] = data.map((item) => ({
      time: new Date(item.timestamp).getTime() / 1000,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
    }))

    candlestickSeries.setData(candleData)

    // Add indicators if requested
    if (showIndicators?.sma) {
      // SMA 7
      if (data[0]?.sma_7) {
        const sma7Series = chart.addLineSeries({
          color: '#2962FF',
          lineWidth: 1,
          title: 'SMA 7',
        })
        const sma7Data: LineData[] = data
          .filter((item) => item.sma_7 !== undefined && item.sma_7 !== null)
          .map((item) => ({
            time: new Date(item.timestamp).getTime() / 1000,
            value: item.sma_7!,
          }))
        sma7Series.setData(sma7Data)
      }

      // SMA 25
      if (data[0]?.sma_25) {
        const sma25Series = chart.addLineSeries({
          color: '#FF6D00',
          lineWidth: 1,
          title: 'SMA 25',
        })
        const sma25Data: LineData[] = data
          .filter((item) => item.sma_25 !== undefined && item.sma_25 !== null)
          .map((item) => ({
            time: new Date(item.timestamp).getTime() / 1000,
            value: item.sma_25!,
          }))
        sma25Series.setData(sma25Data)
      }

      // SMA 99
      if (data[0]?.sma_99) {
        const sma99Series = chart.addLineSeries({
          color: '#E040FB',
          lineWidth: 1,
          title: 'SMA 99',
        })
        const sma99Data: LineData[] = data
          .filter((item) => item.sma_99 !== undefined && item.sma_99 !== null)
          .map((item) => ({
            time: new Date(item.timestamp).getTime() / 1000,
            value: item.sma_99!,
          }))
        sma99Series.setData(sma99Data)
      }
    }

    // Bollinger Bands
    if (showIndicators?.bb && data[0]?.bb_upper) {
      const bbUpperSeries = chart.addLineSeries({
        color: '#9C27B0',
        lineWidth: 1,
        lineStyle: 2,
        title: 'BB Upper',
      })
      const bbUpperData: LineData[] = data
        .filter((item) => item.bb_upper !== undefined && item.bb_upper !== null)
        .map((item) => ({
          time: new Date(item.timestamp).getTime() / 1000,
          value: item.bb_upper!,
        }))
      bbUpperSeries.setData(bbUpperData)

      const bbMiddleSeries = chart.addLineSeries({
        color: '#9C27B0',
        lineWidth: 1,
        title: 'BB Middle',
      })
      const bbMiddleData: LineData[] = data
        .filter((item) => item.bb_middle !== undefined && item.bb_middle !== null)
        .map((item) => ({
          time: new Date(item.timestamp).getTime() / 1000,
          value: item.bb_middle!,
        }))
      bbMiddleSeries.setData(bbMiddleData)

      const bbLowerSeries = chart.addLineSeries({
        color: '#9C27B0',
        lineWidth: 1,
        lineStyle: 2,
        title: 'BB Lower',
      })
      const bbLowerData: LineData[] = data
        .filter((item) => item.bb_lower !== undefined && item.bb_lower !== null)
        .map((item) => ({
          time: new Date(item.timestamp).getTime() / 1000,
          value: item.bb_lower!,
        }))
      bbLowerSeries.setData(bbLowerData)
    }

    // Handle window resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    // Fit content
    chart.timeScale().fitContent()

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [data, showIndicators])

  return (
    <div className="w-full">
      <div className="mb-4">
        <h3 className="text-lg font-semibold">
          {symbol} - {timeframe}
        </h3>
      </div>
      <div ref={chartContainerRef} className="w-full" />
    </div>
  )
}
