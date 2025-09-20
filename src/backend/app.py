
"""
Trading Automation Platform - Core Flask Application
Multi-team coordinated development for TradingView -> Alpaca integration
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json
import logging
from datetime import datetime
import os
from alpaca_trade_api import REST, TimeFrame
import pandas as pd

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///trading_platform.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Initialize extensions
db = SQLAlchemy(app)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Alpaca API configuration
ALPACA_PAPER_KEY = os.getenv('ALPACA_PAPER_KEY')
ALPACA_PAPER_SECRET = os.getenv('ALPACA_PAPER_SECRET')
ALPACA_LIVE_KEY = os.getenv('ALPACA_LIVE_KEY')
ALPACA_LIVE_SECRET = os.getenv('ALPACA_LIVE_SECRET')

class TradingSignal(db.Model):
    """Database model for trading signals from TradingView"""
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), nullable=False)
    signal_type = db.Column(db.String(10), nullable=False)  # BUY/SELL
    trading_mode = db.Column(db.String(20), nullable=False)  # Paper/Production
    risk_amount = db.Column(db.Float, nullable=False)
    entry_price = db.Column(db.Float)
    stop_loss = db.Column(db.Float)
    take_profit = db.Column(db.Float)
    strategy = db.Column(db.String(50))
    timeframe = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    raw_payload = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'signal_type': self.signal_type,
            'trading_mode': self.trading_mode,
            'risk_amount': self.risk_amount,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'strategy': self.strategy,
            'timeframe': self.timeframe,
            'timestamp': self.timestamp.isoformat()
        }

class TradeExecution(db.Model):
    """Database model for trade executions via Alpaca"""
    id = db.Column(db.Integer, primary_key=True)
    signal_id = db.Column(db.Integer, db.ForeignKey('trading_signal.id'), nullable=False)
    alpaca_order_id = db.Column(db.String(50))
    status = db.Column(db.String(20))  # pending, filled, cancelled, rejected
    executed_price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    execution_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    signal = db.relationship('TradingSignal', backref=db.backref('executions', lazy=True))

class TradingEngine:
    """Core trading logic coordinated by Trading Analytics Team"""
    
    def __init__(self):
        self.paper_api = None
        self.live_api = None
        self._initialize_alpaca_clients()
    
    def _initialize_alpaca_clients(self):
        """Initialize Alpaca API clients for paper and live trading"""
        try:
            if ALPACA_PAPER_KEY and ALPACA_PAPER_SECRET:
                self.paper_api = REST(
                    ALPACA_PAPER_KEY, 
                    ALPACA_PAPER_SECRET, 
                    base_url='https://paper-api.alpaca.markets'
                )
                logger.info("✅ Paper trading API initialized")
            
            if ALPACA_LIVE_KEY and ALPACA_LIVE_SECRET:
                self.live_api = REST(
                    ALPACA_LIVE_KEY, 
                    ALPACA_LIVE_SECRET, 
                    base_url='https://api.alpaca.markets'
                )
                logger.info("✅ Live trading API initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Alpaca APIs: {e}")
    
    def calculate_position_size(self, risk_amount, entry_price, stop_loss):
        """
        Calculate position size based on fixed risk amount
        Trading Analytics Team implementation using risk management
        """
        if not stop_loss or stop_loss <= 0:
            logger.warning("Invalid stop loss, using default 2% risk")
            stop_loss = entry_price * 0.98
        
        risk_per_share = abs(entry_price - stop_loss)
        if risk_per_share <= 0:
            return 0
        
        position_size = int(risk_amount / risk_per_share)
        logger.info(f"📊 Position size calculated: {position_size} shares for ${risk_amount} risk")
        return position_size
    
    def execute_trade(self, signal_data):
        """
        Execute trade based on signal data
        Coordinates between Backend Team (API) and Trading Analytics Team (logic)
        """
        try:
            # Select appropriate API based on trading mode
            api = self.paper_api if signal_data['trading_mode'].lower() == 'paper' else self.live_api
            
            if not api:
                raise Exception(f"API not configured for {signal_data['trading_mode']} mode")
            
            # Calculate position size
            position_size = self.calculate_position_size(
                signal_data['risk_amount'],
                signal_data.get('entry_price', 0),
                signal_data.get('stop_loss', 0)
            )
            
            if position_size <= 0:
                raise Exception("Invalid position size calculated")
            
            # Prepare order
            side = 'buy' if signal_data['signal_type'].upper() == 'BUY' else 'sell'
            
            order_data = {
                'symbol': signal_data['ticker'],
                'qty': position_size,
                'side': side,
                'type': 'market',
                'time_in_force': 'day'
            }
            
            # Add stop loss if provided
            if signal_data.get('stop_loss'):
                order_data['stop_loss'] = {'stop_price': signal_data['stop_loss']}
            
            # Add take profit if provided
            if signal_data.get('take_profit'):
                order_data['take_profit'] = {'limit_price': signal_data['take_profit']}
            
            # Execute order
            order = api.submit_order(**order_data)
            
            logger.info(f"🚀 Order executed: {order.id} for {signal_data['ticker']}")
            
            return {
                'success': True,
                'order_id': order.id,
                'status': order.status,
                'quantity': position_size
            }
            
        except Exception as e:
            logger.error(f"❌ Trade execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Initialize trading engine
trading_engine = TradingEngine()

@app.route('/webhook', methods=['POST'])
def handle_trading_signal():
    """
    Main webhook endpoint for TradingView signals
    Backend Team implementation with Trading Analytics Team coordination
    """
    try:
        # Parse incoming JSON from TradingView
        signal_data = request.get_json()
        
        if not signal_data:
            return jsonify({'error': 'No JSON data received'}), 400
        
        logger.info(f"📡 Received signal: {signal_data.get('ticker')} - {signal_data.get('signal_type')}")
        
        # Validate required fields
        required_fields = ['ticker', 'signal_type', 'trading_mode', 'risk_amount']
        for field in required_fields:
            if field not in signal_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Store signal in database
        signal = TradingSignal(
            ticker=signal_data['ticker'],
            signal_type=signal_data['signal_type'],
            trading_mode=signal_data['trading_mode'],
            risk_amount=signal_data['risk_amount'],
            entry_price=signal_data.get('entry_price'),
            stop_loss=signal_data.get('stop_loss'),
            take_profit=signal_data.get('take_profit'),
            strategy=signal_data.get('strategy'),
            timeframe=signal_data.get('timeframe'),
            raw_payload=json.dumps(signal_data)
        )
        
        db.session.add(signal)
        db.session.commit()
        
        # Execute trade
        execution_result = trading_engine.execute_trade(signal_data)
        
        # Store execution result
        execution = TradeExecution(
            signal_id=signal.id,
            alpaca_order_id=execution_result.get('order_id'),
            status=execution_result.get('status', 'failed'),
            quantity=execution_result.get('quantity', 0)
        )
        
        db.session.add(execution)
        db.session.commit()
        
        response = {
            'success': True,
            'signal_id': signal.id,
            'execution': execution_result
        }
        
        logger.info(f"✅ Signal processed successfully: {signal.id}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"❌ Webhook processing failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/signals', methods=['GET'])
def get_signals():
    """
    API endpoint to retrieve trading signals
    Frontend Team integration point
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        signals = TradingSignal.query.order_by(TradingSignal.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'signals': [signal.to_dict() for signal in signals.items],
            'total': signals.total,
            'pages': signals.pages,
            'current_page': page
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to retrieve signals: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance', methods=['GET'])
def get_performance():
    """
    Performance analytics endpoint
    Trading Analytics Team implementation with mplfinance/Plotly integration
    """
    try:
        # Get performance metrics
        total_signals = TradingSignal.query.count()
        successful_executions = TradeExecution.query.filter_by(status='filled').count()
        
        # Calculate success rate
        success_rate = (successful_executions / total_signals * 100) if total_signals > 0 else 0
        
        # Get recent signals by ticker
        recent_signals = db.session.query(
            TradingSignal.ticker,
            db.func.count(TradingSignal.id).label('count')
        ).group_by(TradingSignal.ticker).limit(10).all()
        
        return jsonify({
            'total_signals': total_signals,
            'successful_executions': successful_executions,
            'success_rate': round(success_rate, 2),
            'top_tickers': [{'ticker': ticker, 'count': count} for ticker, count in recent_signals]
        })
        
    except Exception as e:
        logger.error(f"❌ Failed to get performance data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for DevOps Team monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'paper_api': 'connected' if trading_engine.paper_api else 'disconnected',
        'live_api': 'connected' if trading_engine.live_api else 'disconnected'
    })

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("📊 Database tables created")
    
    # Start Flask application
    logger.info("🚀 Trading Automation Platform starting...")
    app.run(host='0.0.0.0', port=5000, debug=True)

