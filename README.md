# Eth-Watchdog

Real-time blockchain observability tool for Ethereum RPC nodes with automated Discord alerts and comprehensive latency tracking.

[![CI Pipeline](https://github.com/kasoares/Eth-Watchdog/actions/workflows/ci.yml/badge.svg)](https://github.com/kasoares/Eth-Watchdog/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](Dockerfile)

## Overview

Eth-Watchdog is a lightweight monitoring solution for Ethereum RPC endpoints that provides real-time observability metrics via Discord. Built for reliability monitoring in staking operations, validator infrastructure, and DApp backends.

**Key Features:**
- RPC health checks every 10 seconds
- Minute-by-minute status reports with detailed metrics
- Latency tracking (min/max/average per period)
- Uptime percentage calculation
- Block height synchronization monitoring
- Instant failure alerts
- Containerized deployment

## Quick Start

### Prerequisites

- Docker
- Discord webhook ([create here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks))

### Installation

```bash
git clone https://github.com/kasoares/Eth-Watchdog.git
cd Eth-Watchdog
cp .env.example .env
# Edit .env with your Discord webhook URL
```

### Configuration

Edit `.env` file:
```env
DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN
RPC_URL=https://eth.llamarpc.com  # Optional, defaults to public endpoint
```

### Run

```bash
# Build
docker build -t eth-watchdog:latest .

# Run (foreground)
docker run --env-file .env eth-watchdog:latest

# Run (background with auto-restart)
docker run -d --name watchdog --restart unless-stopped --env-file .env eth-watchdog:latest

# View logs
docker logs -f watchdog
```

## Observability Metrics

### Discord Notifications

**1. Startup Alert**
```
ETH-WATCHDOG ALERT
Eth-Watchdog started and monitoring Ethereum network
Initial Check: Block 23,828,212 | Latency: 179.28ms
```

**2. Status Report (Every Minute)**
```
ETH-WATCHDOG ALERT
STATUS REPORT - Last Minute
Total Checks: 15 | Period: 6/6 | Uptime: 100.0%
Latency: 310.27ms (min: 172.31ms | max: 407.85ms)
Current Block: 23,828,224
```

**Metrics Explained:**
- **Total Checks**: Cumulative health checks since startup
- **Period**: Successful checks / Total checks in last minute
- **Uptime**: Percentage of successful checks in the period
- **Latency**: Average response time with min/max bounds
- **Current Block**: Latest Ethereum block height observed

**3. Failure Alerts**
```
ETH-WATCHDOG ALERT
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

[OK] [2025-11-18 16:55:00] Block: 23,828,212 | Latency: 179.28ms
[OK] [2025-11-18 16:55:10] Block: 23,828,212 | Latency: 165.45ms
[ERROR] [2025-11-18 16:55:20] Timeout after 15023.45ms
[OK] [2025-11-18 16:55:30] Block: 23,828,213 | Latency: 198.76ms
```

## Configuration

### Timing Adjustments

Edit `app.py`:
```python
CHECK_INTERVAL = 10              # Health check frequency (seconds)
STATUS_REPORT_INTERVAL = 6       # Report every N checks (6 = 1 minute)
```

### RPC Endpoints

Supports any EVM-compatible JSON-RPC endpoint:

```env
# Ethereum Mainnet
RPC_URL=https://eth.llamarpc.com
RPC_URL=https://ethereum.publicnode.com

# Polygon
RPC_URL=https://polygon-bor-rpc.publicnode.com

# Private Providers
RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
RPC_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY

# Your Own Node
RPC_URL=http://localhost:8545
```

## Architecture

### Monitoring Flow

```
┌─────────────────┐
│  Eth-Watchdog   │
│   (Container)   │
└────────┬────────┘
         │
         ├─── Every 10s ────> JSON-RPC: eth_blockNumber
         │                    └─> Measure latency
         │                    └─> Track block height
         │
         └─── Every 60s ────> Discord Webhook
                              └─> Period metrics
                              └─> Uptime calculation
```

### Technology Stack

- **Python 3.10**: Lightweight runtime
- **Requests**: Direct JSON-RPC communication (no web3.py overhead)
- **Docker**: Containerized deployment with non-root user
- **GitHub Actions**: Automated CI/CD pipeline

### Design Philosophy

**Why `requests` over `web3.py`?**
- 10x smaller Docker image (~15MB vs ~150MB)
- Direct JSON-RPC control
- Sub-100ms startup time
- Sufficient for health checks

## Monitoring Best Practices

### What Uptime Percentage Means

- **100%**: All checks in the last minute succeeded
- **83.3%**: 5 out of 6 checks succeeded (1 failure)
- **0%**: All checks failed (critical issue)

### Interpreting Latency

- **< 200ms**: Excellent
- **200-500ms**: Good
- **500-1000ms**: Acceptable
- **> 1000ms**: Investigate (network issues or node overload)

### Alert Thresholds

The tool alerts on:
- Connection timeouts (> 15s)
- HTTP errors (non-200 status)
- JSON-RPC errors
- Connection failures

## Use Cases

- **Validator Operations**: Monitor RPC uptime for validator clients
- **DApp Infrastructure**: Ensure backend RPC reliability
- **Multi-Region Monitoring**: Deploy multiple instances across regions
- **SLA Tracking**: Historical uptime data for compliance
- **Incident Response**: Immediate alerts for node failures

## Production Deployment

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  eth-watchdog:
    build: .
    restart: unless-stopped
    env_file: .env
    container_name: eth-watchdog
```

Run:
```bash
docker-compose up -d
```

### Azure Container Instances

```bash
az container create \
  --resource-group eth-monitoring \
  --name eth-watchdog \
  --image youracr.azurecr.io/eth-watchdog:latest \
  --environment-variables \
    DISCORD_WEBHOOK='your-webhook-url' \
    RPC_URL='https://eth.llamarpc.com' \
  --restart-policy Always
```

## CI/CD Pipeline

Automated GitHub Actions workflow:
- Docker image build validation
- Python syntax checking
- Automated testing on push

## Troubleshooting

**Container stops immediately:**
```bash
docker logs watchdog  # Check for errors
```

**No Discord messages:**
- Verify webhook URL is correct
- Check Discord server permissions
- Review container logs for HTTP errors

**High latency:**
- Try different RPC endpoint
- Check network connectivity
- Verify endpoint rate limits

## Future Enhancements

- Prometheus metrics export
- Multiple endpoint monitoring
- Grafana dashboard integration
- Historical data persistence
- Telegram/Slack support

## License

MIT License - See LICENSE for details

## Author

Kaiky Soares  
GitHub: [@kasoares](https://github.com/kasoares)
