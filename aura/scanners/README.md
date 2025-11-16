# Aura Scanners - Infrastructure Discovery System

The Aura scanner system automatically discovers computational assets across your infrastructure and creates AAV monitoring files for each discovered asset.

## Available Scanners

### 1. SystemScanner
Discovers the host system itself as an asset.

```python
from aura.scanners import SystemScanner

scanner = SystemScanner(assets_dir="./assets")
count = await scanner.discover_and_instrument()
```

**Discovers:**
- System hostname and FQDN
- Platform (Linux, macOS, Windows)
- CPU cores and frequency
- Total memory and disk
- Network interfaces
- System uptime

### 2. PortScanner
Discovers listening ports and services.

```python
from aura.scanners import PortScanner

scanner = PortScanner(
    assets_dir="./assets",
    include_stats=True,
    track_connections=True
)
count = await scanner.discover_and_instrument()
```

**Discovers:**
- All listening TCP ports
- Service identification (HTTP, SSH, MySQL, etc.)
- Process names and PIDs
- Connection statistics (established, time_wait, etc.)

**Features:**
- Identifies 30+ common services
- Tracks connection counts per port
- Process-based service detection
- Connection state tracking

### 3. ProcessScanner
Discovers running processes.

```python
from aura.scanners import ProcessScanner

scanner = ProcessScanner(
    assets_dir="./assets",
    min_cpu_percent=1.0,      # Only processes using >= 1% CPU
    min_memory_mb=100.0,      # Or >= 100MB memory
    exclude_system=True       # Skip root processes
)
count = await scanner.discover_and_instrument()
```

**Discovers:**
- Process ID and name
- CPU and memory usage
- Username and status
- Command line arguments

**Filters:**
- Minimum CPU threshold
- Minimum memory threshold
- System process exclusion

### 4. DockerScanner
Discovers Docker containers.

```python
from aura.scanners import DockerScanner

scanner = DockerScanner(assets_dir="./assets")
count = await scanner.discover_and_instrument()
```

**Discovers:**
- Container ID and name
- Image name
- Container status
- Labels and metadata

**Requirements:**
```bash
pip install docker
```

### 5. KubernetesScanner
Discovers Kubernetes pods.

```python
from aura.scanners import KubernetesScanner

scanner = KubernetesScanner(
    assets_dir="./assets",
    namespace="default"
)
count = await scanner.discover_and_instrument()
```

**Discovers:**
- Pod name and namespace
- Labels
- Phase (Running, Pending, etc.)
- Node assignment
- Pod IP address

**Requirements:**
```bash
pip install kubernetes
```

### 6. VMScanner
Discovers virtual machines from hypervisors.

```python
from aura.scanners import VMScanner

scanner = VMScanner(
    assets_dir="./assets",
    hypervisor="auto"  # auto, vmware, virtualbox, kvm
)
count = await scanner.discover_and_instrument()
```

**Supported Hypervisors:**
- **VirtualBox**: Local VMs
- **KVM**: Linux virtualization
- **VMware**: vCenter/ESXi (requires credentials)

**Requirements:**
```bash
# VirtualBox
pip install pyvirtualbox

# KVM
pip install libvirt-python

# VMware
pip install pyvmomi
```

### 7. CloudScanner
Discovers cloud instances.

```python
from aura.scanners import CloudScanner

scanner = CloudScanner(
    assets_dir="./assets",
    cloud_provider="auto",  # auto, aws, azure, gcp
    region="us-east-1"      # Optional
)
count = await scanner.discover_and_instrument()
```

**Supported Providers:**
- **AWS EC2**: Instances across all regions
- **Azure VMs**: Virtual machines
- **GCP Compute Engine**: Instances across zones

**Requirements:**
```bash
# AWS
pip install boto3
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx

# Azure
pip install azure-identity azure-mgmt-compute
export AZURE_SUBSCRIPTION_ID=xxx

# GCP
pip install google-cloud-compute
export GCP_PROJECT_ID=xxx
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

## CLI Usage

The scanners can be used via the CLI:

```bash
# Run all scanners
aura scan all --assets-dir ./assets

# Scan specific resources
aura scan system
aura scan ports --include-stats
aura scan processes --min-cpu 5.0
aura scan docker
aura scan kubernetes --namespace production
aura scan vms --hypervisor kvm
aura scan cloud --provider aws --region us-east-1

# Get help
aura scan --help
aura scan ports --help
```

## How Scanners Work

### 1. Discovery Phase
Each scanner:
- Connects to its target system (Docker API, K8s API, cloud API, etc.)
- Queries for available assets
- Collects metadata for each asset

### 2. Instrumentation Phase
For each discovered asset:
- Creates a unique asset ID
- Generates an AAV file in the assets directory
- Populates with initial metadata
- Enables continuous monitoring

### 3. AAV File Creation
```python
# Example: Docker container discovered
{
    "id": "container-abc123def456",
    "name": "web-server",
    "type": "container",
    "metadata": {
        "container_id": "abc123def456",
        "image": "nginx:latest",
        "status": "running",
        "labels": {...}
    }
}

# Creates: ./assets/container-abc123def456.aav
```

## Base Scanner Architecture

All scanners inherit from `BaseScanner`:

```python
from aura.scanners.base_scanner import BaseScanner

class CustomScanner(BaseScanner):
    async def scan(self) -> List[Dict[str, Any]]:
        """Implement discovery logic."""
        assets = []

        # Your discovery code here
        for item in discovered_items:
            assets.append({
                "id": f"custom-{item.id}",
                "name": item.name,
                "type": "custom",
                "metadata": {...}
            })

        return assets
```

The base scanner provides:
- `discover_and_instrument()` - Main entry point
- `_create_aav_file()` - AAV file creation
- `get_discovered_assets()` - Access to results
- `get_summary()` - Statistics

## Production Usage

### Continuous Discovery
Run scanners periodically to discover new assets:

```bash
# Cron job: Run every 5 minutes
*/5 * * * * cd /opt/aura && aura scan all
```

### Integration with Monitoring
After discovery, the monitoring service picks up new AAV files:

```python
# Monitoring service automatically monitors all AAV files
from aura.service.monitor import AuraMonitor

monitor = AuraMonitor(assets_dir="./assets")
await monitor.start()  # Monitors all discovered assets
```

### Multi-Environment Discovery
Scan across environments:

```bash
# Production
aura scan all --assets-dir /var/aura/prod/assets

# Staging
aura scan all --assets-dir /var/aura/staging/assets

# Development
aura scan all --assets-dir /var/aura/dev/assets
```

## Error Handling

All scanners gracefully handle:
- Missing dependencies (logs warning, returns empty list)
- Permission errors (falls back to partial data)
- API failures (logs error, continues with other assets)
- Credential issues (logs warning, skips provider)

```python
try:
    import docker
except ImportError:
    logger.warning("Docker library not installed")
    return []

try:
    containers = client.containers.list()
except Exception as e:
    logger.error(f"Docker scan failed: {e}")
    return []
```

## Performance

- **Async/Await**: All scanners are async for concurrent operation
- **Batch Processing**: Can process thousands of assets
- **Minimal Overhead**: Only queries metadata, not metrics
- **Parallel Execution**: Can run multiple scanners simultaneously

```python
# Run scanners in parallel
scanners = [
    SystemScanner(),
    DockerScanner(),
    KubernetesScanner(),
    PortScanner(),
]

results = await asyncio.gather(*[
    scanner.discover_and_instrument()
    for scanner in scanners
])
```

## Security

- **Read-Only**: Scanners only read, never modify infrastructure
- **Credential Management**: Uses system credentials (AWS CLI, kubectl, etc.)
- **Permission Aware**: Gracefully handles permission errors
- **No Root Required**: Most scanners work without root (with reduced data)

## Troubleshooting

### Scanner finds 0 assets
```bash
# Check if service is running
systemctl status docker
kubectl get pods

# Check credentials
aws sts get-caller-identity
gcloud auth list

# Check permissions
ls -la /var/run/docker.sock
```

### Permission denied errors
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Run with sudo (last resort)
sudo aura scan docker
```

### Missing dependencies
```bash
# Install all optional dependencies
pip install docker kubernetes boto3 azure-identity google-cloud-compute libvirt-python pyvirtualbox
```

## Examples

### Full Infrastructure Discovery
```python
import asyncio
from aura.scanners import *

async def discover_all():
    assets_dir = "./assets"

    # Create all scanners
    scanners = [
        SystemScanner(assets_dir),
        PortScanner(assets_dir),
        ProcessScanner(assets_dir, min_cpu_percent=5.0),
        DockerScanner(assets_dir),
        KubernetesScanner(assets_dir),
        CloudScanner(assets_dir, cloud_provider="aws"),
    ]

    # Run all in parallel
    results = await asyncio.gather(*[
        scanner.discover_and_instrument()
        for scanner in scanners
    ])

    total = sum(results)
    print(f"Discovered {total} assets")

asyncio.run(discover_all())
```

### Port Statistics
```python
from aura.scanners import PortScanner

scanner = PortScanner()
await scanner.scan()

# Get all port stats
stats = scanner.get_all_port_stats()
print(f"Total ports: {stats['total_ports']}")
print(f"Top ports: {stats['top_ports']}")

# Get specific port details
port_details = scanner.get_port_details(80)
print(f"Port 80 has {port_details['stats']['established']} established connections")
```

### Cloud Discovery with Metrics
```python
from aura.scanners import CloudScanner

scanner = CloudScanner(cloud_provider="aws", region="us-east-1")
await scanner.discover_and_instrument()

# Get metrics for specific instance
metrics = scanner.get_instance_metrics("i-1234567890abcdef0", "aws")
print(f"CPU: {metrics['cpu_utilization']}%")
```

## Next Steps

After discovery:
1. AAV files are created in assets directory
2. Start monitoring service: `systemctl start aura-monitor`
3. View dashboard: `http://localhost:8080`
4. Query assets: `aura status --summary`
5. Watch specific asset: `aura watch <asset-id>`
