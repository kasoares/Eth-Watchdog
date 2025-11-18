"""
Eth-Watchdog - Ethereum Node Health Monitor
Monitora a disponibilidade de nós RPC Ethereum e envia alertas via Discord
"""

import os
import time
import requests
from datetime import datetime
from statistics import mean


# Configurações via variáveis de ambiente
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
RPC_URL = os.getenv("RPC_URL", "https://eth.llamarpc.com")

# Intervalo entre verificações (segundos)
CHECK_INTERVAL = 10

# Frequência de relatórios de status (a cada N verificações bem-sucedidas)
STATUS_REPORT_INTERVAL = 5  # 6 verificações × 10s = 60s (1 minuto)

# Histórico de latências para o período atual de relatório
current_period_latencies = []


def send_discord_alert(message: str) -> None:
    """
    Sends alert notification to Discord webhook.
    
    Args:
        message: Message to be sent
    """
    if not DISCORD_WEBHOOK:
        print(f"[ALERT] {message} (Discord webhook not configured)")
        return
    
    try:
        payload = {
            "content": f"**ETH-WATCHDOG ALERT**\n{message}",
            "username": "Eth-Watchdog Bot"
        }
        response = requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
        
        if response.status_code == 204:
            print(f"[OK] Alert sent to Discord: {message}")
        else:
            print(f"[ERROR] Failed to send alert. Status: {response.status_code}")
            
    except Exception as e:
        print(f"[ERROR] Error sending Discord notification: {e}")


def check_eth_status() -> dict:
    """
    Checks Ethereum node status through JSON-RPC call.
    Uses eth_blockNumber method to verify connectivity and synchronization.
    
    Returns:
        dict: Status information including success, latency, and block height
    """
    start_time = time.time()
    
    try:
        # JSON-RPC payload to get current block number
        # Using pure requests instead of heavy libs (web3.py) to optimize container performance
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }
        
        response = requests.post(RPC_URL, json=payload, timeout=15)
        latency = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for errors in JSON-RPC response
            if "error" in data:
                error_msg = data["error"].get("message", "Unknown error")
                print(f"[ERROR] [{get_timestamp()}] RPC Error: {error_msg} | Latency: {latency:.2f}ms")
                send_discord_alert(f"Ethereum node returned error: {error_msg}")
                return {"success": False, "latency": latency, "block_height": None}
            
            # Convert hexadecimal result to integer
            block_height_hex = data.get("result", "0x0")
            block_height = int(block_height_hex, 16)
            
            # Add latency to current period
            current_period_latencies.append(latency)
            
            print(f"[OK] [{get_timestamp()}] Block: {block_height:,} | Latency: {latency:.2f}ms")
            return {"success": True, "latency": latency, "block_height": block_height}
        else:
            latency = (time.time() - start_time) * 1000
            print(f"[ERROR] [{get_timestamp()}] HTTP {response.status_code} | Latency: {latency:.2f}ms")
            send_discord_alert(f"Ethereum Node Unreachable! (HTTP {response.status_code})")
            return {"success": False, "latency": latency, "block_height": None}
            
    except requests.exceptions.Timeout:
        latency = (time.time() - start_time) * 1000
        print(f"[TIMEOUT] [{get_timestamp()}] Timeout after {latency:.2f}ms")
        send_discord_alert("Ethereum Node Unreachable! (Timeout)")
        return {"success": False, "latency": latency, "block_height": None}
        
    except requests.exceptions.ConnectionError:
        latency = (time.time() - start_time) * 1000
        print(f"[ERROR] [{get_timestamp()}] Connection error | Latency: {latency:.2f}ms")
        send_discord_alert("Ethereum Node Unreachable! (Connection Error)")
        return {"success": False, "latency": latency, "block_height": None}
        
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        print(f"[ERROR] [{get_timestamp()}] Unexpected error: {type(e).__name__} - {e}")
        send_discord_alert(f"Ethereum Node Unreachable! (Error: {type(e).__name__})")
        return {"success": False, "latency": latency, "block_height": None}


def get_timestamp() -> str:
    """Returns formatted timestamp for logs"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def send_status_report(check_count: int, success_count: int, period_latencies: list, last_block: int):
    """
    Sends periodic status report to Discord with observability metrics.
    
    Args:
        check_count: Total number of checks performed
        success_count: Number of successful checks in current period
        period_latencies: Latencies from current reporting period
        last_block: Last observed block height
    """
    uptime_percentage = (success_count / check_count * 100) if check_count > 0 else 0
    avg_latency = mean(period_latencies) if period_latencies else 0
    min_latency = min(period_latencies) if period_latencies else 0
    max_latency = max(period_latencies) if period_latencies else 0
    
    report = (
        f"**STATUS REPORT**\n"
        f"Checks: {check_count} | Success: {success_count} | Uptime: {uptime_percentage:.1f}%\n"
        f"Latency: {avg_latency:.2f}ms (min: {min_latency:.2f}ms | max: {max_latency:.2f}ms)\n"
        f"Last Block: {last_block:,}"
    )
    
    send_discord_alert(report)


def main():
    """
    Main monitoring loop.
    Periodically checks node status and maintains logs to stdout (Docker).
    """
    print("=" * 60)
    print("ETH-WATCHDOG - Ethereum Node Monitor")
    print("=" * 60)
    print(f"RPC URL: {RPC_URL}")
    print(f"Check Interval: {CHECK_INTERVAL}s")
    print(f"Status Report Every: {STATUS_REPORT_INTERVAL} checks")
    print(f"Discord Alerts: {'Enabled' if DISCORD_WEBHOOK else 'Disabled'}")
    print("=" * 60)
    print()
    
    # Send startup notification with initial health check
    initial_check = check_eth_status()
    if initial_check["success"]:
        send_discord_alert(
            f"Eth-Watchdog started and monitoring Ethereum network\n"
            f"Initial Check: Block {initial_check['block_height']:,} | Latency: {initial_check['latency']:.2f}ms"
        )
    else:
        send_discord_alert("Eth-Watchdog started but initial health check failed!")
    
    # Monitoring metrics
    check_count = 0
    success_count = 0
    period_success_count = 0
    last_block_height = 0
    
    # Infinite monitoring loop
    # Keeps container active and performs periodic checks
    while True:
        try:
            result = check_eth_status()
            check_count += 1
            
            if result["success"]:
                success_count += 1
                period_success_count += 1
                last_block_height = result["block_height"]
                
                # Send periodic status report
                if period_success_count >= STATUS_REPORT_INTERVAL:
                    send_status_report(
                        check_count, 
                        period_success_count,
                        current_period_latencies.copy(),
                        last_block_height
                    )
                    # Reset period counters
                    period_success_count = 0
                    current_period_latencies.clear()
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n[SHUTDOWN] Monitoring interrupted by user")
            send_discord_alert(f"Eth-Watchdog shutdown - Final stats: {success_count}/{check_count} successful checks")
            break
            
        except Exception as e:
            # Failsafe: capture any unforeseen errors to keep service running
            print(f"[CRITICAL] [{get_timestamp()}] Critical error in main loop: {e}")
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
