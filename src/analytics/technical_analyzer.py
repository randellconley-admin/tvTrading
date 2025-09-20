


"""
Technical Analysis Engine using TA-Lib
Trading Analytics Team Implementation
"""

import pandas as pd
import numpy as np
import talib
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class TechnicalAnalyzer:
    """
    Core technical analysis engine using TA-Lib
    Simulates Pine Script technical analysis functions
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize with OHLCV data
        
        Args:
            data: DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume']
        """
        self.data = data.copy()
        self.high = data['High'].values
        self.low = data['Low'].values
        self.close = data['Close'].values
        self.open = data['Open'].values
        self.volume = data['Volume'].values
        self.indicators = {}
    
    def calculate_trend_indicators(self) -> Dict:
        """
        Calculate trend-following indicators
        Equivalent to Pine Script: ta.sma, ta.ema, ta.bb
        """
        indicators = {}
        
        try:
            # Simple Moving Averages
            indicators['SMA_5'] = talib.SMA(self.close, timeperiod=5)
            indicators['SMA_10'] = talib.SMA(self.close, timeperiod=10)
            indicators['SMA_20'] = talib.SMA(self.close, timeperiod=20)
            indicators['SMA_50'] = talib.SMA(self.close, timeperiod=50)
            indicators['SMA_200'] = talib.SMA(self.close, timeperiod=200)
            
            # Exponential Moving Averages
            indicators['EMA_12'] = talib.EMA(self.close, timeperiod=12)
            indicators['EMA_26'] = talib.EMA(self.close, timeperiod=26)
            indicators['EMA_50'] = talib.EMA(self.close, timeperiod=50)
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = talib.BBANDS(
                self.close, timeperiod=20, nbdevup=2, nbdevdn=2
            )
            indicators['BB_Upper'] = bb_upper
            indicators['BB_Middle'] = bb_middle
            indicators['BB_Lower'] = bb_lower
            indicators['BB_Width'] = (bb_upper - bb_lower) / bb_middle * 100
            
            # Parabolic SAR
            indicators['SAR'] = talib.SAR(self.high, self.low, acceleration=0.02, maximum=0.2)
            
            print("✅ Trend indicators calculated successfully")
            
        except Exception as e:
            print(f"❌ Error calculating trend indicators: {e}")
        
        return indicators
    
    def calculate_momentum_indicators(self) -> Dict:
        """
        Calculate momentum oscillators
        Equivalent to Pine Script: ta.rsi, ta.macd, ta.stoch
        """
        indicators = {}
        
        try:
            # RSI (Relative Strength Index)
            indicators['RSI'] = talib.RSI(self.close, timeperiod=14)
            indicators['RSI_Fast'] = talib.RSI(self.close, timeperiod=7)
            indicators['RSI_Slow'] = talib.RSI(self.close, timeperiod=21)
            
            # MACD (Moving Average Convergence Divergence)
            macd, macd_signal, macd_hist = talib.MACD(
                self.close, fastperiod=12, slowperiod=26, signalperiod=9
            )
            indicators['MACD'] = macd
            indicators['MACD_Signal'] = macd_signal
            indicators['MACD_Histogram'] = macd_hist
            
            # Stochastic Oscillator
            slowk, slowd = talib.STOCH(
                self.high, self.low, self.close,
                fastk_period=14, slowk_period=3, slowd_period=3
            )
            indicators['STOCH_K'] = slowk
            indicators['STOCH_D'] = slowd
            
            # Williams %R
            indicators['WILLR'] = talib.WILLR(self.high, self.low, self.close, timeperiod=14)
            
            # Commodity Channel Index
            indicators['CCI'] = talib.CCI(self.high, self.low, self.close, timeperiod=14)
            
            # Rate of Change
            indicators['ROC'] = talib.ROC(self.close, timeperiod=10)
            
            print("✅ Momentum indicators calculated successfully")
            
        except Exception as e:
            print(f"❌ Error calculating momentum indicators: {e}")
        
        return indicators
    
    def calculate_volatility_indicators(self) -> Dict:
        """
        Calculate volatility indicators
        Equivalent to Pine Script: ta.atr, ta.tr
        """
        indicators = {}
        
        try:
            # Average True Range
            indicators['ATR'] = talib.ATR(self.high, self.low, self.close, timeperiod=14)
            indicators['ATR_Fast'] = talib.ATR(self.high, self.low, self.close, timeperiod=7)
            indicators['ATR_Slow'] = talib.ATR(self.high, self.low, self.close, timeperiod=21)
            
            # True Range
            indicators['TRANGE'] = talib.TRANGE(self.high, self.low, self.close)
            
            # Normalized Average True Range
            indicators['NATR'] = talib.NATR(self.high, self.low, self.close, timeperiod=14)
            
            print("✅ Volatility indicators calculated successfully")
            
        except Exception as e:
            print(f"❌ Error calculating volatility indicators: {e}")
        
        return indicators
    
    def calculate_volume_indicators(self) -> Dict:
        """
        Calculate volume-based indicators
        Equivalent to Pine Script volume analysis
        """
        indicators = {}
        
        try:
            # On-Balance Volume
            indicators['OBV'] = talib.OBV(self.close, self.volume)
            
            # Accumulation/Distribution Line
            indicators['AD'] = talib.AD(self.high, self.low, self.close, self.volume)
            
            # Chaikin A/D Oscillator
            indicators['ADOSC'] = talib.ADOSC(
                self.high, self.low, self.close, self.volume,
                fastperiod=3, slowperiod=10
            )
            
            # Volume Rate of Change
            indicators['VROC'] = talib.ROC(self.volume, timeperiod=10)
            
            # Volume Moving Average
            indicators['Volume_SMA'] = talib.SMA(self.volume, timeperiod=20)
            
            print("✅ Volume indicators calculated successfully")
            
        except Exception as e:
            print(f"❌ Error calculating volume indicators: {e}")
        
        return indicators
    
    def detect_candlestick_patterns(self) -> Dict:
        """
        Detect candlestick patterns using TA-Lib
        Equivalent to Pine Script pattern recognition
        """
        patterns = {}
        
        try:
            # Reversal Patterns
            patterns['DOJI'] = talib.CDLDOJI(self.open, self.high, self.low, self.close)
            patterns['HAMMER'] = talib.CDLHAMMER(self.open, self.high, self.low, self.close)
            patterns['HANGING_MAN'] = talib.CDLHANGINGMAN(self.open, self.high, self.low, self.close)
            patterns['SHOOTING_STAR'] = talib.CDLSHOOTINGSTAR(self.open, self.high, self.low, self.close)
            patterns['INVERTED_HAMMER'] = talib.CDLINVERTEDHAMMER(self.open, self.high, self.low, self.close)
            
            # Engulfing Patterns
            patterns['ENGULFING'] = talib.CDLENGULFING(self.open, self.high, self.low, self.close)
            patterns['DARK_CLOUD'] = talib.CDLDARKCLOUDCOVER(self.open, self.high, self.low, self.close)
            patterns['PIERCING'] = talib.CDLPIERCING(self.open, self.high, self.low, self.close)
            
            # Star Patterns
            patterns['MORNING_STAR'] = talib.CDLMORNINGSTAR(self.open, self.high, self.low, self.close)
            patterns['EVENING_STAR'] = talib.CDLEVENINGSTAR(self.open, self.high, self.low, self.close)
            patterns['DOJI_STAR'] = talib.CDLDOJISTAR(self.open, self.high, self.low, self.close)
            
            # Three-Candle Patterns
            patterns['THREE_WHITE_SOLDIERS'] = talib.CDL3WHITESOLDIERS(self.open, self.high, self.low, self.close)
            patterns['THREE_BLACK_CROWS'] = talib.CDL3BLACKCROWS(self.open, self.high, self.low, self.close)
            patterns['THREE_INSIDE'] = talib.CDL3INSIDE(self.open, self.high, self.low, self.close)
            patterns['THREE_OUTSIDE'] = talib.CDL3OUTSIDE(self.open, self.high, self.low, self.close)
            
            print("✅ Candlestick patterns detected successfully")
            
        except Exception as e:
            print(f"❌ Error detecting candlestick patterns: {e}")
        
        return patterns
    
    def calculate_all_indicators(self) -> Dict:
        """
        Calculate all technical indicators at once
        Returns comprehensive technical analysis data
        """
        print("📊 Calculating comprehensive technical analysis...")
        
        all_indicators = {}
        
        # Calculate all indicator categories
        all_indicators.update(self.calculate_trend_indicators())
        all_indicators.update(self.calculate_momentum_indicators())
        all_indicators.update(self.calculate_volatility_indicators())
        all_indicators.update(self.calculate_volume_indicators())
        all_indicators.update(self.detect_candlestick_patterns())
        
        # Store for later use
        self.indicators = all_indicators
        
        print(f"✅ Calculated {len(all_indicators)} technical indicators")
        return all_indicators
    
    def generate_trading_signals(self) -> pd.DataFrame:
        """
        Generate trading signals based on technical indicators
        Simulates Pine Script strategy logic
        """
        if not self.indicators:
            self.calculate_all_indicators()
        
        signals = pd.DataFrame(index=self.data.index)
        
        # Initialize signal columns
        signals['Trend_Signal'] = 0
        signals['Momentum_Signal'] = 0
        signals['Volume_Signal'] = 0
        signals['Pattern_Signal'] = 0
        signals['Combined_Signal'] = 0
        
        try:
            # Trend Signals (Moving Average Crossovers)
            sma_10 = self.indicators.get('SMA_10', np.zeros(len(self.data)))
            sma_20 = self.indicators.get('SMA_20', np.zeros(len(self.data)))
            
            signals['Trend_Signal'] = np.where(
                (sma_10 > sma_20) & (self.close > sma_10), 1,  # Bullish trend
                np.where((sma_10 < sma_20) & (self.close < sma_10), -1, 0)  # Bearish trend
            )
            
            # Momentum Signals (RSI + MACD)
            rsi = self.indicators.get('RSI', np.full(len(self.data), 50))
            macd = self.indicators.get('MACD', np.zeros(len(self.data)))
            macd_signal = self.indicators.get('MACD_Signal', np.zeros(len(self.data)))
            
            signals['Momentum_Signal'] = np.where(
                (rsi < 30) & (macd > macd_signal), 1,  # Oversold + MACD bullish
                np.where((rsi > 70) & (macd < macd_signal), -1, 0)  # Overbought + MACD bearish
            )
            
            # Volume Signals (OBV trend)
            obv = self.indicators.get('OBV', np.zeros(len(self.data)))
            obv_sma = talib.SMA(obv, timeperiod=10)
            
            signals['Volume_Signal'] = np.where(
                obv > obv_sma, 1,  # Volume supporting uptrend
                np.where(obv < obv_sma, -1, 0)  # Volume supporting downtrend
            )
            
            # Pattern Signals (Candlestick patterns)
            bullish_patterns = (
                self.indicators.get('HAMMER', np.zeros(len(self.data))) +
                self.indicators.get('MORNING_STAR', np.zeros(len(self.data))) +
                self.indicators.get('ENGULFING', np.zeros(len(self.data)))
            )
            
            bearish_patterns = (
                self.indicators.get('SHOOTING_STAR', np.zeros(len(self.data))) +
                self.indicators.get('EVENING_STAR', np.zeros(len(self.data))) +
                self.indicators.get('DARK_CLOUD', np.zeros(len(self.data)))
            )
            
            signals['Pattern_Signal'] = np.where(
                bullish_patterns > 0, 1,
                np.where(bearish_patterns < 0, -1, 0)
            )
            
            # Combined Signal (weighted average)
            signals['Combined_Signal'] = (
                signals['Trend_Signal'] * 0.4 +
                signals['Momentum_Signal'] * 0.3 +
                signals['Volume_Signal'] * 0.2 +
                signals['Pattern_Signal'] * 0.1
            )
            
            # Generate final buy/sell signals
            signals['Action'] = np.where(
                signals['Combined_Signal'] > 0.5, 'BUY',
                np.where(signals['Combined_Signal'] < -0.5, 'SELL', 'HOLD')
            )
            
            print(f"✅ Generated trading signals for {len(signals)} periods")
            
        except Exception as e:
            print(f"❌ Error generating trading signals: {e}")
        
        return signals
    
    def get_latest_analysis(self) -> Dict:
        """
        Get latest technical analysis summary
        Perfect for real-time dashboard display
        """
        if not self.indicators:
            self.calculate_all_indicators()
        
        latest_idx = -1
        
        analysis = {
            'timestamp': self.data.index[latest_idx].isoformat(),
            'price': {
                'current': float(self.close[latest_idx]),
                'open': float(self.open[latest_idx]),
                'high': float(self.high[latest_idx]),
                'low': float(self.low[latest_idx]),
                'volume': float(self.volume[latest_idx])
            },
            'trend': {
                'sma_10': float(self.indicators.get('SMA_10', [0])[latest_idx]),
                'sma_20': float(self.indicators.get('SMA_20', [0])[latest_idx]),
                'ema_12': float(self.indicators.get('EMA_12', [0])[latest_idx]),
                'bb_upper': float(self.indicators.get('BB_Upper', [0])[latest_idx]),
                'bb_lower': float(self.indicators.get('BB_Lower', [0])[latest_idx])
            },
            'momentum': {
                'rsi': float(self.indicators.get('RSI', [50])[latest_idx]),
                'macd': float(self.indicators.get('MACD', [0])[latest_idx]),
                'macd_signal': float(self.indicators.get('MACD_Signal', [0])[latest_idx]),
                'stoch_k': float(self.indicators.get('STOCH_K', [50])[latest_idx])
            },
            'volatility': {
                'atr': float(self.indicators.get('ATR', [0])[latest_idx]),
                'bb_width': float(self.indicators.get('BB_Width', [0])[latest_idx])
            },
            'volume': {
                'obv': float(self.indicators.get('OBV', [0])[latest_idx]),
                'volume_sma': float(self.indicators.get('Volume_SMA', [0])[latest_idx])
            }
        }
        
        return analysis
    
    def calculate_support_resistance(self, window: int = 20) -> Dict:
        """
        Calculate support and resistance levels
        Uses pivot points and price action analysis
        """
        try:
            # Calculate pivot points
            high_rolling = pd.Series(self.high).rolling(window=window, center=True)
            low_rolling = pd.Series(self.low).rolling(window=window, center=True)
            
            # Find local maxima (resistance) and minima (support)
            resistance_levels = []
            support_levels = []
            
            for i in range(window, len(self.high) - window):
                if self.high[i] == high_rolling.iloc[i:i+1].max().iloc[0]:
                    resistance_levels.append(self.high[i])
                
                if self.low[i] == low_rolling.iloc[i:i+1].min().iloc[0]:
                    support_levels.append(self.low[i])
            
            # Get most significant levels (by frequency)
            resistance_counts = pd.Series(resistance_levels).value_counts()
            support_counts = pd.Series(support_levels).value_counts()
            
            return {
                'resistance_levels': resistance_counts.head(5).index.tolist(),
                'support_levels': support_counts.head(5).index.tolist(),
                'current_price': float(self.close[-1])
            }
            
        except Exception as e:
            print(f"❌ Error calculating support/resistance: {e}")
            return {'resistance_levels': [], 'support_levels': [], 'current_price': 0}


