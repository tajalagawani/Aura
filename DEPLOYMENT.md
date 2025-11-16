# Aura Deployment Guide

## Quick Deploy (3 Commands)

```bash
git clone https://github.com/tajalagawani/Aura.git
cd Aura
./install.sh
```

Done! Aura is now monitoring your machine.

## What Just Happened

The installer automatically:
1. ✅ Checked Python 3.11+ requirement
2. ✅ Installed Aura and all dependencies
3. ✅ Created `./assets/` directory
4. ✅ Created AAV file for your machine: `./assets/<hostname>.aav`
5. ✅ Started sensors and collected initial metrics
6. ✅ Validated everything works

## Verify Installation

```bash
# Check version
aura version

# View your machine's status
aura status $(hostname) --assets-dir ./assets

# Validate files
aura validate --assets-dir ./assets
```

## Example Output

After installation, you can run:

```bash
aura status $(hostname) --assets-dir ./assets
```

You'll see:

```
📊 YourMachine - Live Status
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

## Deploy to Multiple Machines

To monitor multiple machines:

### Option 1: Install on Each Machine

```bash
# On each machine:
git clone https://github.com/tajalagawani/Aura.git
cd Aura
./install.sh
```

Each machine will create its own AAV file in `./assets/`

### Option 2: Shared Storage (Recommended for Production)

```bash
# Machine 1:
git clone https://github.com/tajalagawani/Aura.git
cd Aura
./install.sh

# Use shared storage (NFS, S3, etc.) for assets
export ASSETS_DIR="/shared/storage/aura-assets"
mkdir -p $ASSETS_DIR

# Machine 2, 3, N:
cd Aura
export ASSETS_DIR="/shared/storage/aura-assets"
./install.sh
```

Now all machines write to the same `assets` directory.

## Production Architecture

For production with 100+ assets:

```
┌─────────────────────────────────────────────────┐
│                 Load Balancer                   │
└───────────────────┬─────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
    ┌───▼───┐               ┌───▼───┐
    │ Web   │               │ API   │
    │ Nodes │               │ Nodes │
    └───┬───┘               └───┬───┘
        │                       │
        └───────────┬───────────┘
                    │
            ┌───────▼────────┐
            │  Shared Storage│
            │  (AAV Files)   │
            └───────┬────────┘
                    │
            ┌───────▼────────┐
            │ Guardian Cluster│
            │ (3 shards)     │
            └───────┬────────┘
                    │
            ┌───────▼────────┐
            │  Redis Cache   │
            └────────────────┘
```

### Step 1: Shared Storage

Setup NFS or S3-compatible storage:

```bash
# Using NFS
sudo mkdir -p /mnt/aura-assets
sudo mount -t nfs nfs-server:/exports/aura /mnt/aura-assets

# Using S3 (with s3fs)
s3fs aura-bucket /mnt/aura-assets -o iam_role=auto
```

### Step 2: Install on All Nodes

```bash
# On each node:
git clone https://github.com/tajalagawani/Aura.git
cd Aura

# Point to shared storage
export ASSETS_DIR="/mnt/aura-assets"
./install.sh
```

### Step 3: Deploy Guardian Cluster

Create `guardian.py`:

```python
import asyncio
from aura.guardian.distributed import DistributedGuardian

async def run_guardian(shard_id, total_shards=3):
    guardian = DistributedGuardian(
        shard_id=shard_id,
        total_shards=total_shards,
        assets_dir="/mnt/aura-assets",
        validation_interval=30,
        repair_enabled=True
    )

    await guardian.start()

if __name__ == "__main__":
    import sys
    shard_id = int(sys.argv[1])
    asyncio.run(run_guardian(shard_id))
```

Run 3 Guardian instances:

```bash
# Terminal 1 (Guardian 0)
python guardian.py 0

# Terminal 2 (Guardian 1)
python guardian.py 1

# Terminal 3 (Guardian 2)
python guardian.py 2
```

### Step 4: Enable Redis Caching

```bash
# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Use cached client in your code
from aura.ai.context_client import AuraClient

client = AuraClient(
    assets_dir="/mnt/aura-assets",
    cache_enabled=True,
    redis_host="localhost",
    redis_port=6379
)
```

## Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Aura
COPY . .
RUN pip install -e .

# Create assets directory
RUN mkdir -p /assets

# Expose volume for assets
VOLUME /assets

# Run sensor monitoring
CMD ["python", "-m", "aura.sensors"]
```

Build and run:

```bash
# Build image
docker build -t aura:latest .

# Run container
docker run -d \
  -v /shared/assets:/assets \
  -e ASSET_ID=$(hostname) \
  -e ASSET_TYPE=container \
  aura:latest
```

## Kubernetes Deployment

Create `aura-daemonset.yaml`:

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: aura-agent
spec:
  selector:
    matchLabels:
      app: aura-agent
  template:
    metadata:
      labels:
        app: aura-agent
    spec:
      containers:
      - name: aura
        image: aura:latest
        env:
        - name: ASSET_ID
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        - name: ASSET_TYPE
          value: "k8s-node"
        volumeMounts:
        - name: assets
          mountPath: /assets
      volumes:
      - name: assets
        persistentVolumeClaim:
          claimName: aura-assets-pvc
```

Deploy:

```bash
kubectl apply -f aura-daemonset.yaml
```

## Monitoring with Systemd

Create `/etc/systemd/system/aura-sensor.service`:

```ini
[Unit]
Description=Aura Sensor Agent
After=network.target

[Service]
Type=simple
User=aura
WorkingDirectory=/opt/aura
Environment="ASSETS_DIR=/var/lib/aura/assets"
ExecStart=/usr/bin/python3 -m aura.sensors
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable aura-sensor
sudo systemctl start aura-sensor
sudo systemctl status aura-sensor
```

## Performance Tuning

### For High-Scale (1000+ assets)

1. **Enable Redis caching:**
   ```python
   client = AuraClient(cache_enabled=True, cache_ttl=60)
   ```

2. **Tune sensor intervals:**
   ```python
   sensor = ComputeSensor(
       asset_id="server-01",
       aav_file_path="/assets/server-01.aav",
       interval=10  # Slower updates for less critical assets
   )
   ```

3. **Run distributed Guardian:**
   Use 3-5 Guardian shards for 1000+ assets

4. **Batch queries:**
   ```python
   # Instead of querying one by one
   results = await client.batch_query(asset_ids)
   ```

## Security Considerations

1. **File Permissions:**
   ```bash
   chmod 640 /assets/*.aav
   chown aura:aura /assets/*.aav
   ```

2. **Network Security:**
   - Restrict Redis access (use authentication)
   - Use TLS for shared storage
   - Firewall Guardian ports

3. **Access Control:**
   ```python
   # Read-only client for AI agents
   client = AuraClient(assets_dir="/assets", read_only=True)
   ```

## Monitoring Aura Itself

Check Guardian health:

```bash
# View Guardian stats
python -c "
from aura.guardian.distributed import DistributedGuardian
guardian = DistributedGuardian(0, 3, './assets')
print(guardian.get_stats())
"
```

Monitor sensor health:

```bash
# Check sensor status in AAV files
aura validate --assets-dir ./assets
```

## Troubleshooting

### High CPU usage

```bash
# Check sensor intervals
# Increase interval for less critical assets
```

### Files not updating

```bash
# Check sensor status
aura validate --assets-dir ./assets

# Check Guardian logs
```

### Memory leaks

```bash
# Memory sensor includes leak detection
aura status <asset-id> --assets-dir ./assets
# Check "Memory > Leak Detection" field
```

## Next Steps

1. **Integrate with your AI agents:**
   See README.md for AI client examples

2. **Setup alerting:**
   Use the query API to find unhealthy assets

3. **Create dashboards:**
   Build visualizations using the Python API

4. **Scale horizontally:**
   Add more Guardian shards as you grow

## Support

- GitHub Issues: https://github.com/tajalagawani/Aura/issues
- Documentation: See README.md and aura.md
- Examples: Check the Python API examples in README.md
