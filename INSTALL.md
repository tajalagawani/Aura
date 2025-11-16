# Aura Installation Guide

## Single Command Install

```bash
./install.sh
```

That's it! The installer handles everything.

## What the Installer Does

1. ✅ Checks Python 3.11+ requirement
2. ✅ Installs Aura package and dependencies
3. ✅ Creates `./assets` directory
4. ✅ Initializes monitoring for your machine
5. ✅ Collects initial metrics (5 seconds)
6. ✅ Shows you commands to try

## After Installation

The installer will create an AAV file for your machine at:
```
./assets/<your-hostname>.aav
```

You can immediately use these commands:

```bash
# View detailed status
aura status <your-hostname> --assets-dir ./assets

# View summary
aura status --summary --assets-dir ./assets

# Query for high resource usage
aura query --filter "memory > 70" --assets-dir ./assets

# Watch live updates
aura watch <your-hostname> --assets-dir ./assets
```

The installer outputs the exact commands with your hostname.

## Manual Installation

If you prefer manual installation:

```bash
# 1. Install package
pip install -e .

# 2. Create assets directory
mkdir -p ./assets

# 3. Initialize for your machine
python3 -c "
from aura.core.aav import AAVFile
import socket

hostname = socket.gethostname()
AAVFile.create_empty(
    file_path=f'./assets/{hostname}.aav',
    asset_id=hostname,
    asset_type='machine',
    asset_name=hostname
)
print(f'Created: ./assets/{hostname}.aav')
"

# 4. Collect initial metrics
python3 -c "
import asyncio
import socket
from aura.sensors import ComputeSensor, MemorySensor, StorageSensor

async def collect():
    hostname = socket.gethostname()
    aav_path = f'./assets/{hostname}.aav'

    sensors = [
        ComputeSensor(hostname, aav_path),
        MemorySensor(hostname, aav_path),
        StorageSensor(hostname, aav_path),
    ]

    tasks = [sensor.start() for sensor in sensors]
    try:
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=5.0)
    except asyncio.TimeoutError:
        for sensor in sensors:
            await sensor.stop()

asyncio.run(collect())
"
```

## Requirements

- **Python**: 3.11 or higher
- **OS**: Linux, macOS, or Windows
- **Disk Space**: ~50MB for package and dependencies
- **Memory**: Minimal (<10MB per asset)

## Verifying Installation

After installation, verify everything works:

```bash
# Check Aura version
aura version

# Validate installed files
aura validate --assets-dir ./assets

# View status
aura status --summary --assets-dir ./assets
```

## Troubleshooting

### Python version error

If you get a Python version error:

```bash
# Check your Python version
python3 --version

# Must be 3.11 or higher
# Install Python 3.11+ from python.org
```

### Command not found: aura

If `aura` command is not found:

```bash
# Reinstall
pip install -e .

# Or use full path
python3 -m aura.cli.main --help
```

### Permission denied on install.sh

```bash
# Make it executable
chmod +x install.sh
./install.sh
```

## Next Steps

After successful installation:

1. **View your machine's status:**
   ```bash
   aura status <hostname> --assets-dir ./assets
   ```

2. **Monitor additional machines:**
   See the "Monitor Additional Assets" section in README.md

3. **Integrate with AI agents:**
   See the "AI Agent Integration" section in README.md

4. **Production deployment:**
   See the "Production Deployment" section in README.md

## Uninstalling

To completely remove Aura:

```bash
# Uninstall package
pip uninstall aura

# Remove assets directory
rm -rf ./assets
```

## Support

If you encounter issues:

1. Check the [README.md](README.md) for documentation
2. Review [aura.md](aura.md) for detailed specifications
3. Open an issue on GitHub with error details
