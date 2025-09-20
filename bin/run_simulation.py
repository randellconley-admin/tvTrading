



#!/usr/bin/env python3

"""
Trading Simulation Runner
Demonstrates mplfinance, Plotly, and TA-Lib integration
Multi-Team Coordination: All Teams Working Together
"""

import sys
import os
sys.path.append('/workspace/tvTrading')

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import json
from src.analytics.technical_analyzer import TechnicalAnalyzer
from src.analytics.chart_generators import MPLFinanceChartGenerator, PlotlyInteractiveCharts

def fetch_sample_data(ticker: str = "AAPL", period: str = "6mo") -> pd.DataFrame:
    """
    Fetch sample market data for demonstration
    """
    print(f"📊 Fetching {period} data for {ticker}...")
    
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period=period, interval="1d")
        
        if data.empty:
            raise ValueError(f"No data available for {ticker}")
        
        # Ensure proper column names - yfinance returns different columns
        if len(data.columns) == 7:
            # yfinance returns: Open, High, Low, Close, Adj Close, Volume, Dividends, Stock Splits
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
        elif len(data.columns) == 6:
            # Sometimes: Open, High, Low, Close, Adj Close, Volume
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
        elif len(data.columns) == 5:
            # Already correct format
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        print(f"✅ Fetched {len(data)} trading days for {ticker}")
        return data
        
    except Exception as e:
        print(f"❌ Error fetching data for {ticker}: {e}")
        return None

def run_comprehensive_analysis(ticker: str = "AAPL"):
    """
    Run comprehensive trading analysis demonstration
    """
    print("🚀 Starting Comprehensive Trading Analysis")
    print("=" * 60)
    
    # Step 1: Fetch market data
    data = fetch_sample_data(ticker)
    if data is None:
        return False
    
    # Step 2: Technical Analysis with TA-Lib
    print(f"\n📊 Running Technical Analysis for {ticker}...")
    analyzer = TechnicalAnalyzer(data)
    indicators = analyzer.calculate_all_indicators()
    signals = analyzer.generate_trading_signals()
    
    # Step 3: Generate Static Charts with mplfinance
    print(f"\n📈 Creating Static Charts with mplfinance...")
    mpl_generator = MPLFinanceChartGenerator(data, indicators, signals)
    
    # Create main chart
    main_chart_path = mpl_generator.create_main_chart(ticker)
    
    # Create indicator subplots
    indicator_chart_path = mpl_generator.create_indicator_subplots(ticker)
    
    # Create pattern analysis chart
    pattern_chart_path = mpl_generator.create_pattern_analysis_chart(ticker)
    
    # Step 4: Generate Interactive Charts with Plotly
    print(f"\n🎨 Creating Interactive Charts with Plotly...")
    plotly_generator = PlotlyInteractiveCharts(data, indicators, signals)
    
    # Create comprehensive dashboard
    interactive_fig = plotly_generator.create_comprehensive_dashboard(ticker)
    
    # Save interactive chart
    interactive_path = plotly_generator.save_interactive_chart(interactive_fig, ticker)
    
    # Step 5: Generate Analysis Summary
    print(f"\n📋 Generating Analysis Summary...")
    latest_analysis = analyzer.get_latest_analysis()
    
    # Count signals
    buy_signals = len(signals[signals['Action'] == 'BUY'])
    sell_signals = len(signals[signals['Action'] == 'SELL'])
    hold_signals = len(signals[signals['Action'] == 'HOLD'])
    
    # Calculate performance metrics
    total_signals = buy_signals + sell_signals
    signal_frequency = total_signals / len(data) * 100 if len(data) > 0 else 0
    
    summary = {
        'ticker': ticker,
        'analysis_date': datetime.now().isoformat(),
        'data_period': {
            'start_date': data.index[0].isoformat(),
            'end_date': data.index[-1].isoformat(),
            'total_days': len(data)
        },
        'technical_indicators': {
            'total_calculated': len(indicators),
            'latest_rsi': float(indicators.get('RSI', [0])[-1]) if 'RSI' in indicators else None,
            'latest_macd': float(indicators.get('MACD', [0])[-1]) if 'MACD' in indicators else None,
            'latest_atr': float(indicators.get('ATR', [0])[-1]) if 'ATR' in indicators else None
        },
        'trading_signals': {
            'total_signals': total_signals,
            'buy_signals': buy_signals,
            'sell_signals': sell_signals,
            'hold_signals': hold_signals,
            'signal_frequency_pct': round(signal_frequency, 2)
        },
        'charts_generated': {
            'mplfinance_main': main_chart_path,
            'mplfinance_indicators': indicator_chart_path,
            'mplfinance_patterns': pattern_chart_path,
            'plotly_interactive': interactive_path
        },
        'latest_analysis': latest_analysis
    }
    
    # Save summary
    summary_path = f'/workspace/tvTrading/analysis_summary_{ticker}.json'
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    # Step 6: Generate Webhook Simulation
    print(f"\n🔗 Simulating TradingView Webhooks...")
    webhook_payloads = []
    
    for idx, row in signals.iterrows():
        if row['Action'] in ['BUY', 'SELL']:
            payload = {
                "signal": row['Action'],
                "ticker": ticker,
                "tradingMode": "Paper",
                "riskAmount": 100.0,
                "entryPrice": float(data.loc[idx, 'Close']),
                "stopLoss": float(data.loc[idx, 'Close'] * (0.98 if row['Action'] == 'BUY' else 1.02)),
                "takeProfit": float(data.loc[idx, 'Close'] * (1.05 if row['Action'] == 'BUY' else 0.95)),
                "strategy": "comprehensive_analysis",
                "timeframe": "1d",
                "timestamp": idx.isoformat(),
                "rsi": float(indicators.get('RSI', [50])[data.index.get_loc(idx)]) if 'RSI' in indicators else 50,
                "atr": float(indicators.get('ATR', [1])[data.index.get_loc(idx)]) if 'ATR' in indicators else 1
            }
            webhook_payloads.append(payload)
    
    # Save webhook payloads
    webhook_path = f'/workspace/tvTrading/webhooks/{ticker}_simulation_webhooks.json'
    os.makedirs(os.path.dirname(webhook_path), exist_ok=True)
    
    with open(webhook_path, 'w') as f:
        json.dump(webhook_payloads, f, indent=2)
    
    # Display Results
    print("\n" + "=" * 60)
    print("🎯 COMPREHENSIVE ANALYSIS COMPLETE!")
    print("=" * 60)
    print(f"📊 Ticker: {ticker}")
    print(f"📅 Period: {data.index[0].date()} to {data.index[-1].date()}")
    print(f"📈 Data Points: {len(data)} trading days")
    print(f"🔢 Technical Indicators: {len(indicators)} calculated")
    print(f"🎯 Trading Signals: {total_signals} total ({buy_signals} BUY, {sell_signals} SELL)")
    print(f"📊 Signal Frequency: {signal_frequency:.1f}% of trading days")
    
    print(f"\n📈 Latest Technical Analysis:")
    print(f"   • Price: ${latest_analysis['price']['current']:.2f}")
    print(f"   • RSI: {latest_analysis['momentum']['rsi']:.1f}")
    print(f"   • MACD: {latest_analysis['momentum']['macd']:.4f}")
    print(f"   • ATR: {latest_analysis['volatility']['atr']:.2f}")
    
    print(f"\n📊 Charts Generated:")
    print(f"   • mplfinance Main Chart: {main_chart_path}")
    print(f"   • mplfinance Indicators: {indicator_chart_path}")
    print(f"   • mplfinance Patterns: {pattern_chart_path}")
    print(f"   • Plotly Interactive: {interactive_path}")
    
    print(f"\n🔗 Webhook Simulation:")
    print(f"   • Payloads Generated: {len(webhook_payloads)}")
    print(f"   • Saved to: {webhook_path}")
    
    print(f"\n📋 Full Analysis Summary: {summary_path}")
    print("=" * 60)
    
    return True

def run_multi_ticker_analysis(tickers: list = None):
    """
    Run analysis for multiple tickers
    """
    if tickers is None:
        tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
    
    print(f"🚀 Running Multi-Ticker Analysis for {len(tickers)} stocks")
    print("=" * 80)
    
    results = {}
    
    for i, ticker in enumerate(tickers, 1):
        print(f"\n[{i}/{len(tickers)}] Processing {ticker}...")
        try:
            success = run_comprehensive_analysis(ticker)
            results[ticker] = 'SUCCESS' if success else 'FAILED'
        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")
            results[ticker] = f'ERROR: {str(e)}'
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 MULTI-TICKER ANALYSIS COMPLETE!")
    print("=" * 80)
    
    successful = sum(1 for status in results.values() if status == 'SUCCESS')
    failed = len(tickers) - successful
    
    print(f"📊 Results Summary:")
    print(f"   • Total Tickers: {len(tickers)}")
    print(f"   • Successful: {successful}")
    print(f"   • Failed: {failed}")
    
    print(f"\n📋 Individual Results:")
    for ticker, status in results.items():
        status_icon = "✅" if status == "SUCCESS" else "❌"
        print(f"   {status_icon} {ticker}: {status}")
    
    print("\n📁 All generated files are in:")
    print("   • Charts: /workspace/tvTrading/charts/")
    print("   • Webhooks: /workspace/tvTrading/webhooks/")
    print("   • Analysis: /workspace/tvTrading/analysis_summary_*.json")
    print("=" * 80)
    
    return results

def main():
    """
    Main execution function
    """
    print("🎯 Trading Automation Platform - Simulation Runner")
    print("Demonstrating TA-Lib + mplfinance + Plotly Integration")
    print("=" * 80)
    
    # Create necessary directories
    os.makedirs('/workspace/tvTrading/charts', exist_ok=True)
    os.makedirs('/workspace/tvTrading/webhooks', exist_ok=True)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'multi':
            # Run multi-ticker analysis
            tickers = sys.argv[2:] if len(sys.argv) > 2 else None
            run_multi_ticker_analysis(tickers)
        else:
            # Run single ticker analysis
            ticker = sys.argv[1].upper()
            run_comprehensive_analysis(ticker)
    else:
        # Default: run single ticker analysis for AAPL
        run_comprehensive_analysis('AAPL')
    
    print("\n🎯 Simulation complete! Check the generated files.")

if __name__ == "__main__":
    main()



