

# 🎯 Trading Automation Platform

A comprehensive trading automation platform that bridges TradingView Pine Scripts with Alpaca brokerage for automated trading execution.

## 🏗️ Project Structure

```
tvTrading/
├── docs/                           # Documentation
│   ├── DEVELOPMENT_PLAN.md         # Complete development roadmap
│   ├── LOCAL_SIMULATION_PLAN.md    # Local simulation strategy
│   ├── CENTRALIZED_ARCHITECTURE.md # Single EC2 deployment guide
│   └── project-plan.md             # Original project requirements
├── src/                            # Source code
│   ├── backend/                    # Flask application & APIs
│   │   ├── app.py                  # Main Flask application
│   │   ├── trading_simulator.py    # Local trading simulation
│   │   └── requirements.txt        # Python dependencies
│   ├── frontend/                   # React dashboard (TBD)
│   ├── analytics/                  # Trading analytics & indicators
│   └── scripts/                    # Deployment & utility scripts
│       └── pine_script_template.pine # TradingView Pine Script template
├── bin/                            # Executable scripts
└── .openhands/                     # OpenHands microagents
    └── microagents/
        └── multi-team-trading-coordinator.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- TradingView Pro+ account
- Alpaca brokerage account

### Installation
```bash
# Clone repository
git clone https://github.com/randellconley-admin/tvTrading.git
cd tvTrading

# Install dependencies
pip install -r src/backend/requirements.txt

# Run local simulation
python src/backend/trading_simulator.py
```

## 🎯 Core Features

### 📊 **Multi-Library Trading Analytics**
- **TA-Lib**: 150+ technical indicators
- **mplfinance**: Professional static charts
- **Plotly**: Interactive web dashboards

### 🔄 **TradingView Integration**
- Pine Script templates for signal generation
- Webhook-based signal transmission
- Support for 2,400+ NYSE tickers

### 🏦 **Alpaca Brokerage Integration**
- Paper trading for testing
- Live trading execution
- Position sizing & risk management

### 📈 **Real-time Dashboard**
- Live signal monitoring
- Performance analytics
- Interactive charts

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Flask, PostgreSQL, Redis | Core API & data storage |
| **Analytics** | TA-Lib, mplfinance, Plotly | Technical analysis & visualization |
| **Frontend** | React, Plotly.js | Interactive dashboard |
| **Infrastructure** | Docker, Nginx, AWS | Deployment & hosting |

## 📋 Development Phases

1. **Phase 1**: Local simulation with TA-Lib, mplfinance, Plotly
2. **Phase 2**: Flask webhook application with Alpaca integration
3. **Phase 3**: React dashboard for real-time monitoring
4. **Phase 4**: TradingView Pine Script integration
5. **Phase 5**: Production deployment on AWS EC2

## 🎯 Teams & Microagent Coordination

This project uses OpenHands microagents for multi-team coordination:

- **Frontend Team**: React dashboard & user interface
- **Backend Team**: Flask APIs & webhook processing
- **Trading Analytics Team**: TA-Lib indicators & mplfinance charts
- **DevOps Team**: Docker deployment & AWS infrastructure

Activate with: `Teams: [your request]`

## 📊 Local Simulation

Run the trading simulator to test strategies locally:

```bash
python src/backend/trading_simulator.py
```

This generates:
- Technical analysis using TA-Lib
- Static charts with mplfinance
- Interactive dashboards with Plotly
- Simulated webhook payloads

## 🚀 Deployment

### Single EC2 Instance (Recommended)
```bash
# Deploy to AWS EC2
./bin/deploy.sh

# Access dashboard
https://your-domain.com
```

### Local Development
```bash
# Start with Docker Compose
docker-compose up -d

# Access locally
http://localhost:5000
```

## 📈 Performance Targets

- **Latency**: < 100ms webhook processing
- **Throughput**: 1000+ signals/hour
- **Uptime**: 99.9% availability
- **Accuracy**: 100% signal processing

## 🔒 Security

- SSL/TLS encryption
- API key encryption at rest
- Rate limiting & DDoS protection
- Regular security updates

## 📞 Support

- **Documentation**: `/docs` directory
- **Issues**: GitHub Issues
- **Microagent**: Use `Teams:` prefix for multi-team coordination

---

**Built with ❤️ using OpenHands Multi-Team Coordination**


