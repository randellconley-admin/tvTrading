

# 🎯 Local Trading Simulation with mplfinance, Plotly & TA-Lib

## 📊 Core Library Integration Strategy

### Library Roles & Responsibilities

#### 🔍 **TA-Lib** - Technical Analysis Engine
- **Purpose**: Calculate 150+ technical indicators
- **Integration**: Core signal generation logic
- **Key Functions**:
  - RSI, MACD, Bollinger Bands
  - Moving averages (SMA, EMA, WMA)
  - Candlestick pattern recognition
  - Volume indicators

#### 📈 **mplfinance** - Static Financial Charts
- **Purpose**: Generate publication-quality financial charts
- **Integration**: Backtesting visualization and reports
- **Key Features**:
  - Candlestick charts with volume
  - Technical indicator overlays
  - Buy/sell signal markers
  - Multi-timeframe analysis

#### 🎨 **Plotly** - Interactive Dashboards
- **Purpose**: Real-time interactive trading dashboard
- **Integration**: Live monitoring and analysis
- **Key Features**:
  - Real-time candlestick updates
  - Interactive technical indicators
  - Zoom, pan, hover functionality
  - Web-based dashboard integration

---

## 🏗️ Simplified Architecture (No OpenSearch)

```
┌─────────────────┐    ┌──────────────────────────────────┐    ┌─────────────────┐
│   TradingView   │───▶│        Single EC2 Instance       │───▶│     Alpaca      │
│  (Pine Scripts) │    │  ┌─────────────────────────────┐  │    │  (Paper/Live)   │
└─────────────────┘    │  │     Flask App (Port 5000)   │  │    └─────────────────┘
                       │  │     PostgreSQL (Port 5432)  │  │
                       │  │     Redis (Port 6379)       │  │
                       │  │     Nginx (Port 80/443)     │  │
                       │  └─────────────────────────────┘  │
                       └──────────────────────────────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │   Route53 DNS   │
                               │ trading.domain  │
                               └─────────────────┘
```

---

## 🔧 Updated Technology Stack

### Core Components
```yaml
Backend:
  - Flask: Web framework
  - PostgreSQL: Database
  - Redis: Caching
  - Celery: Background tasks

Trading Analytics:
  - TA-Lib: Technical indicators
  - mplfinance: Static charts
  - Plotly: Interactive charts
  - pandas/numpy: Data processing

Frontend:
  - React: Dashboard UI
  - Plotly.js: Interactive charts
  - WebSocket: Real-time updates

Infrastructure:
  - Docker: Containerization
  - Nginx: Reverse proxy
  - Route53: DNS
  - S3: Backups only
  - SNS: Critical alerts
```

---

## 📋 Implementation Plan

### Phase 1: Local Simulation Engine
**Trading Analytics Team Lead**

#### 1.1 TA-Lib Integration
```python
import talib
import pandas as pd
import numpy as np

class TechnicalAnalyzer:
    """Core technical analysis using TA-Lib"""
    
    def __init__(self, data):
        self.data = data
        self.high = data['High'].values
        self.low = data['Low'].values
        self.close = data['Close'].values
        self.volume = data['Volume'].values
    
    def calculate_indicators(self):
        """Calculate all technical indicators"""
        indicators = {}
        
        # Trend Indicators
        indicators['SMA_10'] = talib.SMA(self.close, timeperiod=10)
        indicators['SMA_20'] = talib.SMA(self.close, timeperiod=20)
        indicators['EMA_12'] = talib.EMA(self.close, timeperiod=12)
        indicators['EMA_26'] = talib.EMA(self.close, timeperiod=26)
        
        # Momentum Indicators
        indicators['RSI'] = talib.RSI(self.close, timeperiod=14)
        indicators['MACD'], indicators['MACD_signal'], indicators['MACD_hist'] = talib.MACD(self.close)
        
        # Volatility Indicators
        indicators['BB_upper'], indicators['BB_middle'], indicators['BB_lower'] = talib.BBANDS(self.close)
        indicators['ATR'] = talib.ATR(self.high, self.low, self.close, timeperiod=14)
        
        # Volume Indicators
        indicators['OBV'] = talib.OBV(self.close, self.volume)
        
        # Candlestick Patterns
        indicators['DOJI'] = talib.CDLDOJI(self.high, self.low, self.close, self.close)
        indicators['HAMMER'] = talib.CDLHAMMER(self.high, self.low, self.close, self.close)
        indicators['ENGULFING'] = talib.CDLENGULFING(self.high, self.low, self.close, self.close)
        
        return indicators
    
    def generate_signals(self, indicators):
        """Generate buy/sell signals based on indicators"""
        signals = pd.DataFrame(index=self.data.index)
        
        # Simple moving average crossover
        signals['MA_Signal'] = np.where(
            indicators['SMA_10'] > indicators['SMA_20'], 1, 0
        )
        
        # RSI oversold/overbought
        signals['RSI_Signal'] = np.where(
            (indicators['RSI'] < 30), 1,  # Buy signal
            np.where(indicators['RSI'] > 70, -1, 0)  # Sell signal
        )
        
        # MACD crossover
        signals['MACD_Signal'] = np.where(
            indicators['MACD'] > indicators['MACD_signal'], 1, -1
        )
        
        # Combined signal
        signals['Combined_Signal'] = (
            signals['MA_Signal'] + 
            signals['RSI_Signal'] + 
            signals['MACD_Signal']
        )
        
        return signals
```

#### 1.2 mplfinance Chart Generation
```python
import mplfinance as mpf
import matplotlib.pyplot as plt

class StaticChartGenerator:
    """Generate static financial charts using mplfinance"""
    
    def __init__(self, data, indicators, signals):
        self.data = data
        self.indicators = indicators
        self.signals = signals
    
    def create_trading_chart(self, ticker, save_path=None):
        """Create comprehensive trading chart"""
        
        # Prepare additional plots
        apds = [
            mpf.make_addplot(self.indicators['SMA_10'], color='blue', width=1),
            mpf.make_addplot(self.indicators['SMA_20'], color='red', width=1),
            mpf.make_addplot(self.indicators['BB_upper'], color='gray', alpha=0.5),
            mpf.make_addplot(self.indicators['BB_lower'], color='gray', alpha=0.5),
        ]
        
        # Add buy/sell markers
        buy_signals = self.signals[self.signals['Combined_Signal'] > 1].index
        sell_signals = self.signals[self.signals['Combined_Signal'] < -1].index
        
        if len(buy_signals) > 0:
            buy_prices = self.data.loc[buy_signals, 'Low'] * 0.98
            apds.append(mpf.make_addplot(buy_prices, type='scatter', 
                                       markersize=100, marker='^', color='green'))
        
        if len(sell_signals) > 0:
            sell_prices = self.data.loc[sell_signals, 'High'] * 1.02
            apds.append(mpf.make_addplot(sell_prices, type='scatter', 
                                       markersize=100, marker='v', color='red'))
        
        # Create the chart
        mpf.plot(
            self.data,
            type='candle',
            style='charles',
            title=f'{ticker} - Trading Analysis',
            ylabel='Price ($)',
            volume=True,
            addplot=apds,
            figsize=(15, 10),
            savefig=save_path if save_path else None
        )
    
    def create_indicator_subplots(self, ticker):
        """Create separate indicator charts"""
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        
        # RSI subplot
        axes[0].plot(self.data.index, self.indicators['RSI'], color='purple')
        axes[0].axhline(y=70, color='r', linestyle='--', alpha=0.7)
        axes[0].axhline(y=30, color='g', linestyle='--', alpha=0.7)
        axes[0].set_title(f'{ticker} - RSI')
        axes[0].set_ylabel('RSI')
        
        # MACD subplot
        axes[1].plot(self.data.index, self.indicators['MACD'], color='blue', label='MACD')
        axes[1].plot(self.data.index, self.indicators['MACD_signal'], color='red', label='Signal')
        axes[1].bar(self.data.index, self.indicators['MACD_hist'], color='gray', alpha=0.7)
        axes[1].set_title(f'{ticker} - MACD')
        axes[1].set_ylabel('MACD')
        axes[1].legend()
        
        # Volume subplot
        axes[2].bar(self.data.index, self.data['Volume'], color='lightblue', alpha=0.7)
        axes[2].plot(self.data.index, self.indicators['OBV'], color='orange', label='OBV')
        axes[2].set_title(f'{ticker} - Volume & OBV')
        axes[2].set_ylabel('Volume')
        axes[2].legend()
        
        plt.tight_layout()
        return fig
```

#### 1.3 Plotly Interactive Dashboard
```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

class InteractiveDashboard:
    """Create interactive trading dashboard using Plotly"""
    
    def __init__(self, data, indicators, signals):
        self.data = data
        self.indicators = indicators
        self.signals = signals
    
    def create_main_chart(self, ticker):
        """Create main interactive candlestick chart"""
        
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{ticker} Price', 'RSI', 'MACD', 'Volume'),
            row_width=[0.2, 0.1, 0.1, 0.1]
        )
        
        # Candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=self.data.index,
                open=self.data['Open'],
                high=self.data['High'],
                low=self.data['Low'],
                close=self.data['Close'],
                name='Price'
            ),
            row=1, col=1
        )
        
        # Moving averages
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.indicators['SMA_10'],
                mode='lines',
                name='SMA 10',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.indicators['SMA_20'],
                mode='lines',
                name='SMA 20',
                line=dict(color='red', width=1)
            ),
            row=1, col=1
        )
        
        # Bollinger Bands
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.indicators['BB_upper'],
                mode='lines',
                name='BB Upper',
                line=dict(color='gray', width=1, dash='dash'),
                showlegend=False
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.indicators['BB_lower'],
                mode='lines',
                name='BB Lower',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Buy/Sell signals
        buy_signals = self.signals[self.signals['Combined_Signal'] > 1]
        sell_signals = self.signals[self.signals['Combined_Signal'] < -1]
        
        if len(buy_signals) > 0:
            fig.add_trace(
                go.Scatter(
                    x=buy_signals.index,
                    y=self.data.loc[buy_signals.index, 'Low'] * 0.98,
                    mode='markers',
                    name='Buy Signal',
                    marker=dict(symbol='triangle-up', size=15, color='green')
                ),
                row=1, col=1
            )
        
        if len(sell_signals) > 0:
            fig.add_trace(
                go.Scatter(
                    x=sell_signals.index,
                    y=self.data.loc[sell_signals.index, 'High'] * 1.02,
                    mode='markers',
                    name='Sell Signal',
                    marker=dict(symbol='triangle-down', size=15, color='red')
                ),
                row=1, col=1
            )
        
        # RSI
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.indicators['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='purple')
            ),
            row=2, col=1
        )
        
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.indicators['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='blue')
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.indicators['MACD_signal'],
                mode='lines',
                name='MACD Signal',
                line=dict(color='red')
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=self.data.index,
                y=self.indicators['MACD_hist'],
                name='MACD Histogram',
                marker_color='gray',
                opacity=0.7
            ),
            row=3, col=1
        )
        
        # Volume
        fig.add_trace(
            go.Bar(
                x=self.data.index,
                y=self.data['Volume'],
                name='Volume',
                marker_color='lightblue',
                opacity=0.7
            ),
            row=4, col=1
        )
        
        # Update layout
        fig.update_layout(
            title=f'{ticker} - Interactive Trading Analysis',
            xaxis_rangeslider_visible=False,
            height=800,
            showlegend=True
        )
        
        return fig
    
    def create_performance_dashboard(self, portfolio_data):
        """Create portfolio performance dashboard"""
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Portfolio Value', 'Daily Returns', 'Signal Distribution', 'Win/Loss Ratio'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Portfolio value over time
        fig.add_trace(
            go.Scatter(
                x=portfolio_data.index,
                y=portfolio_data['Portfolio_Value'],
                mode='lines',
                name='Portfolio Value',
                line=dict(color='green', width=2)
            ),
            row=1, col=1
        )
        
        # Daily returns
        fig.add_trace(
            go.Bar(
                x=portfolio_data.index,
                y=portfolio_data['Daily_Return'],
                name='Daily Returns',
                marker_color=['green' if x > 0 else 'red' for x in portfolio_data['Daily_Return']]
            ),
            row=1, col=2
        )
        
        # Signal distribution pie chart
        signal_counts = self.signals['Combined_Signal'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=['Buy', 'Hold', 'Sell'],
                values=[signal_counts.get(1, 0), signal_counts.get(0, 0), signal_counts.get(-1, 0)],
                name="Signal Distribution"
            ),
            row=2, col=1
        )
        
        # Win/Loss ratio
        wins = len(portfolio_data[portfolio_data['Daily_Return'] > 0])
        losses = len(portfolio_data[portfolio_data['Daily_Return'] < 0])
        
        fig.add_trace(
            go.Bar(
                x=['Wins', 'Losses'],
                y=[wins, losses],
                name='Win/Loss',
                marker_color=['green', 'red']
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title='Portfolio Performance Dashboard',
            height=600,
            showlegend=True
        )
        
        return fig
```

### Phase 2: Flask Integration
**Backend Team + Trading Analytics Team**

#### 2.1 Updated Flask Application
```python
from flask import Flask, render_template, jsonify
import yfinance as yf
from technical_analyzer import TechnicalAnalyzer
from chart_generator import StaticChartGenerator, InteractiveDashboard
import json

app = Flask(__name__)

@app.route('/api/analyze/<ticker>')
def analyze_ticker(ticker):
    """Analyze ticker and return technical analysis"""
    try:
        # Fetch data
        stock = yf.Ticker(ticker)
        data = stock.history(period="6mo")
        
        # Perform technical analysis
        analyzer = TechnicalAnalyzer(data)
        indicators = analyzer.calculate_indicators()
        signals = analyzer.generate_signals(indicators)
        
        # Create interactive chart
        dashboard = InteractiveDashboard(data, indicators, signals)
        chart_json = dashboard.create_main_chart(ticker).to_json()
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'chart': json.loads(chart_json),
            'latest_signal': signals['Combined_Signal'].iloc[-1],
            'latest_rsi': indicators['RSI'][-1],
            'latest_price': data['Close'].iloc[-1]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/simulate/<ticker>')
def simulate_strategy(ticker):
    """Simulate Pine Script strategy locally"""
    try:
        # This simulates what the Pine Script would do
        stock = yf.Ticker(ticker)
        data = stock.history(period="1y")
        
        analyzer = TechnicalAnalyzer(data)
        indicators = analyzer.calculate_indicators()
        signals = analyzer.generate_signals(indicators)
        
        # Simulate trading
        portfolio_value = 10000  # Starting capital
        position = 0
        trades = []
        
        for i, (date, signal) in enumerate(signals['Combined_Signal'].items()):
            if signal > 1 and position == 0:  # Buy signal
                position = portfolio_value / data.loc[date, 'Close']
                portfolio_value = 0
                trades.append({
                    'date': date.isoformat(),
                    'action': 'BUY',
                    'price': data.loc[date, 'Close'],
                    'shares': position
                })
            elif signal < -1 and position > 0:  # Sell signal
                portfolio_value = position * data.loc[date, 'Close']
                position = 0
                trades.append({
                    'date': date.isoformat(),
                    'action': 'SELL',
                    'price': data.loc[date, 'Close'],
                    'portfolio_value': portfolio_value
                })
        
        # Final portfolio value
        if position > 0:
            final_value = position * data['Close'].iloc[-1]
        else:
            final_value = portfolio_value
        
        return jsonify({
            'success': True,
            'ticker': ticker,
            'initial_value': 10000,
            'final_value': final_value,
            'return_pct': ((final_value - 10000) / 10000) * 100,
            'trades': trades,
            'total_trades': len(trades)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```

---

## 🚀 Deployment Without OpenSearch

### Updated Docker Compose
```yaml
version: '3.8'

services:
  flask-app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://trading:password@postgres:5432/trading_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./charts:/app/charts
      - ./logs:/app/logs

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=trading_db
      - POSTGRES_USER=trading
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/build:/usr/share/nginx/html
    depends_on:
      - flask-app

volumes:
  postgres_data:
  redis_data:
```

This simplified approach focuses on the core trading functionality using the three specified libraries while maintaining the centralized EC2 architecture without OpenSearch complexity.


