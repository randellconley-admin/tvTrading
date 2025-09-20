

"""
Trading Simulation & Visualization Platform
Using mplfinance, Plotly, and TA-Lib to simulate Pine Script functionality
Multi-Team Coordination: Trading Analytics Team Lead Implementation
"""

import pandas as pd
import numpy as np
import yfinance as yf
import mplfinance as mpf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import talib
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class TradingSimulator:
    """
    Core trading simulation engine using TA-Lib for indicators
    and mplfinance/Plotly for visualization
    """
    
    def __init__(self, tickers: List[str] = None):
        self.tickers = tickers or [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
            'META', 'NVDA', 'JPM', 'JNJ', 'V'
        ]
        self.data = {}
        self.signals = {}
        self.performance = {}
        
    def fetch_market_data(self, period: str = "6mo", interval: str = "1d") -> Dict:
        """
        Fetch market data for all tickers using yfinance
        Simulates the data that Pine Script would access via request.security()
        """
        print("📊 Fetching market data for simulation...")
        
        for ticker in self.tickers:
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(period=period, interval=interval)
                
                if not df.empty:
                    # Ensure proper column names for mplfinance
                    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                    self.data[ticker] = df
                    print(f"✅ {ticker}: {len(df)} bars loaded")
                else:
                    print(f"❌ {ticker}: No data available")
                    
            except Exception as e:
                print(f"❌ Error fetching {ticker}: {e}")
        
        return self.data
    
    def calculate_technical_indicators(self, ticker: str) -> Dict:
        """
        Calculate technical indicators using TA-Lib
        Simulates Pine Script technical analysis functions
        """
        if ticker not in self.data:
            return {}
        
        df = self.data[ticker].copy()
        
        # Convert to numpy arrays for TA-Lib
        high = df['High'].values
        low = df['Low'].values
        close = df['Close'].values
        volume = df['Volume'].values
        
        indicators = {}
        
        try:
            # Moving Averages (Pine Script: ta.sma, ta.ema)
            indicators['SMA_10'] = talib.SMA(close, timeperiod=10)
            indicators['SMA_20'] = talib.SMA(close, timeperiod=20)
            indicators['EMA_12'] = talib.EMA(close, timeperiod=12)
            indicators['EMA_26'] = talib.EMA(close, timeperiod=26)
            
            # RSI (Pine Script: ta.rsi)
            indicators['RSI'] = talib.RSI(close, timeperiod=14)
            
            # MACD (Pine Script: ta.macd)
            macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
            indicators['MACD'] = macd
            indicators['MACD_Signal'] = macd_signal
            indicators['MACD_Histogram'] = macd_hist
            
            # Bollinger Bands (Pine Script: ta.bb)
            bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
            indicators['BB_Upper'] = bb_upper
            indicators['BB_Middle'] = bb_middle
            indicators['BB_Lower'] = bb_lower
            
            # ATR for stop loss calculation (Pine Script: ta.atr)
            indicators['ATR'] = talib.ATR(high, low, close, timeperiod=14)
            
            # Volume indicators
            indicators['OBV'] = talib.OBV(close, volume)
            
            # Candlestick patterns (Pine Script pattern recognition)
            indicators['DOJI'] = talib.CDLDOJI(df['Open'].values, high, low, close)
            indicators['HAMMER'] = talib.CDLHAMMER(df['Open'].values, high, low, close)
            indicators['ENGULFING'] = talib.CDLENGULFING(df['Open'].values, high, low, close)
            
            # Stochastic Oscillator
            slowk, slowd = talib.STOCH(high, low, close, fastk_period=14, slowk_period=3, slowd_period=3)
            indicators['STOCH_K'] = slowk
            indicators['STOCH_D'] = slowd
            
            print(f"✅ {ticker}: Technical indicators calculated")
            
        except Exception as e:
            print(f"❌ Error calculating indicators for {ticker}: {e}")
        
        return indicators
    
    def generate_trading_signals(self, ticker: str) -> List[Dict]:
        """
        Generate trading signals based on technical analysis
        Simulates Pine Script strategy logic
        """
        if ticker not in self.data:
            return []
        
        df = self.data[ticker].copy()
        indicators = self.calculate_technical_indicators(ticker)
        
        signals = []
        
        # Add indicators to dataframe
        for key, values in indicators.items():
            if len(values) == len(df):
                df[key] = values
        
        # Trading Strategy Logic (simulating Pine Script conditions)
        for i in range(20, len(df)):  # Start after indicator warmup period
            
            # Buy Signal Conditions (Pine Script: buy_condition)
            sma_crossover = (df['SMA_10'].iloc[i] > df['SMA_20'].iloc[i] and 
                           df['SMA_10'].iloc[i-1] <= df['SMA_20'].iloc[i-1])
            
            rsi_oversold = df['RSI'].iloc[i] < 30 and df['RSI'].iloc[i-1] >= 30
            
            macd_bullish = (df['MACD'].iloc[i] > df['MACD_Signal'].iloc[i] and 
                          df['MACD'].iloc[i-1] <= df['MACD_Signal'].iloc[i-1])
            
            # Sell Signal Conditions
            sma_crossunder = (df['SMA_10'].iloc[i] < df['SMA_20'].iloc[i] and 
                            df['SMA_10'].iloc[i-1] >= df['SMA_20'].iloc[i-1])
            
            rsi_overbought = df['RSI'].iloc[i] > 70 and df['RSI'].iloc[i-1] <= 70
            
            macd_bearish = (df['MACD'].iloc[i] < df['MACD_Signal'].iloc[i] and 
                          df['MACD'].iloc[i-1] >= df['MACD_Signal'].iloc[i-1])
            
            # Generate Buy Signal
            if sma_crossover or (rsi_oversold and macd_bullish):
                entry_price = df['Close'].iloc[i]
                atr_value = df['ATR'].iloc[i]
                
                signal = {
                    'signal': 'BUY',
                    'ticker': ticker,
                    'timestamp': df.index[i].strftime('%Y-%m-%d %H:%M:%S'),
                    'entry_price': round(entry_price, 2),
                    'stop_loss': round(entry_price - (atr_value * 2), 2),
                    'take_profit': round(entry_price + (atr_value * 3), 2),
                    'rsi': round(df['RSI'].iloc[i], 2),
                    'atr': round(atr_value, 2),
                    'strategy': 'sma_rsi_macd',
                    'risk_amount': 100.0,
                    'trading_mode': 'Paper'
                }
                signals.append(signal)
            
            # Generate Sell Signal
            elif sma_crossunder or (rsi_overbought and macd_bearish):
                entry_price = df['Close'].iloc[i]
                atr_value = df['ATR'].iloc[i]
                
                signal = {
                    'signal': 'SELL',
                    'ticker': ticker,
                    'timestamp': df.index[i].strftime('%Y-%m-%d %H:%M:%S'),
                    'entry_price': round(entry_price, 2),
                    'stop_loss': round(entry_price + (atr_value * 2), 2),
                    'take_profit': round(entry_price - (atr_value * 3), 2),
                    'rsi': round(df['RSI'].iloc[i], 2),
                    'atr': round(atr_value, 2),
                    'strategy': 'sma_rsi_macd',
                    'risk_amount': 100.0,
                    'trading_mode': 'Paper'
                }
                signals.append(signal)
        
        self.signals[ticker] = signals
        print(f"✅ {ticker}: {len(signals)} trading signals generated")
        return signals
    
    def create_mplfinance_chart(self, ticker: str, save_path: str = None) -> str:
        """
        Create professional trading charts using mplfinance
        Simulates TradingView chart visualization
        """
        if ticker not in self.data:
            return None
        
        df = self.data[ticker].copy()
        indicators = self.calculate_technical_indicators(ticker)
        
        # Add indicators to dataframe for plotting
        for key, values in indicators.items():
            if len(values) == len(df):
                df[key] = values
        
        # Prepare additional plots
        apds = []
        
        # RSI subplot
        if 'RSI' in df.columns:
            apds.append(mpf.make_addplot(df['RSI'], panel=1, color='purple', 
                                       ylabel='RSI', ylim=(0, 100)))
            # RSI levels
            apds.append(mpf.make_addplot([70]*len(df), panel=1, color='red', 
                                       linestyle='--', alpha=0.7))
            apds.append(mpf.make_addplot([30]*len(df), panel=1, color='green', 
                                       linestyle='--', alpha=0.7))
        
        # MACD subplot
        if all(col in df.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
            apds.append(mpf.make_addplot(df['MACD'], panel=2, color='blue', ylabel='MACD'))
            apds.append(mpf.make_addplot(df['MACD_Signal'], panel=2, color='red'))
            apds.append(mpf.make_addplot(df['MACD_Histogram'], panel=2, type='bar', 
                                       color='gray', alpha=0.3))
        
        # Moving averages on main chart
        if 'SMA_10' in df.columns:
            apds.append(mpf.make_addplot(df['SMA_10'], color='blue', width=1))
        if 'SMA_20' in df.columns:
            apds.append(mpf.make_addplot(df['SMA_20'], color='red', width=1))
        
        # Bollinger Bands
        if all(col in df.columns for col in ['BB_Upper', 'BB_Lower']):
            apds.append(mpf.make_addplot(df['BB_Upper'], color='gray', alpha=0.5))
            apds.append(mpf.make_addplot(df['BB_Lower'], color='gray', alpha=0.5))
        
        # Mark trading signals
        signals = self.signals.get(ticker, [])
        if signals:
            buy_signals = [s for s in signals if s['signal'] == 'BUY']
            sell_signals = [s for s in signals if s['signal'] == 'SELL']
            
            # Create signal markers
            buy_dates = [pd.to_datetime(s['timestamp']) for s in buy_signals]
            sell_dates = [pd.to_datetime(s['timestamp']) for s in sell_signals]
            
            # Add buy/sell markers
            for date in buy_dates:
                if date in df.index:
                    idx = df.index.get_loc(date)
                    apds.append(mpf.make_addplot([df['Low'].iloc[idx] * 0.98], 
                                               type='scatter', markersize=100, 
                                               marker='^', color='green'))
            
            for date in sell_dates:
                if date in df.index:
                    idx = df.index.get_loc(date)
                    apds.append(mpf.make_addplot([df['High'].iloc[idx] * 1.02], 
                                               type='scatter', markersize=100, 
                                               marker='v', color='red'))
        
        # Create the chart
        save_path = save_path or f'/workspace/tvTrading/charts/{ticker}_mplfinance.png'
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        mpf.plot(df, 
                type='candle',
                style='charles',
                title=f'{ticker} - Trading Analysis (mplfinance)',
                ylabel='Price ($)',
                volume=True,
                addplot=apds,
                figsize=(16, 12),
                savefig=save_path)
        
        print(f"✅ {ticker}: mplfinance chart saved to {save_path}")
        return save_path
    
    def create_plotly_interactive_chart(self, ticker: str, save_path: str = None) -> str:
        """
        Create interactive trading charts using Plotly
        Perfect for web dashboard integration
        """
        if ticker not in self.data:
            return None
        
        df = self.data[ticker].copy()
        indicators = self.calculate_technical_indicators(ticker)
        
        # Add indicators to dataframe
        for key, values in indicators.items():
            if len(values) == len(df):
                df[key] = values
        
        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{ticker} Price & Indicators', 'Volume', 'RSI', 'MACD'),
            row_width=[0.2, 0.1, 0.1, 0.1]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='Price',
                increasing_line_color='green',
                decreasing_line_color='red'
            ),
            row=1, col=1
        )
        
        # Moving averages
        if 'SMA_10' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['SMA_10'], name='SMA 10', 
                          line=dict(color='blue', width=1)),
                row=1, col=1
            )
        
        if 'SMA_20' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', 
                          line=dict(color='red', width=1)),
                row=1, col=1
            )
        
        # Bollinger Bands
        if all(col in df.columns for col in ['BB_Upper', 'BB_Lower', 'BB_Middle']):
            fig.add_trace(
                go.Scatter(x=df.index, y=df['BB_Upper'], name='BB Upper', 
                          line=dict(color='gray', width=1), opacity=0.5),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=df['BB_Lower'], name='BB Lower', 
                          line=dict(color='gray', width=1), opacity=0.5, 
                          fill='tonexty', fillcolor='rgba(128,128,128,0.1)'),
                row=1, col=1
            )
        
        # Volume
        fig.add_trace(
            go.Bar(x=df.index, y=df['Volume'], name='Volume', 
                   marker_color='lightblue', opacity=0.7),
            row=2, col=1
        )
        
        # RSI
        if 'RSI' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['RSI'], name='RSI', 
                          line=dict(color='purple', width=2)),
                row=3, col=1
            )
            # RSI levels
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        # MACD
        if all(col in df.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
            fig.add_trace(
                go.Scatter(x=df.index, y=df['MACD'], name='MACD', 
                          line=dict(color='blue', width=2)),
                row=4, col=1
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=df['MACD_Signal'], name='MACD Signal', 
                          line=dict(color='red', width=2)),
                row=4, col=1
            )
            fig.add_trace(
                go.Bar(x=df.index, y=df['MACD_Histogram'], name='MACD Histogram', 
                       marker_color='gray', opacity=0.3),
                row=4, col=1
            )
        
        # Add trading signals
        signals = self.signals.get(ticker, [])
        if signals:
            buy_signals = [s for s in signals if s['signal'] == 'BUY']
            sell_signals = [s for s in signals if s['signal'] == 'SELL']
            
            # Buy signals
            if buy_signals:
                buy_dates = [pd.to_datetime(s['timestamp']) for s in buy_signals]
                buy_prices = [s['entry_price'] for s in buy_signals]
                
                fig.add_trace(
                    go.Scatter(
                        x=buy_dates, y=buy_prices, mode='markers',
                        marker=dict(symbol='triangle-up', size=15, color='green'),
                        name='Buy Signals', text=[f"BUY: ${p}" for p in buy_prices]
                    ),
                    row=1, col=1
                )
            
            # Sell signals
            if sell_signals:
                sell_dates = [pd.to_datetime(s['timestamp']) for s in sell_signals]
                sell_prices = [s['entry_price'] for s in sell_signals]
                
                fig.add_trace(
                    go.Scatter(
                        x=sell_dates, y=sell_prices, mode='markers',
                        marker=dict(symbol='triangle-down', size=15, color='red'),
                        name='Sell Signals', text=[f"SELL: ${p}" for p in sell_prices]
                    ),
                    row=1, col=1
                )
        
        # Update layout
        fig.update_layout(
            title=f'{ticker} - Interactive Trading Analysis (Plotly)',
            xaxis_rangeslider_visible=False,
            height=800,
            showlegend=True,
            template='plotly_white'
        )
        
        # Update y-axes
        fig.update_yaxes(title_text="Price ($)", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
        fig.update_yaxes(title_text="MACD", row=4, col=1)
        
        # Save as HTML
        save_path = save_path or f'/workspace/tvTrading/charts/{ticker}_plotly.html'
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        fig.write_html(save_path)
        print(f"✅ {ticker}: Interactive Plotly chart saved to {save_path}")
        
        return save_path
    
    def simulate_pine_script_webhook(self, ticker: str) -> List[Dict]:
        """
        Simulate Pine Script webhook payloads
        Generates the exact JSON that would be sent to Flask webhook
        """
        signals = self.signals.get(ticker, [])
        webhook_payloads = []
        
        for signal in signals:
            # Create webhook payload matching Pine Script format
            payload = {
                "signal": signal['signal'],
                "ticker": signal['ticker'],
                "tradingMode": signal['trading_mode'],
                "riskAmount": signal['risk_amount'],
                "entryPrice": signal['entry_price'],
                "stopLoss": signal['stop_loss'],
                "takeProfit": signal['take_profit'],
                "strategy": signal['strategy'],
                "timeframe": "1d",
                "timestamp": signal['timestamp'],
                "tickerGroup": "Group_1_NYSE",
                "rsi": signal['rsi'],
                "atr": signal['atr']
            }
            webhook_payloads.append(payload)
        
        # Save webhook payloads to file
        webhook_file = f'/workspace/tvTrading/webhooks/{ticker}_webhooks.json'
        os.makedirs(os.path.dirname(webhook_file), exist_ok=True)
        
        with open(webhook_file, 'w') as f:
            json.dump(webhook_payloads, f, indent=2)
        
        print(f"✅ {ticker}: {len(webhook_payloads)} webhook payloads saved to {webhook_file}")
        return webhook_payloads
    
    def run_full_simulation(self) -> Dict:
        """
        Run complete trading simulation for all tickers
        Coordinates all teams: Analytics, Backend, Frontend
        """
        print("🚀 Starting Full Trading Simulation...")
        print("=" * 60)
        
        # Step 1: Fetch market data
        self.fetch_market_data()
        
        # Step 2: Generate signals and create visualizations for each ticker
        all_signals = []
        all_webhooks = []
        
        for ticker in self.tickers:
            if ticker in self.data:
                print(f"\n📊 Processing {ticker}...")
                
                # Generate trading signals
                signals = self.generate_trading_signals(ticker)
                all_signals.extend(signals)
                
                # Create mplfinance chart
                self.create_mplfinance_chart(ticker)
                
                # Create Plotly interactive chart
                self.create_plotly_interactive_chart(ticker)
                
                # Generate webhook payloads
                webhooks = self.simulate_pine_script_webhook(ticker)
                all_webhooks.extend(webhooks)
        
        # Step 3: Generate summary report
        summary = {
            'simulation_date': datetime.now().isoformat(),
            'tickers_processed': len([t for t in self.tickers if t in self.data]),
            'total_signals': len(all_signals),
            'buy_signals': len([s for s in all_signals if s['signal'] == 'BUY']),
            'sell_signals': len([s for s in all_signals if s['signal'] == 'SELL']),
            'webhook_payloads': len(all_webhooks),
            'charts_generated': {
                'mplfinance': len([t for t in self.tickers if t in self.data]),
                'plotly': len([t for t in self.tickers if t in self.data])
            }
        }
        
        # Save summary
        with open('/workspace/tvTrading/simulation_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\n" + "=" * 60)
        print("🎯 SIMULATION COMPLETE!")
        print(f"📊 Processed: {summary['tickers_processed']} tickers")
        print(f"🎯 Generated: {summary['total_signals']} trading signals")
        print(f"📈 Buy signals: {summary['buy_signals']}")
        print(f"📉 Sell signals: {summary['sell_signals']}")
        print(f"🔗 Webhook payloads: {summary['webhook_payloads']}")
        print(f"📊 Charts created: {summary['charts_generated']['mplfinance']} mplfinance + {summary['charts_generated']['plotly']} Plotly")
        print("=" * 60)
        
        return summary

def main():
    """
    Main execution function
    Demonstrates the complete trading simulation pipeline
    """
    # Initialize simulator with popular tickers
    tickers = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
        'META', 'NVDA', 'JPM', 'JNJ', 'V'
    ]
    
    simulator = TradingSimulator(tickers)
    
    # Run full simulation
    summary = simulator.run_full_simulation()
    
    print("\n🎯 Simulation files generated:")
    print("📊 Charts: /workspace/tvTrading/charts/")
    print("🔗 Webhooks: /workspace/tvTrading/webhooks/")
    print("📋 Summary: /workspace/tvTrading/simulation_summary.json")
    
    return summary

if __name__ == "__main__":
    main()


