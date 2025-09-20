


"""
Chart Generation using mplfinance and Plotly
Trading Analytics Team Implementation
"""

import pandas as pd
import numpy as np
import mplfinance as mpf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class MPLFinanceChartGenerator:
    """
    Static financial chart generation using mplfinance
    Perfect for backtesting reports and static analysis
    """
    
    def __init__(self, data: pd.DataFrame, indicators: Dict, signals: pd.DataFrame = None):
        """
        Initialize chart generator
        
        Args:
            data: OHLCV DataFrame
            indicators: Technical indicators dictionary
            signals: Trading signals DataFrame
        """
        self.data = data.copy()
        self.indicators = indicators
        self.signals = signals
        
        # Ensure proper datetime index
        if not isinstance(self.data.index, pd.DatetimeIndex):
            self.data.index = pd.to_datetime(self.data.index)
    
    def create_main_chart(self, ticker: str, save_path: str = None, 
                         show_signals: bool = True) -> str:
        """
        Create comprehensive trading chart with all indicators
        
        Args:
            ticker: Stock ticker symbol
            save_path: Path to save chart image
            show_signals: Whether to show buy/sell signals
            
        Returns:
            Path to saved chart
        """
        try:
            # Prepare additional plots
            apds = []
            
            # Moving averages on main chart
            if 'SMA_10' in self.indicators:
                sma_10 = pd.Series(self.indicators['SMA_10'], index=self.data.index)
                apds.append(mpf.make_addplot(sma_10, color='blue', width=1.5, alpha=0.8))
            
            if 'SMA_20' in self.indicators:
                sma_20 = pd.Series(self.indicators['SMA_20'], index=self.data.index)
                apds.append(mpf.make_addplot(sma_20, color='red', width=1.5, alpha=0.8))
            
            if 'EMA_12' in self.indicators:
                ema_12 = pd.Series(self.indicators['EMA_12'], index=self.data.index)
                apds.append(mpf.make_addplot(ema_12, color='green', width=1, alpha=0.7))
            
            # Bollinger Bands
            if all(key in self.indicators for key in ['BB_Upper', 'BB_Lower']):
                bb_upper = pd.Series(self.indicators['BB_Upper'], index=self.data.index)
                bb_lower = pd.Series(self.indicators['BB_Lower'], index=self.data.index)
                apds.append(mpf.make_addplot(bb_upper, color='gray', width=1, alpha=0.5, linestyle='--'))
                apds.append(mpf.make_addplot(bb_lower, color='gray', width=1, alpha=0.5, linestyle='--'))
            
            # Support and Resistance levels (if available)
            if hasattr(self, 'support_resistance'):
                sr = self.support_resistance
                for level in sr.get('resistance_levels', [])[:3]:  # Top 3 resistance
                    level_line = pd.Series([level] * len(self.data), index=self.data.index)
                    apds.append(mpf.make_addplot(level_line, color='red', width=0.8, alpha=0.6, linestyle=':'))
                
                for level in sr.get('support_levels', [])[:3]:  # Top 3 support
                    level_line = pd.Series([level] * len(self.data), index=self.data.index)
                    apds.append(mpf.make_addplot(level_line, color='green', width=0.8, alpha=0.6, linestyle=':'))
            
            # Trading signals
            if show_signals and self.signals is not None:
                buy_signals = self.signals[self.signals['Action'] == 'BUY']
                sell_signals = self.signals[self.signals['Action'] == 'SELL']
                
                if len(buy_signals) > 0:
                    buy_prices = self.data.loc[buy_signals.index, 'Low'] * 0.98
                    apds.append(mpf.make_addplot(buy_prices, type='scatter', 
                                               markersize=100, marker='^', color='green'))
                
                if len(sell_signals) > 0:
                    sell_prices = self.data.loc[sell_signals.index, 'High'] * 1.02
                    apds.append(mpf.make_addplot(sell_prices, type='scatter', 
                                               markersize=100, marker='v', color='red'))
            
            # Create the main chart
            save_path = save_path or f'/workspace/tvTrading/charts/{ticker}_main_chart.png'
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            mpf.plot(
                self.data,
                type='candle',
                style='charles',
                title=f'{ticker} - Technical Analysis Overview',
                ylabel='Price ($)',
                volume=True,
                addplot=apds if apds else None,
                figsize=(16, 10),
                savefig=save_path,
                tight_layout=True
            )
            
            print(f"✅ Main chart saved: {save_path}")
            return save_path
            
        except Exception as e:
            print(f"❌ Error creating main chart: {e}")
            return None
    
    def create_indicator_subplots(self, ticker: str, save_path: str = None) -> str:
        """
        Create separate charts for technical indicators
        
        Args:
            ticker: Stock ticker symbol
            save_path: Path to save chart image
            
        Returns:
            Path to saved chart
        """
        try:
            fig, axes = plt.subplots(4, 1, figsize=(16, 12))
            fig.suptitle(f'{ticker} - Technical Indicators Analysis', fontsize=16, fontweight='bold')
            
            # RSI Subplot
            if 'RSI' in self.indicators:
                rsi = pd.Series(self.indicators['RSI'], index=self.data.index)
                axes[0].plot(self.data.index, rsi, color='purple', linewidth=2, label='RSI')
                axes[0].axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
                axes[0].axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
                axes[0].axhline(y=50, color='gray', linestyle='-', alpha=0.5, label='Midline')
                axes[0].set_title('RSI (Relative Strength Index)')
                axes[0].set_ylabel('RSI')
                axes[0].set_ylim(0, 100)
                axes[0].legend()
                axes[0].grid(True, alpha=0.3)
            
            # MACD Subplot
            if all(key in self.indicators for key in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
                macd = pd.Series(self.indicators['MACD'], index=self.data.index)
                macd_signal = pd.Series(self.indicators['MACD_Signal'], index=self.data.index)
                macd_hist = pd.Series(self.indicators['MACD_Histogram'], index=self.data.index)
                
                axes[1].plot(self.data.index, macd, color='blue', linewidth=2, label='MACD')
                axes[1].plot(self.data.index, macd_signal, color='red', linewidth=2, label='Signal')
                axes[1].bar(self.data.index, macd_hist, color='gray', alpha=0.7, label='Histogram')
                axes[1].axhline(y=0, color='black', linestyle='-', alpha=0.5)
                axes[1].set_title('MACD (Moving Average Convergence Divergence)')
                axes[1].set_ylabel('MACD')
                axes[1].legend()
                axes[1].grid(True, alpha=0.3)
            
            # Stochastic Oscillator
            if all(key in self.indicators for key in ['STOCH_K', 'STOCH_D']):
                stoch_k = pd.Series(self.indicators['STOCH_K'], index=self.data.index)
                stoch_d = pd.Series(self.indicators['STOCH_D'], index=self.data.index)
                
                axes[2].plot(self.data.index, stoch_k, color='blue', linewidth=2, label='%K')
                axes[2].plot(self.data.index, stoch_d, color='red', linewidth=2, label='%D')
                axes[2].axhline(y=80, color='red', linestyle='--', alpha=0.7, label='Overbought (80)')
                axes[2].axhline(y=20, color='green', linestyle='--', alpha=0.7, label='Oversold (20)')
                axes[2].set_title('Stochastic Oscillator')
                axes[2].set_ylabel('Stochastic')
                axes[2].set_ylim(0, 100)
                axes[2].legend()
                axes[2].grid(True, alpha=0.3)
            
            # Volume and OBV
            if 'OBV' in self.indicators:
                # Volume bars
                volume_colors = ['green' if close >= open_price else 'red' 
                               for close, open_price in zip(self.data['Close'], self.data['Open'])]
                axes[3].bar(self.data.index, self.data['Volume'], color=volume_colors, alpha=0.7, label='Volume')
                
                # OBV line on secondary y-axis
                ax3_twin = axes[3].twinx()
                obv = pd.Series(self.indicators['OBV'], index=self.data.index)
                ax3_twin.plot(self.data.index, obv, color='orange', linewidth=2, label='OBV')
                
                axes[3].set_title('Volume & On-Balance Volume (OBV)')
                axes[3].set_ylabel('Volume')
                ax3_twin.set_ylabel('OBV', color='orange')
                axes[3].legend(loc='upper left')
                ax3_twin.legend(loc='upper right')
                axes[3].grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            save_path = save_path or f'/workspace/tvTrading/charts/{ticker}_indicators.png'
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Indicator charts saved: {save_path}")
            return save_path
            
        except Exception as e:
            print(f"❌ Error creating indicator subplots: {e}")
            return None
    
    def create_pattern_analysis_chart(self, ticker: str, save_path: str = None) -> str:
        """
        Create candlestick pattern analysis chart
        
        Args:
            ticker: Stock ticker symbol
            save_path: Path to save chart image
            
        Returns:
            Path to saved chart
        """
        try:
            # Prepare pattern markers
            apds = []
            
            # Bullish patterns
            bullish_patterns = ['HAMMER', 'MORNING_STAR', 'ENGULFING', 'PIERCING']
            for pattern in bullish_patterns:
                if pattern in self.indicators:
                    pattern_data = pd.Series(self.indicators[pattern], index=self.data.index)
                    bullish_signals = pattern_data[pattern_data > 0]
                    if len(bullish_signals) > 0:
                        marker_prices = self.data.loc[bullish_signals.index, 'Low'] * 0.97
                        apds.append(mpf.make_addplot(marker_prices, type='scatter',
                                                   markersize=80, marker='^', color='green'))
            
            # Bearish patterns
            bearish_patterns = ['SHOOTING_STAR', 'EVENING_STAR', 'DARK_CLOUD', 'HANGING_MAN']
            for pattern in bearish_patterns:
                if pattern in self.indicators:
                    pattern_data = pd.Series(self.indicators[pattern], index=self.data.index)
                    bearish_signals = pattern_data[pattern_data < 0]
                    if len(bearish_signals) > 0:
                        marker_prices = self.data.loc[bearish_signals.index, 'High'] * 1.03
                        apds.append(mpf.make_addplot(marker_prices, type='scatter',
                                                   markersize=80, marker='v', color='red'))
            
            save_path = save_path or f'/workspace/tvTrading/charts/{ticker}_patterns.png'
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            mpf.plot(
                self.data,
                type='candle',
                style='nightclouds',
                title=f'{ticker} - Candlestick Pattern Analysis',
                ylabel='Price ($)',
                addplot=apds if apds else None,
                figsize=(16, 8),
                savefig=save_path
            )
            
            print(f"✅ Pattern analysis chart saved: {save_path}")
            return save_path
            
        except Exception as e:
            print(f"❌ Error creating pattern analysis chart: {e}")
            return None

class PlotlyInteractiveCharts:
    """
    Interactive chart generation using Plotly
    Perfect for web dashboards and real-time monitoring
    """
    
    def __init__(self, data: pd.DataFrame, indicators: Dict, signals: pd.DataFrame = None):
        """
        Initialize interactive chart generator
        
        Args:
            data: OHLCV DataFrame
            indicators: Technical indicators dictionary
            signals: Trading signals DataFrame
        """
        self.data = data.copy()
        self.indicators = indicators
        self.signals = signals
    
    def create_comprehensive_dashboard(self, ticker: str) -> go.Figure:
        """
        Create comprehensive interactive trading dashboard
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Plotly Figure object
        """
        try:
            # Create subplots
            fig = make_subplots(
                rows=5, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.02,
                subplot_titles=(
                    f'{ticker} - Price & Indicators',
                    'Volume',
                    'RSI',
                    'MACD',
                    'Stochastic'
                ),
                row_heights=[0.4, 0.15, 0.15, 0.15, 0.15]
            )
            
            # Main candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=self.data.index,
                    open=self.data['Open'],
                    high=self.data['High'],
                    low=self.data['Low'],
                    close=self.data['Close'],
                    name='Price',
                    increasing_line_color='#00ff88',
                    decreasing_line_color='#ff4444'
                ),
                row=1, col=1
            )
            
            # Moving averages
            if 'SMA_10' in self.indicators:
                fig.add_trace(
                    go.Scatter(
                        x=self.data.index,
                        y=self.indicators['SMA_10'],
                        mode='lines',
                        name='SMA 10',
                        line=dict(color='blue', width=2),
                        opacity=0.8
                    ),
                    row=1, col=1
                )
            
            if 'SMA_20' in self.indicators:
                fig.add_trace(
                    go.Scatter(
                        x=self.data.index,
                        y=self.indicators['SMA_20'],
                        mode='lines',
                        name='SMA 20',
                        line=dict(color='red', width=2),
                        opacity=0.8
                    ),
                    row=1, col=1
                )
            
            # Bollinger Bands
            if all(key in self.indicators for key in ['BB_Upper', 'BB_Lower', 'BB_Middle']):
                fig.add_trace(
                    go.Scatter(
                        x=self.data.index,
                        y=self.indicators['BB_Upper'],
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
                        y=self.indicators['BB_Lower'],
                        mode='lines',
                        name='BB Lower',
                        line=dict(color='gray', width=1, dash='dash'),
                        fill='tonexty',
                        fillcolor='rgba(128,128,128,0.1)',
                        showlegend=False
                    ),
                    row=1, col=1
                )
            
            # Trading signals
            if self.signals is not None:
                buy_signals = self.signals[self.signals['Action'] == 'BUY']
                sell_signals = self.signals[self.signals['Action'] == 'SELL']
                
                if len(buy_signals) > 0:
                    fig.add_trace(
                        go.Scatter(
                            x=buy_signals.index,
                            y=self.data.loc[buy_signals.index, 'Low'] * 0.98,
                            mode='markers',
                            name='Buy Signal',
                            marker=dict(symbol='triangle-up', size=12, color='green'),
                            text=[f"BUY: ${price:.2f}" for price in self.data.loc[buy_signals.index, 'Close']],
                            hovertemplate='<b>BUY SIGNAL</b><br>Price: $%{text}<br>Date: %{x}<extra></extra>'
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
                            marker=dict(symbol='triangle-down', size=12, color='red'),
                            text=[f"SELL: ${price:.2f}" for price in self.data.loc[sell_signals.index, 'Close']],
                            hovertemplate='<b>SELL SIGNAL</b><br>Price: $%{text}<br>Date: %{x}<extra></extra>'
                        ),
                        row=1, col=1
                    )
            
            # Volume
            volume_colors = ['green' if close >= open_price else 'red' 
                           for close, open_price in zip(self.data['Close'], self.data['Open'])]
            
            fig.add_trace(
                go.Bar(
                    x=self.data.index,
                    y=self.data['Volume'],
                    name='Volume',
                    marker_color=volume_colors,
                    opacity=0.7,
                    showlegend=False
                ),
                row=2, col=1
            )
            
            # RSI
            if 'RSI' in self.indicators:
                fig.add_trace(
                    go.Scatter(
                        x=self.data.index,
                        y=self.indicators['RSI'],
                        mode='lines',
                        name='RSI',
                        line=dict(color='purple', width=2),
                        showlegend=False
                    ),
                    row=3, col=1
                )
                
                # RSI levels
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1, opacity=0.7)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1, opacity=0.7)
                fig.add_hline(y=50, line_dash="dot", line_color="gray", row=3, col=1, opacity=0.5)
            
            # MACD
            if all(key in self.indicators for key in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
                fig.add_trace(
                    go.Scatter(
                        x=self.data.index,
                        y=self.indicators['MACD'],
                        mode='lines',
                        name='MACD',
                        line=dict(color='blue', width=2),
                        showlegend=False
                    ),
                    row=4, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=self.data.index,
                        y=self.indicators['MACD_Signal'],
                        mode='lines',
                        name='MACD Signal',
                        line=dict(color='red', width=2),
                        showlegend=False
                    ),
                    row=4, col=1
                )
                
                fig.add_trace(
                    go.Bar(
                        x=self.data.index,
                        y=self.indicators['MACD_Histogram'],
                        name='MACD Histogram',
                        marker_color='gray',
                        opacity=0.7,
                        showlegend=False
                    ),
                    row=4, col=1
                )
            
            # Stochastic
            if all(key in self.indicators for key in ['STOCH_K', 'STOCH_D']):
                fig.add_trace(
                    go.Scatter(
                        x=self.data.index,
                        y=self.indicators['STOCH_K'],
                        mode='lines',
                        name='%K',
                        line=dict(color='blue', width=2),
                        showlegend=False
                    ),
                    row=5, col=1
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=self.data.index,
                        y=self.indicators['STOCH_D'],
                        mode='lines',
                        name='%D',
                        line=dict(color='red', width=2),
                        showlegend=False
                    ),
                    row=5, col=1
                )
                
                # Stochastic levels
                fig.add_hline(y=80, line_dash="dash", line_color="red", row=5, col=1, opacity=0.7)
                fig.add_hline(y=20, line_dash="dash", line_color="green", row=5, col=1, opacity=0.7)
            
            # Update layout
            fig.update_layout(
                title=f'{ticker} - Interactive Trading Analysis Dashboard',
                xaxis_rangeslider_visible=False,
                height=900,
                showlegend=True,
                template='plotly_white',
                hovermode='x unified'
            )
            
            # Update y-axes labels
            fig.update_yaxes(title_text="Price ($)", row=1, col=1)
            fig.update_yaxes(title_text="Volume", row=2, col=1)
            fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
            fig.update_yaxes(title_text="MACD", row=4, col=1)
            fig.update_yaxes(title_text="Stochastic", row=5, col=1, range=[0, 100])
            
            print(f"✅ Interactive dashboard created for {ticker}")
            return fig
            
        except Exception as e:
            print(f"❌ Error creating interactive dashboard: {e}")
            return None
    
    def save_interactive_chart(self, fig: go.Figure, ticker: str, save_path: str = None) -> str:
        """
        Save interactive chart as HTML file
        
        Args:
            fig: Plotly Figure object
            ticker: Stock ticker symbol
            save_path: Path to save HTML file
            
        Returns:
            Path to saved HTML file
        """
        try:
            save_path = save_path or f'/workspace/tvTrading/charts/{ticker}_interactive.html'
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            fig.write_html(save_path, include_plotlyjs='cdn')
            print(f"✅ Interactive chart saved: {save_path}")
            return save_path
            
        except Exception as e:
            print(f"❌ Error saving interactive chart: {e}")
            return None
    
    def create_performance_dashboard(self, portfolio_data: pd.DataFrame) -> go.Figure:
        """
        Create portfolio performance dashboard
        
        Args:
            portfolio_data: DataFrame with portfolio performance metrics
            
        Returns:
            Plotly Figure object
        """
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Portfolio Value Over Time',
                    'Daily Returns Distribution',
                    'Signal Distribution',
                    'Monthly Performance'
                ),
                specs=[
                    [{"secondary_y": False}, {"type": "histogram"}],
                    [{"type": "pie"}, {"type": "bar"}]
                ]
            )
            
            # Portfolio value over time
            fig.add_trace(
                go.Scatter(
                    x=portfolio_data.index,
                    y=portfolio_data['Portfolio_Value'],
                    mode='lines',
                    name='Portfolio Value',
                    line=dict(color='green', width=3),
                    fill='tonexty',
                    fillcolor='rgba(0,255,136,0.1)'
                ),
                row=1, col=1
            )
            
            # Daily returns histogram
            fig.add_trace(
                go.Histogram(
                    x=portfolio_data['Daily_Return'],
                    name='Daily Returns',
                    nbinsx=50,
                    marker_color='blue',
                    opacity=0.7
                ),
                row=1, col=2
            )
            
            # Signal distribution pie chart
            if self.signals is not None:
                signal_counts = self.signals['Action'].value_counts()
                fig.add_trace(
                    go.Pie(
                        labels=signal_counts.index,
                        values=signal_counts.values,
                        name="Signal Distribution",
                        marker_colors=['green', 'gray', 'red']
                    ),
                    row=2, col=1
                )
            
            # Monthly performance
            monthly_returns = portfolio_data['Daily_Return'].resample('M').sum()
            colors = ['green' if ret > 0 else 'red' for ret in monthly_returns]
            
            fig.add_trace(
                go.Bar(
                    x=monthly_returns.index,
                    y=monthly_returns.values,
                    name='Monthly Returns',
                    marker_color=colors,
                    opacity=0.8
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                title='Portfolio Performance Dashboard',
                height=700,
                showlegend=True,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            print(f"❌ Error creating performance dashboard: {e}")
            return None



