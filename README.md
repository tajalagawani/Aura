# Aura - Universal AI Asset Authority

**Real-time infrastructure context for AI agents.**

Aura gives AI systems environmental awareness through lightweight sensors that monitor computational assets in real-time. Get sub-millisecond infrastructure context for intelligent decision-making.

## Quick Install

```bash
# Clone the repository
git clone <your-repo-url>
cd aura

# Run installer (does everything)
./install.sh
```

That's it! The installer will:
- ✅ Check Python 3.11+ requirement
- ✅ Install Aura package
- ✅ Create assets directory
- ✅ Initialize monitoring for your machine
- ✅ Collect initial metrics

## Usage

After installation, try these commands:

```bash
# View live status of your machine
aura status $(hostname) --assets-dir ./assets

# View summary of all monitored assets
aura status --summary --assets-dir ./assets

# Query for high resource usage
aura query --filter "memory > 70" --assets-dir ./assets

# Watch live updates (Ctrl+C to stop)
aura watch $(hostname) --assets-dir ./assets

# Validate file integrity
aura validate --assets-dir ./assets
```

## Beautiful CLI Output

```
📊 MyMachine - Live Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Updated: 2 seconds ago

💻 COMPUTE
   CPU:         45.2% █████████░░░░░░░░░░░ Normal
   Load:      1.23
   Processes: 147

🧠 MEMORY
   Usage:      68.1% █████████████░░░░░░░ Normal
   Available: 2.0 GB
   Trend:     Stable

💾 STORAGE
   Usage:      67.8% █████████████░░░░░░░ Normal
   Free:      15.6 GB
   I/O:       Read 2.3 MB/s, Write 1.8 MB/s

🌐 NETWORK
   Connections: 127 active

✅ SERVICES
   Health:    HEALTHY ✓

💡 RECOMMENDATIONS
   All systems operating normally. No action needed.
```

## Python API

Use Aura in your Python code:

```python
from aura.core.aav import AAVFile

# Read AAV file
aav = AAVFile("./assets/my-server.aav")
data = aav.read()

# Check metrics
cpu = data['compute']['real_time']['cpu_percent']
memory = data['memory']['real_time']['usage_percent']

if cpu < 70 and memory < 80:
    print("✅ Safe to deploy")
else:
    print("⚠️  High resource usage - wait")
```

## AI Agent Integration

```python
from aura.ai.context_client import AuraClient
import asyncio

async def check_deployment():
    client = AuraClient(assets_dir="./assets")

    # AI makes informed decision
    result = await client.is_safe_to_deploy("my-server")

    if result["safe"]:
        print("✅", result["recommendation"])
    else:
        print("⚠️", result["recommendation"])

asyncio.run(check_deployment())
```

## Monitor Additional Assets

To monitor more machines/containers:

```python
from aura.core.aav import AAVFile
from aura.sensors import ComputeSensor, MemorySensor, StorageSensor
import asyncio

async def monitor_asset(asset_id, asset_type="server"):
    # Create AAV file
    AAVFile.create_empty(
        file_path=f"./assets/{asset_id}.aav",
        asset_id=asset_id,
        asset_type=asset_type
    )

    # Start sensors
    sensors = [
        ComputeSensor(asset_id, f"./assets/{asset_id}.aav"),
        MemorySensor(asset_id, f"./assets/{asset_id}.aav"),
        StorageSensor(asset_id, f"./assets/{asset_id}.aav"),
    ]

    tasks = [sensor.start() for sensor in sensors]
    await asyncio.gather(*tasks)

# Run monitoring
asyncio.run(monitor_asset("web-server-01"))
```

## Features

- ✅ **Real-Time Metrics** - CPU, Memory, Disk, Network, Services
- ✅ **Intelligent Updates** - Change-driven, not polling
- ✅ **Human-Readable** - TOML files you can edit
- ✅ **AI-Optimized** - Sub-millisecond queries
- ✅ **Self-Healing** - Auto-repair corrupted files
- ✅ **Scalable** - 1 to 10,000+ assets
- ✅ **Beautiful CLI** - Rich terminal interface

## Architecture

```
AI Agent → Cache (Redis) → .AAV Files → Sensors → Assets
                ↓
            Guardian (validates & repairs)
```

## 5 Built-in Sensors

1. **ComputeSensor** - CPU, load, processes
2. **MemorySensor** - RAM, leak detection
3. **StorageSensor** - Disk, I/O, mount points
4. **NetworkSensor** - Connections, traffic
5. **ServicesSensor** - Health, uptime, dependencies

## File Format

AAV (AI Authority Vector) files are human-readable TOML:

```toml
[metadata]
format_version = "2.0.0"
asset_id = "web-server-01"
last_updated = "2025-11-16T18:01:56Z"

[asset]
id = "web-server-01"
type = "server"
status = "running"

[compute.real_time]
cpu_percent = 45.2
load_average = [1.23, 1.15, 1.08]
process_count = 47

[memory.real_time]
usage_percent = 68.1
available_mb = 2048.0

[storage.real_time]
disk_usage_percent = 67.8
free_gb = 15.6
```

## Requirements

- Python 3.11+
- psutil (system metrics)
- toml (file format)
- click (CLI)
- pydantic (validation)
- redis (optional, for caching)

All dependencies are installed automatically by `./install.sh`

## Production Deployment

For production with multiple assets:

1. **Install on each machine:**
   ```bash
   ./install.sh
   ```

2. **Centralize AAV files (optional):**
   ```bash
   # Use shared storage for ./assets directory
   # All machines write to same location
   ```

3. **Enable Redis caching (optional):**
   ```python
   from aura.ai.context_client import AuraClient

   client = AuraClient(
       assets_dir="./assets",
       cache_enabled=True,
       redis_host="localhost"
   )
   ```

4. **Run Guardian for validation:**
   ```python
   from aura.guardian.distributed import DistributedGuardian

   guardian = DistributedGuardian(
       shard_id=0,
       total_shards=3,
       assets_dir="./assets",
       validation_interval=30
   )

   await guardian.start()
   ```

## Documentation

- [Full Specification](aura.md) - Complete system design
- [Implementation Plan](PRODUCTION_IMPLEMENTATION_PLAN.md) - Production roadmap
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

## CLI Command Reference

### Status Commands

```bash
# Detailed view of single asset
aura status <asset-id> --assets-dir ./assets

# Summary of all assets
aura status --summary --assets-dir ./assets

# Default view (first 5 assets)
aura status --assets-dir ./assets
```

### Query Commands

```bash
# Find high CPU
aura query --filter "cpu > 80" --assets-dir ./assets

# Find high memory
aura query --filter "memory > 70" --assets-dir ./assets
```

### Watch Command

```bash
# Live updates every 5 seconds
aura watch <asset-id> --assets-dir ./assets

# Custom interval
aura watch <asset-id> --assets-dir ./assets --interval 10
```

### Validation Commands

```bash
# Validate all files
aura validate --assets-dir ./assets

# Check deployment safety
aura deploy-check <asset-id> --assets-dir ./assets
```

### Other Commands

```bash
# Show version
aura version

# Help
aura --help
```

## Uninstall

```bash
pip uninstall aura
rm -rf ./assets
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Built for the AI community**

Making AI reliable through environmental awareness.
