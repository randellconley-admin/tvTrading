---
name: Multi-Team Trading Coordinator
type: knowledge
version: 1.0.0
agent: CodeActAgent
triggers: []
---

# Multi-Team Trading Coordinator Microagent

This microagent provides coordination and routing capabilities for managing multiple enterprise full-stack development teams specialized in stock brokerage and financial trading applications.

## Overview

The Multi-Team Trading Coordinator is designed to orchestrate and manage multiple specialized teams, each consisting of:
- Full enterprise full-stack development team
- Stock brokerage specialists with expertise in:
  - mplfinance (matplotlib finance plotting)
  - Plotly (interactive financial charts)
  - TA-Lib (Technical Analysis Library)

## Team Router with Communication Output

The coordinator includes a sophisticated routing system that shows real-time communication between agents and teams:

### Router Features
- **Message Routing**: Routes tasks and communications between teams
- **Real-time Output**: Shows all inter-team communications with timestamps
- **Task Assignment**: Automatically assigns tasks based on requirements analysis
- **Status Monitoring**: Tracks team status and project progress
- **Coordination Events**: Manages cross-team collaboration

### Communication Flow
```
[12:34:56.789] 🎯 ROUTER: Multi-Team Trading Router initialized
[12:34:56.790] 👥 ROUTER: Teams ready - Frontend, Backend, Trading Analytics, DevOps
[12:34:56.791] 🚀 COORDINATOR: Starting project 'TradingPlatform_v1'
[12:34:56.792] 🔍 COORDINATOR: Analyzing requirement - 'Create trading dashboard UI'
[12:34:56.793] 🎯 COORDINATOR: Assigning to frontend team
[12:34:56.794] 📡 ROUTER: coordinator → frontend (task_assignment): New task for project
[12:34:56.795] 📨 FRONTEND received: New task for project 'TradingPlatform_v1'
[12:34:56.796] 🎨 FRONTEND: Starting UI development for 'Create trading dashboard UI'
```

## Team Capabilities

### Full-Stack Development Team
- **Frontend**: React, Vue.js, Angular with real-time trading interfaces
- **Backend**: Node.js, Python (FastAPI/Django), Java Spring Boot
- **Database**: PostgreSQL, MongoDB, Redis for real-time data
- **DevOps**: Docker, Kubernetes, CI/CD pipelines
- **Cloud**: AWS, Azure, GCP deployment and scaling

### Stock Brokerage Team
- **Technical Analysis**: TA-Lib integration for indicators and patterns
- **Data Visualization**: 
  - mplfinance for candlestick charts and technical overlays
  - Plotly for interactive dashboards and real-time charts
- **Market Data**: Real-time feeds, historical data processing
- **Trading Systems**: Order management, risk management, portfolio tracking
- **Compliance**: Regulatory requirements and audit trails

## Coordination Responsibilities

### Project Routing
- Analyze incoming requirements and route to appropriate teams
- Determine resource allocation based on project complexity
- Coordinate cross-team dependencies and integrations

### Technical Architecture
- Design scalable trading platform architectures
- Ensure proper separation of concerns between teams
- Implement microservices patterns for trading systems

### Quality Assurance
- Coordinate testing strategies across teams
- Ensure financial data accuracy and system reliability
- Implement proper error handling and failover mechanisms

### Deployment Coordination
- Orchestrate multi-team deployments
- Manage environment configurations
- Coordinate database migrations and data synchronization

## Key Technologies and Libraries

### Financial Analysis Stack
```python
# Core financial libraries
import mplfinance as mpf
import plotly.graph_objects as go
import plotly.express as px
import talib as ta
import pandas as pd
import numpy as np
```

### Trading Platform Components
- **Real-time Data Processing**: WebSocket connections, message queues
- **Chart Rendering**: Canvas-based charts, SVG graphics
- **Order Management**: RESTful APIs, event-driven architecture
- **Risk Management**: Real-time position monitoring, automated alerts

## Best Practices

### Code Organization
- Maintain separate repositories for different trading modules
- Use consistent coding standards across all teams
- Implement proper version control and branching strategies

### Data Management
- Ensure data consistency across all trading systems
- Implement proper backup and disaster recovery
- Maintain audit trails for all trading activities

### Security
- Implement proper authentication and authorization
- Secure API endpoints and data transmission
- Regular security audits and penetration testing

### Performance
- Optimize for low-latency trading operations
- Implement proper caching strategies
- Monitor system performance and scalability

## Team Coordination Patterns

### Message-Based Communication
Teams communicate through a centralized router that handles task assignment, status updates, and coordination:

```python
# Team communication example
class TeamRouter:
    def route_task(self, requirement, project):
        if "chart" in requirement.lower():
            return "trading_analytics"  # mplfinance, Plotly, TA-Lib
        elif "api" in requirement.lower():
            return "backend"           # FastAPI, Django
        elif "ui" in requirement.lower():
            return "frontend"          # React, Vue, Angular
        else:
            return "devops"            # Deployment, Infrastructure
```

### Real-Time Coordination
The router provides live output showing team interactions:
- Task assignments with automatic team selection
- Progress updates from each specialized team
- Cross-team coordination for complex features
- Resource sharing and dependency management

## Integration Patterns

### Team Communication
- Use standardized APIs between team components
- Implement event-driven architecture for real-time updates
- Maintain clear documentation and interface contracts
- Router-based message passing between teams

### Data Flow
- Centralized market data distribution via Redis
- Consistent data models across all teams
- Real-time synchronization of trading positions
- Shared data repositories for team collaboration

### Monitoring and Alerting
- Comprehensive logging across all systems
- Real-time monitoring of trading operations
- Automated alerting for system issues and trading anomalies
- Team status tracking and progress monitoring

## Error Handling and Limitations

### Common Issues
- Market data feed interruptions
- High-frequency trading latency requirements
- Regulatory compliance complexities
- Cross-team coordination challenges

### Mitigation Strategies
- Implement redundant data feeds
- Use proper circuit breakers and fallback mechanisms
- Maintain comprehensive testing environments
- Regular team synchronization meetings

## Usage Examples

### Coordinating a New Trading Feature
1. Analyze requirements and identify affected teams
2. Design system architecture and data flow
3. Coordinate development timelines across teams
4. Implement integration testing strategies
5. Orchestrate deployment and monitoring

### Managing Technical Debt
1. Assess technical debt across all team codebases
2. Prioritize refactoring efforts based on business impact
3. Coordinate refactoring schedules to minimize disruption
4. Ensure proper testing and validation of changes

This microagent serves as the central coordination point for complex trading platform development, ensuring all teams work together effectively while maintaining the high standards required for financial trading systems.
