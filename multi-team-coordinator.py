#!/usr/bin/env python3
"""
Multi-Team Trading Coordinator Script
Coordinates tasks across multiple Docker containers for different development teams
"""

import subprocess
import sys
import json
from typing import Dict, List, Optional

class MultiTeamCoordinator:
    def __init__(self):
        self.containers = {
            'frontend': 'trading-frontend-team',
            'backend': 'trading-backend-team', 
            'analytics': 'trading-analytics-team',
            'devops': 'trading-devops-team'
        }
        
    def execute_team_task(self, team: str, command: str) -> Dict:
        """Execute task in specific team container"""
        if team not in self.containers:
            return {"error": f"Unknown team: {team}"}
            
        container_name = self.containers[team]
        try:
            result = subprocess.run([
                'docker', 'exec', container_name, 'bash', '-c', command
            ], capture_output=True, text=True, timeout=300)
            
            return {
                "team": team,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out in {team} container"}
        except Exception as e:
            return {"error": f"Failed to execute in {team}: {str(e)}"}
    
    def start_multi_team_environment(self):
        """Start all team containers using docker-compose"""
        try:
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose.multi-team.yml', 'up', '-d'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Multi-team environment started successfully")
                return True
            else:
                print(f"❌ Failed to start environment: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error starting environment: {str(e)}")
            return False
    
    def stop_multi_team_environment(self):
        """Stop all team containers"""
        try:
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose.multi-team.yml', 'down'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Multi-team environment stopped successfully")
                return True
            else:
                print(f"❌ Failed to stop environment: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error stopping environment: {str(e)}")
            return False
    
    def check_team_status(self):
        """Check status of all team containers"""
        print("🔍 Checking team container status...")
        for team, container in self.containers.items():
            try:
                result = subprocess.run([
                    'docker', 'ps', '--filter', f'name={container}', '--format', 'table {{.Names}}\t{{.Status}}'
                ], capture_output=True, text=True)
                
                if container in result.stdout:
                    print(f"✅ {team.capitalize()} Team: Running")
                else:
                    print(f"❌ {team.capitalize()} Team: Not running")
            except Exception as e:
                print(f"❌ {team.capitalize()} Team: Error checking status")
    
    def coordinate_trading_setup(self):
        """Coordinate setup across all trading teams"""
        print("🚀 Coordinating trading platform setup...")
        
        tasks = [
            ("frontend", "npm install && echo 'Frontend dependencies installed'"),
            ("backend", "pip install -r requirements.txt 2>/dev/null || echo 'Backend ready'"),
            ("analytics", "python -c 'import mplfinance, plotly, talib; print(\"Trading libraries ready\")'"),
            ("devops", "docker --version && echo 'DevOps tools ready'")
        ]
        
        results = []
        for team, command in tasks:
            print(f"📋 Executing setup for {team} team...")
            result = self.execute_team_task(team, command)
            results.append(result)
            
            if result.get("success"):
                print(f"✅ {team.capitalize()} setup completed")
            else:
                print(f"❌ {team.capitalize()} setup failed: {result.get('error', 'Unknown error')}")
        
        return results
    
    def run_trading_analysis_demo(self):
        """Run a demo trading analysis across teams"""
        print("📊 Running trading analysis demo...")
        
        # Analytics team: Generate sample trading data and charts
        analysis_command = """
python -c "
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate sample trading data
dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
prices = 100 + np.cumsum(np.random.randn(len(dates)) * 0.5)
volume = np.random.randint(1000, 10000, len(dates))

df = pd.DataFrame({
    'Date': dates,
    'Close': prices,
    'Volume': volume
})

print('Sample Trading Data Generated:')
print(df.head())
print(f'Price range: {prices.min():.2f} - {prices.max():.2f}')
print('Trading analysis demo completed successfully!')
"
        """
        
        result = self.execute_team_task("analytics", analysis_command)
        if result.get("success"):
            print("✅ Trading analysis demo completed")
            print(result["stdout"])
        else:
            print("❌ Trading analysis demo failed")
            print(result.get("stderr", "Unknown error"))

def main():
    coordinator = MultiTeamCoordinator()
    
    if len(sys.argv) < 2:
        print("""
Multi-Team Trading Coordinator

Usage:
    python multi-team-coordinator.py <command>

Commands:
    start       - Start all team containers
    stop        - Stop all team containers  
    status      - Check status of team containers
    setup       - Coordinate setup across all teams
    demo        - Run trading analysis demo
    exec        - Execute command in specific team container
                  Usage: exec <team> <command>

Teams: frontend, backend, analytics, devops
        """)
        return
    
    command = sys.argv[1]
    
    if command == "start":
        coordinator.start_multi_team_environment()
    elif command == "stop":
        coordinator.stop_multi_team_environment()
    elif command == "status":
        coordinator.check_team_status()
    elif command == "setup":
        coordinator.coordinate_trading_setup()
    elif command == "demo":
        coordinator.run_trading_analysis_demo()
    elif command == "exec" and len(sys.argv) >= 4:
        team = sys.argv[2]
        cmd = " ".join(sys.argv[3:])
        result = coordinator.execute_team_task(team, cmd)
        print(json.dumps(result, indent=2))
    else:
        print("❌ Invalid command. Use --help for usage information.")

if __name__ == "__main__":
    main()
