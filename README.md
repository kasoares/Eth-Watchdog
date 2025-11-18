# Eth-Watchdog

Real-time monitoring tool for Ethereum RPC nodes with automated Discord alerts and latency tracking.

[![CI Pipeline](https://github.com/kasoares/Eth-Watchdog/actions/workflows/ci.yml/badge.svg)](https://github.com/kasoares/Eth-Watchdog/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](Dockerfile)

## What It Does

Eth-Watchdog monitors Ethereum RPC endpoints every 10 seconds and sends detailed status reports to Discord every minute. It tracks:
- Node availability and uptime
- Block height synchronization
- Response latency (current, min, max, average per period)
- Connection failures and timeouts

Perfect for monitoring staking infrastructure, validator nodes, or any Ethereum RPC endpoint.

## Why Use This

**Problem:** Running validators or DApps requires reliable RPC access. When nodes fail, you lose money.

**Solution:** Get instant alerts on Discord when something goes wrong, plus regular status updates showing your node is healthy.

## Quick Start

### Prerequisites

- Docker installed
- Discord webhook URL ([create one here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks))

### Setup

1. Clone and configure:
```bash
git clone https://github.com/kasoares/Eth-Watchdog.git
cd Eth-Watchdog
cp .env.example .env
```

2. Edit `.env` with your Discord webhook:
```env
DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN
RPC_URL=https://eth.llamarpc.com  # Optional
```

3. Build and run:
```bash
docker build -t eth-watchdog:latest .
docker run --env-file .env eth-watchdog:latest
```

For background execution:
```bash
docker run -d --name watchdog --restart unless-stopped --env-file .env eth-watchdog:latest
```

View logs:
```bash
docker logs -f watchdog
```

## What You'll See

### Discord Messages

**Startup:**
```
Eth-Watchdog started and monitoring Ethereum network
```

**Every Minute (Status Report):**
```
STATUS REPORT
Checks: 6 | Success: 6 | Uptime: 100.0%
Latency: 125.43ms (min: 98.21ms | max: 156.78ms)
Last Block: 18,500,234
```

**On Failure:**
```
Ethereum Node Unreachable! (Timeout)
```

### Terminal Logs

```
============================================================
ETH-WATCHDOG - Ethereum Node Monitor
============================================================
RPC URL: https://eth.llamarpc.com
Check Interval: 10s
Status Report Every: 6 checks
Discord Alerts: Enabled
============================================================

[OK] [2025-11-18 12:00:00] Block: 18,500,234 | Latency: 120.45ms
[OK] [2025-11-18 12:00:10] Block: 18,500,234 | Latency: 115.32ms
```

## Configuration

### Timing Settings

Edit `app.py` to adjust:
```python
CHECK_INTERVAL = 10              # Check every 10 seconds
STATUS_REPORT_INTERVAL = 6       # Report every 6 checks (1 minute)
```

### Different RPC Endpoints

Works with any EVM-compatible chain:
```env
# Ethereum mainnet
RPC_URL=https://eth.llamarpc.com

# Polygon
RPC_URL=https://polygon-bor-rpc.publicnode.com

# Your own node
RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
```

## Technical Details

### Stack

- **Python 3.10**: Lightweight, async-capable
- **Docker**: Containerized deployment
- **GitHub Actions**: Automated CI/CD
- **JSON-RPC**: Direct blockchain communication

### Why Not web3.py?

```python
# web3.py: ~50MB, heavy dependencies
from web3 import Web3

# This project: ~5MB, direct control
import requests
```

**Benefits:**
- 10x smaller Docker image
- Faster startup
- Only what we need for health checks

### Security

- Runs as non-root user (UID 1000)
- Integrated Docker healthcheck
- No sensitive data in logs
- Environment-based configuration

## CI/CD Pipeline

GitHub Actions automatically:
1. Builds Docker image on every push
2. Validates Python syntax
3. Runs basic import tests
4. Checks for common code issues

## Use Cases

- **Validator Monitoring**: Ensure your RPC endpoint stays healthy
- **Infrastructure Observability**: Track node performance over time
- **Incident Response**: Get alerted immediately when nodes fail
- **SLA Monitoring**: Track uptime and latency metrics

## Future Improvements

- Prometheus metrics export
- Multiple node monitoring
- Historical data persistence
- Web dashboard
- Telegram/Slack integration

## License

MIT License - See LICENSE file for details.

## Author

Kaiky Soares  
GitHub: [@kasoares](https://github.com/kasoares)
