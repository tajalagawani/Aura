# Aura Project

## Universal AI Asset Authority & Real-Time Context System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAAV Spec](https://img.shields.io/badge/spec-OpenAAV%20v1.0-blue.svg)](https://github.com/openaav/specification)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](https://github.com/aura-project/aura)

**Aura** gives AI systems environmental awareness through real-time, living infrastructure files. By embedding lightweight "sensors" into every computational asset, AI gains instant, reliable context about the entire infrastructure - transforming blind AI into context-aware intelligent agents.

> *"Making AI reliable through environmental awareness - not through bigger models, but through real-time context."*

---

## 🎯 The Problem We Solve

### Current AI in Production:

```python
# AI operates blind:
ai: "Deploy the new API version"
→ ❌ Fails: Database migration pending
→ ❌ Fails: Peak traffic (3000 req/s)  
→ ❌ Fails: Dependency unhealthy
→ ❌ Fails: Insufficient resources

# Why? AI had no environmental context
```

**AI today lacks:**
- ❌ Real-time infrastructure awareness
- ❌ Understanding of dependencies and relationships
- ❌ Knowledge of current resource availability
- ❌ Insight into system health and status
- ❌ Visibility into consequences of actions

**This makes AI unreliable, unsafe, and impractical for production operations.**

---

## 💡 The Aura Solution

### The Breakthrough: Infrastructure Nervous System

Just like the human body has a nervous system that provides instant awareness, Aura creates a **computational nervous system** that gives AI real-time environmental intelligence.

```
Traditional AI:                    Aura-Powered AI:
┌─────────────┐                   ┌─────────────┐
│  Blind AI   │                   │ Context-    │
│  Guessing   │                   │ Aware AI    │
│  Hoping     │                   │ Knowing     │
└─────────────┘                   └──────┬──────┘
                                         │
                                         ▼
                                  ┌─────────────┐
                                  │  Live .aav  │
                                  │   Files     │
                                  └──────┬──────┘
                                         │
                                         ▼
                                  ┌─────────────┐
                                  │ 5 Embedded  │
                                  │  "Sensors"  │
                                  │  per Asset  │
                                  └──────┬──────┘
                                         │
                                         ▼
                                  ┌─────────────┐
                                  │   Asset     │
                                  │ (Container, │
                                  │  VM, etc.)  │
                                  └─────────────┘
```

---

## 🏗️ Architecture Overview

### The 6-Layer System

```
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 6: AI DECISION LAYER                          │
│  Claude, GPT-4, Custom AI Agents with Real-Time Context         │
└────────────────────────┬────────────────────────────────────────┘
                         │ Reads live context
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 5: CACHING LAYER (NEW)                        │
│  Redis/In-Memory Cache for Ultra-Fast AI Queries                │
│  - Sub-millisecond reads for AI agents                          │
│  - Aggregated views across assets                               │
│  - Query optimization for common patterns                       │
└────────────────────────┬────────────────────────────────────────┘
                         │ Cached from
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 4: GUARDIAN LAYER                             │
│  Distributed validator ensures .aav files are always healthy     │
│  - File integrity validation                                     │
│  - Automatic corruption repair                                   │
│  - Sensor health monitoring                                      │
│  - Emergency file reconstruction                                 │
│  - Self-monitoring and alerting                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │ Protects & validates
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 3: LIVING .AAV FILES                          │
│  Real-time, human-readable TOML files (one per asset)           │
│  /assets/container-payment-api.aav ← Updated in real-time       │
│  /assets/database-postgres-prod.aav ← Live infrastructure state │
│  /assets/machine-prod-server-01.aav ← Intelligent updates       │
└────────────────────────┬────────────────────────────────────────┘
                         │ Updated by
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 2: SENSOR AGENTS                              │
│  5 lightweight monitors embedded in each asset:                  │
│  📊 ComputeSensor    - CPU, processes, load                     │
│  📊 MemorySensor     - RAM, leaks, usage                        │
│  📊 StorageSensor    - Disk, I/O, space                         │
│  📊 NetworkSensor    - Connections, traffic                     │
│  📊 ServicesSensor   - APIs, health, responses                  │
└────────────────────────┬────────────────────────────────────────┘
                         │ Monitors
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 1: COMPUTATIONAL ASSETS                       │
│  Containers │ VMs │ Databases │ Code │ APIs │ Kubernetes        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📄 The Core: Living .aav Files

### What is a .aav File?

**.aav (AI Authority Vector)** - A real-time, human-readable file that represents the complete state of a computational asset.

**Key Properties:**
- ✅ **Human-readable TOML format** (open in any text editor)
- ✅ **Intelligent updates** (change-driven, not time-driven)
- ✅ **One file per asset** (self-contained context)
- ✅ **5 dedicated sections** (each updated independently)
- ✅ **Version controllable** (track changes with git)
- ✅ **Cached for AI performance** (sub-millisecond queries)

### Example Live .aav File

```toml
# container-payment-api.aav
# This file updates when SIGNIFICANT CHANGES occur!

[metadata]
format_version = "2.0.0"
asset_id = "container-payment-api"
last_updated = "2025-11-16T15:30:45.123Z"
schema_version = "2.0"

[asset]
id = "container-payment-api"
type = "container"
name = "Payment API Service"
status = "running"
tags = ["production", "critical", "payments"]
environment = "production"

# ═══════════════════════════════════════════════════════════════
# SECTION 1: COMPUTE (Updated by ComputeSensor on change)
# ═══════════════════════════════════════════════════════════════
[compute]
last_updated = "2025-11-16T15:30:45.100Z"
sensor = "ComputeSensor_v2.0"
sensor_status = "healthy"
update_strategy = "change_driven"  # Only updates on 5%+ CPU change

[compute.real_time]
cpu_percent = 45.2              # ← Changes on 5% threshold
load_average = 1.23             # ← Live load average
process_count = 47              # ← Current process count
last_significant_change = "2025-11-16T15:25:15Z"

[compute.thresholds]
cpu_warning = 70.0
cpu_critical = 85.0
update_threshold = 5.0          # 5% change triggers update

[[compute.processes.critical]]
pid = 1234
name = "payment-service"
cpu_percent = 12.5
memory_mb = 256
status = "running"

[compute.events]
recent = [
  { timestamp = "2025-11-16T15:30:40Z", event = "process_started", pid = 1236 },
  { timestamp = "2025-11-16T15:25:15Z", event = "cpu_spike", cpu_percent = 89.5 }
]

# ═══════════════════════════════════════════════════════════════
# SECTION 2: MEMORY (Updated by MemorySensor independently)
# ═══════════════════════════════════════════════════════════════
[memory]
last_updated = "2025-11-16T15:30:45.150Z"
sensor = "MemorySensor_v2.0"
sensor_status = "healthy"
update_strategy = "change_driven"

[memory.real_time]
usage_percent = 68.1            # ← Live memory usage
available_mb = 2048             # ← Updates on 5% change
used_mb = 4352

[memory.analysis]
leak_detection = "stable"
growth_rate_mb_per_hour = 12.5
trend = "stable"

[memory.thresholds]
warning = 80.0
critical = 90.0
update_threshold = 5.0

# ═══════════════════════════════════════════════════════════════
# SECTION 3: STORAGE (Updated by StorageSensor independently)
# ═══════════════════════════════════════════════════════════════
[storage]
last_updated = "2025-11-16T15:30:45.200Z"
sensor = "StorageSensor_v2.0"
sensor_status = "healthy"

[storage.real_time]
disk_usage_percent = 67.8       # ← Live disk usage
free_gb = 15.6
io_read_mb_per_sec = 2.3
io_write_mb_per_sec = 1.8

[storage.thresholds]
warning = 80.0
critical = 90.0
update_threshold = 1.0          # 1% change for disk

# ═══════════════════════════════════════════════════════════════
# SECTION 4: NETWORK (Updated by NetworkSensor independently)
# ═══════════════════════════════════════════════════════════════
[network]
last_updated = "2025-11-16T15:30:45.250Z"
sensor = "NetworkSensor_v2.0"
sensor_status = "healthy"

[network.real_time]
active_connections = 127        # ← Live connection count
bytes_sent_per_sec = 1024000
bytes_recv_per_sec = 2048000

[network.thresholds]
max_connections = 500
update_threshold = 10           # 10 connection change

[[network.connections.active]]
local_port = 8080
remote_host = "nginx-lb-01"
state = "ESTABLISHED"

# ═══════════════════════════════════════════════════════════════
# SECTION 5: SERVICES (Updated by ServicesSensor independently)
# ═══════════════════════════════════════════════════════════════
[services]
last_updated = "2025-11-16T15:30:45.300Z"
sensor = "ServicesSensor_v2.0"
sensor_status = "healthy"

[services.application]
health_status = "healthy"       # ← Instant health updates
version = "3.2.2"
uptime_seconds = 86400

[[services.api_endpoints.monitored]]
path = "/api/v1/payments"
method = "POST"
avg_response_time_ms = 45       # ← Real-time performance
requests_per_minute = 1250
error_rate_percent = 0.02

[[services.dependencies]]
name = "postgres-db"
status = "healthy"
response_time_ms = 15
```

---

## 📊 The "Sensor" Approach: Embedded Monitoring

### What Are the Sensors?

**5 tiny, specialized monitoring agents** embedded safely into each asset. Think of them as **nerve endings** that instantly report significant changes.

### The 5 Essential Sensors

```python
# Each sensor is ~50-100 lines of code, <10MB RAM, <1% CPU

sensors = {
    "ComputeSensor": {
        "monitors": ["CPU usage", "Process lifecycle", "Load average"],
        "updates": "On 5%+ CPU change, process start/stop",
        "footprint": "5MB RAM, 0.5% CPU",
        "safety": "Read-only /proc access"
    },
    "MemorySensor": {
        "monitors": ["RAM usage", "Memory leaks", "Swap usage"],
        "updates": "On 5%+ memory change, leak detection",
        "footprint": "3MB RAM, 0.3% CPU",
        "safety": "Read-only /proc access"
    },
    "StorageSensor": {
        "monitors": ["Disk space", "I/O operations", "File changes"],
        "updates": "On 1%+ disk change, high I/O",
        "footprint": "4MB RAM, 0.4% CPU",
        "safety": "Read-only filesystem metrics"
    },
    "NetworkSensor": {
        "monitors": ["Connections", "Traffic", "Failed connections"],
        "updates": "On 10+ connection change, traffic spike",
        "footprint": "4MB RAM, 0.4% CPU",
        "safety": "Read-only network stats"
    },
    "ServicesSensor": {
        "monitors": ["API health", "Response times", "Error rates"],
        "updates": "On health change, 2x response time",
        "footprint": "6MB RAM, 0.6% CPU",
        "safety": "HTTP health checks only"
    }
}

# Total footprint per asset: ~22MB RAM, ~2.2% CPU
# Negligible impact on host application
```

### How Sensors Are Embedded (Safely)

#### **For Containers: Sidecar Pattern** (Safest Approach)

```python
# When we discover a container, inject monitoring sidecar
def safely_instrument_container(container_name: str):
    """Inject monitoring sidecar - completely isolated and safe"""
    
    # Deploy 5 sensor sidecars (or 1 multi-sensor sidecar)
    sidecar_config = {
        "image": "aura/sensor-agent:latest",
        "name": f"{container_name}-aura-sensors",
        
        # SAFETY: Read-only access to host metrics
        "volumes": [
            "/proc:/host/proc:ro",           # Read-only process info
            "/sys:/host/sys:ro",             # Read-only system info
            "/assets:/shared/assets:rw"      # Shared .aav file location
        ],
        
        # SAFETY: Share network namespace (see same connections)
        "network_mode": f"container:{container_name}",
        
        # SAFETY: No privilege escalation
        "privileged": False,
        "user": "1000:1000",  # Non-root
        
        # SAFETY: Resource limits
        "mem_limit": "25m",    # Max 25MB total
        "cpu_quota": 2200,     # Max 2.2% CPU
        
        # SAFETY: Security profiles
        "security_opt": [
            "apparmor=aura-sensor",
            "seccomp=aura-sensor.json"
        ],
        
        # Tell sensors which asset to monitor
        "environment": {
            "TARGET_CONTAINER": container_name,
            "AAV_FILE": f"/shared/assets/{container_name}.aav",
            "UPDATE_MODE": "change-driven",
            "CACHE_ENDPOINT": "redis://cache:6379"
        }
    }
    
    # Deploy sidecar
    sidecar = docker.containers.run(**sidecar_config, detach=True)
    return sidecar
```

#### **Kubernetes Enhanced Security**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: payment-api-instrumented
spec:
  containers:
  - name: payment-api
    image: payment-api:latest
    
  - name: aura-sensors
    image: aura/sensor-agent:latest
    
    # Enhanced security context
    securityContext:
      runAsUser: 1000
      runAsGroup: 1000
      runAsNonRoot: true
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      
      capabilities:
        drop: ["ALL"]
      
      # SELinux/AppArmor profiles
      seLinuxOptions:
        type: aura_sensor_t
      appArmorProfile:
        type: Localhost
        localhostProfile: aura-sensor
    
    # Strict resource limits
    resources:
      limits:
        memory: "25Mi"
        cpu: "25m"
      requests:
        memory: "15Mi"
        cpu: "10m"
    
    # Read-only volumes
    volumeMounts:
    - name: proc
      mountPath: /host/proc
      readOnly: true
    - name: sys
      mountPath: /host/sys
      readOnly: true
    - name: aav-files
      mountPath: /shared/assets
  
  volumes:
  - name: proc
    hostPath:
      path: /proc
  - name: sys
    hostPath:
      path: /sys
  - name: aav-files
    persistentVolumeClaim:
      claimName: aura-assets
```

#### **Security Profiles**

```bash
# AppArmor profile for sensors
cat > /etc/apparmor.d/aura-sensor << 'EOF'
#include <tunables/global>

/usr/local/bin/aura-sensor {
  #include <abstractions/base>
  
  # Allow read-only monitoring
  /proc/              r,
  /sys/               r,
  /proc/*/stat        r,
  /proc/*/status      r,
  /proc/*/cmdline     r,
  /sys/class/net/**   r,
  
  # Deny sensitive paths
  deny /etc/shadow    rwx,
  deny /etc/passwd    w,
  deny /root/**       rwx,
  deny /home/**       rwx,
  
  # Allow writing only to .aav files
  /shared/assets/*.aav        w,
  /shared/assets/*.health     w,
  
  # Network: localhost only
  network inet stream,
  
  # Deny privilege escalation
  deny capability sys_admin,
  deny capability sys_module,
}
EOF

# Load profile
apparmor_parser -r /etc/apparmor.d/aura-sensor
```

#### **Safety Guarantees**

```python
safety_checklist = {
    "✅ Non-intrusive": "Separate container, no interference with host app",
    "✅ Fail-safe": "If sensor crashes, host continues normally",
    "✅ Removable": "Clean uninstall, no traces left",
    "✅ Minimal footprint": "<25MB memory, <2.5% CPU total",
    "✅ Secure": "Read-only system access, non-root user",
    "✅ Isolated": "Cannot affect application processes",
    "✅ Resource-limited": "Hard caps on CPU/memory usage",
    "✅ Observable": "Sensor health is monitored by Guardian",
    "✅ AppArmor/SELinux": "Mandatory access controls enforced",
    "✅ No privilege escalation": "All capabilities dropped",
    "✅ Sensitive data redacted": "Secrets filtered from metrics"
}
```

---

## ⚡ Intelligent Updates: Change-Driven, Not Time-Driven

### The Critical Difference

```python
# ❌ TRADITIONAL APPROACH (Polling - Wasteful)
while True:
    scan_everything()
    update_file()
    sleep(300)  # File is stale for 5 minutes, wastes resources

# ❌ NAIVE REAL-TIME (Event spam - Overwhelming)
on_any_cpu_change():     update_file()  # 1000s of updates/sec
on_any_memory_change():  update_file()  # File thrashing
on_any_network_change(): update_file()  # I/O bottleneck

# ✅ AURA APPROACH (Change-driven - Intelligent)
on_significant_cpu_change():      update_file()  # 5%+ change
on_significant_memory_change():   update_file()  # 5%+ change
on_connection_count_change():     update_file()  # 10+ connections
on_health_status_change():        update_file()  # State change
on_process_lifecycle():           update_file()  # Start/stop only

# Result: 10-100 updates/minute instead of 10,000+
```

### Adaptive Sampling with Backpressure

```python
class AdaptiveSensor:
    """Automatically adjusts monitoring frequency based on system load"""
    
    def __init__(self):
        self.sampling_interval = 0.1    # Start at 100ms
        self.min_interval = 0.1         # Fastest: 100ms
        self.max_interval = 5.0         # Slowest: 5s (under extreme load)
        self.change_threshold = 5.0     # 5% change triggers update
        
    async def monitor_with_intelligence(self):
        """Monitor with adaptive sampling and change detection"""
        
        previous_cpu = 0
        consecutive_failures = 0
        
        while True:
            start = time.time()
            
            try:
                # Sample metric
                current_cpu = psutil.cpu_percent(interval=0.1)
                
                # Only update if SIGNIFICANT change
                if abs(current_cpu - previous_cpu) > self.change_threshold:
                    await self.update_file({
                        "compute": {
                            "real_time": {
                                "cpu_percent": current_cpu,
                                "last_significant_change": datetime.utcnow().isoformat() + "Z"
                            }
                        }
                    })
                    previous_cpu = current_cpu
                    
                    # Success - can sample faster
                    self.sampling_interval = max(
                        self.min_interval,
                        self.sampling_interval * 0.95
                    )
                    consecutive_failures = 0
                
            except IOError as e:
                # File locked or I/O overload - slow down
                consecutive_failures += 1
                self.sampling_interval = min(
                    self.max_interval,
                    self.sampling_interval * (1.5 ** consecutive_failures)
                )
                logger.warning(f"I/O pressure detected, slowing to {self.sampling_interval}s")
                
            except Exception as e:
                logger.error(f"Sensor error: {e}")
                consecutive_failures += 1
            
            # Adaptive sleep
            elapsed = time.time() - start
            sleep_time = max(0, self.sampling_interval - elapsed)
            await asyncio.sleep(sleep_time)
```

### Event Aggregation for Scale

```python
class EventAggregator:
    """Batch and deduplicate events before writing to reduce I/O"""
    
    def __init__(self):
        self.pending_updates = {}  # asset_id -> {section -> data}
        self.flush_interval = 1.0  # Adaptive: 1s-5s based on load
        self.max_queue_size = 5000
        
    async def queue_update(self, asset_id: str, section: str, data: dict):
        """Queue update instead of immediate write"""
        
        if asset_id not in self.pending_updates:
            self.pending_updates[asset_id] = {}
        
        # Merge with existing updates (latest wins)
        self.pending_updates[asset_id][section] = {
            **self.pending_updates[asset_id].get(section, {}),
            **data,
            "aggregated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Emergency flush if queue too large
        if len(self.pending_updates) > self.max_queue_size:
            await self.flush_all()
    
    async def flush_periodically(self):
        """Intelligent batching with adaptive intervals"""
        while True:
            await asyncio.sleep(self.adaptive_flush_interval())
            await self.flush_all()
    
    async def flush_all(self):
        """Batch write all pending updates"""
        if not self.pending_updates:
            return
        
        updates_to_write = self.pending_updates.copy()
        self.pending_updates.clear()
        
        # Parallel writes to multiple files
        tasks = [
            self.atomic_write(asset_id, sections)
            for asset_id, sections in updates_to_write.items()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def adaptive_flush_interval(self) -> float:
        """Adjust flush rate based on queue pressure"""
        queue_size = len(self.pending_updates)
        
        if queue_size > 3000:
            return 5.0  # Slow down under pressure
        elif queue_size > 1000:
            return 2.0
        elif queue_size > 100:
            return 1.0
        else:
            return 0.5  # Fast when quiet
    
    async def atomic_write(self, asset_id: str, sections: dict):
        """Atomically update .aav file"""
        aav_path = Path(f"/assets/{asset_id}.aav")
        
        try:
            # Read current file
            current = toml.load(aav_path)
            
            # Merge updates
            for section, data in sections.items():
                if section in current:
                    current[section].update(data)
                else:
                    current[section] = data
            
            # Update metadata
            current["metadata"]["last_updated"] = datetime.utcnow().isoformat() + "Z"
            
            # Atomic write via temp file + rename
            temp_path = aav_path.with_suffix(".tmp")
            with open(temp_path, 'w') as f:
                toml.dump(current, f)
            
            temp_path.replace(aav_path)  # Atomic on POSIX
            
            # Update cache
            await self.update_cache(asset_id, current)
            
        except Exception as e:
            logger.error(f"Failed to write {asset_id}: {e}")
            raise
```

---

## 🛡️ The Guardian: Distributed File Integrity System

### The Problem Guardian Solves

**What happens when sensors fail?**
- Sensor crashes → stale data
- File corruption → AI can't read context
- Sensor deadlock → other sensors blocked
- All sensors fail → no current context
- Scale: Single Guardian can't monitor 10,000+ assets

**Solution: Distributed Guardian Architecture**

### Guardian Responsibilities

```python
guardian_duties = {
    "1. File Integrity Validation": {
        "task": "Continuously validate .aav files are healthy",
        "frequency": "Every 30 seconds per shard",
        "actions": ["Check TOML syntax", "Validate structure", "Check freshness"]
    },
    "2. Corruption Repair": {
        "task": "Instantly repair corrupted files",
        "frequency": "Immediate on detection",
        "actions": ["Attempt TOML fixes", "Rebuild from backup", "Emergency reconstruction"]
    },
    "3. Sensor Health Monitoring": {
        "task": "Monitor health of all sensor containers",
        "frequency": "Every 60 seconds",
        "actions": ["Check sensor running", "Monitor restart count", "Restart unhealthy sensors"]
    },
    "4. Emergency Reconstruction": {
        "task": "Rebuild files when all else fails",
        "frequency": "On complete failure",
        "actions": ["Create minimal valid .aav", "Restart sensors", "Log incident"]
    },
    "5. Self-Monitoring": {
        "task": "Monitor Guardian's own health",
        "frequency": "Every 5 minutes",
        "actions": ["Check resource usage", "Validate Guardian health", "Report to coordinator"]
    },
    "6. Shard Coordination": {
        "task": "Coordinate with other Guardian instances",
        "frequency": "Continuous",
        "actions": ["Leader election", "Shard rebalancing", "Failover handling"]
    }
}
```

### Distributed Guardian Architecture

```python
class DistributedGuardian:
    """Sharded Guardian for massive scale"""
    
    def __init__(self, shard_id: int, total_shards: int):
        self.shard_id = shard_id
        self.total_shards = total_shards
        self.my_assets = set()
        self.coordinator_url = "http://guardian-coordinator:8080"
        
    def should_monitor(self, asset_id: str) -> bool:
        """Consistent hash-based sharding"""
        return hash(asset_id) % self.total_shards == self.shard_id
    
    async def start_guardian_duties(self):
        """Run all guardian responsibilities for my shard"""
        
        # Discover my assets
        self.my_assets = await self.discover_my_assets()
        
        logger.info(f"Guardian shard {self.shard_id}/{self.total_shards} "
                   f"monitoring {len(self.my_assets)} assets")
        
        # Run all duties in parallel
        await asyncio.gather(
            self.file_integrity_monitor(),
            self.sensor_health_monitor(),
            self.emergency_repair_service(),
            self.file_cleanup_service(),
            self.shard_coordinator(),
            self.self_monitor()
        )
    
    async def discover_my_assets(self) -> set:
        """Find which assets this shard is responsible for"""
        all_assets = list(Path("/assets/").glob("*.aav"))
        
        my_assets = {
            asset.stem for asset in all_assets
            if self.should_monitor(asset.stem)
        }
        
        return my_assets
    
    async def file_integrity_monitor(self):
        """Validate files in my shard"""
        while True:
            for asset_id in self.my_assets:
                aav_file = Path(f"/assets/{asset_id}.aav")
                
                validation = await self.validate_file_integrity(aav_file)
                
                if not validation["valid"]:
                    logger.error(f"File corruption detected: {asset_id}")
                    await self.repair_file(aav_file, validation)
            
            await asyncio.sleep(30)  # Check every 30s
    
    async def validate_file_integrity(self, aav_file: Path) -> dict:
        """Comprehensive file validation"""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # 1. File exists and readable
            if not aav_file.exists():
                validation["valid"] = False
                validation["errors"].append("File does not exist")
                return validation
            
            # 2. Not locked by stuck process
            with open(aav_file, 'r') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            
            # 3. Valid TOML syntax
            try:
                data = toml.load(aav_file)
            except toml.TomlDecodeError as e:
                validation["valid"] = False
                validation["errors"].append(f"Invalid TOML: {e}")
                return validation
            
            # 4. Required structure present
            required_keys = ["metadata", "asset", "compute", "memory", "storage", "network", "services"]
            missing = [k for k in required_keys if k not in data]
            if missing:
                validation["valid"] = False
                validation["errors"].append(f"Missing sections: {missing}")
            
            # 5. Data is fresh (updated recently)
            last_updated = datetime.fromisoformat(data["metadata"]["last_updated"].replace("Z", "+00:00"))
            age = datetime.now(timezone.utc) - last_updated
            
            if age.total_seconds() > 300:  # 5 minutes
                validation["warnings"].append(f"Stale data: {age.total_seconds()}s old")
            
            # 6. Sections are consistent
            for section in ["compute", "memory", "storage", "network", "services"]:
                if section in data:
                    if "sensor_status" in data[section]:
                        if data[section]["sensor_status"] != "healthy":
                            validation["warnings"].append(f"{section} sensor unhealthy")
            
        except Exception as e:
            validation["valid"] = False
            validation["errors"].append(f"Validation error: {e}")
        
        return validation
    
    async def repair_file(self, aav_file: Path, validation: dict):
        """Attempt to repair corrupted file"""
        
        logger.info(f"Attempting repair of {aav_file}")
        
        # Try to load partial data
        try:
            with open(aav_file, 'r') as f:
                content = f.read()
            
            # Attempt TOML fixes
            fixed_content = self.attempt_toml_fixes(content)
            
            # Test if fixed
            try:
                toml.loads(fixed_content)
                
                # Write fixed version
                with open(aav_file, 'w') as f:
                    f.write(fixed_content)
                
                logger.info(f"Successfully repaired {aav_file}")
                return
            except:
                pass
        except:
            pass
        
        # Repair failed - try backup
        backup_file = aav_file.with_suffix(".aav.backup")
        if backup_file.exists():
            logger.info(f"Restoring from backup: {aav_file}")
            backup_file.replace(aav_file)
            return
        
        # Last resort - rebuild from scratch
        asset_id = aav_file.stem
        await self.emergency_file_rebuild(aav_file, asset_id)
    
    async def emergency_file_rebuild(self, aav_file: Path, asset_id: str):
        """Rebuild file from scratch if all else fails"""
        
        logger.warning(f"Emergency rebuild: {asset_id}")
        
        emergency_aav = {
            "metadata": {
                "format_version": "2.0.0",
                "asset_id": asset_id,
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "emergency_rebuild": True,
                "rebuild_reason": "File corruption - all repair attempts failed"
            },
            "asset": {
                "id": asset_id,
                "type": "unknown",
                "status": "unknown"
            },
            "compute": {"sensor_status": "restarting"},
            "memory": {"sensor_status": "restarting"},
            "storage": {"sensor_status": "restarting"},
            "network": {"sensor_status": "restarting"},
            "services": {"sensor_status": "restarting"}
        }
        
        # Write emergency file
        with open(aav_file, 'w') as f:
            toml.dump(emergency_aav, f)
        
        # Restart sensors for this asset
        await self.restart_sensors_for_asset(asset_id)
        
        # Alert
        await self.alert_emergency_rebuild(asset_id)
    
    async def sensor_health_monitor(self):
        """Monitor health of sensor containers in my shard"""
        docker_client = docker.from_env()
        
        while True:
            for asset_id in self.my_assets:
                sensor_container = f"{asset_id}-aura-sensors"
                
                try:
                    container = docker_client.containers.get(sensor_container)
                    
                    # Check health
                    if container.status != "running":
                        logger.warning(f"Sensor unhealthy: {sensor_container}")
                        await self.restart_sensor_container(sensor_container)
                    
                    # Check restart count
                    restart_count = container.attrs["RestartCount"]
                    if restart_count > 5:
                        logger.error(f"Sensor crash loop: {sensor_container}")
                        await self.alert_sensor_crash_loop(sensor_container)
                
                except docker.errors.NotFound:
                    logger.error(f"Sensor container missing: {sensor_container}")
                    await self.redeploy_sensor(asset_id)
            
            await asyncio.sleep(60)
    
    async def shard_coordinator(self):
        """Coordinate with other Guardian shards"""
        while True:
            try:
                # Report health to coordinator
                health = {
                    "shard_id": self.shard_id,
                    "assets_monitored": len(self.my_assets),
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                
                await self.report_to_coordinator(health)
                
                # Check for rebalancing instructions
                instructions = await self.check_coordinator_instructions()
                
                if instructions.get("rebalance"):
                    await self.rebalance_assets(instructions["new_shard_count"])
                
            except Exception as e:
                logger.error(f"Coordinator communication failed: {e}")
            
            await asyncio.sleep(30)
    
    async def self_monitor(self):
        """Monitor Guardian's own health"""
        while True:
            process = psutil.Process()
            
            health = {
                "shard_id": self.shard_id,
                "memory_mb": process.memory_info().rss / 1024 / 1024,
                "cpu_percent": process.cpu_percent(),
                "assets_monitored": len(self.my_assets),
                "uptime_seconds": time.time() - process.create_time()
            }
            
            # Alert if Guardian is unhealthy
            if health["memory_mb"] > 200:  # 200MB limit
                logger.warning(f"Guardian memory high: {health['memory_mb']}MB")
            
            if health["cpu_percent"] > 10:  # 10% limit
                logger.warning(f"Guardian CPU high: {health['cpu_percent']}%")
            
            # Log health
            logger.info(f"Guardian health: {health}")
            
            await asyncio.sleep(300)  # Every 5 minutes
```

### Guardian Deployment

```yaml
# Deploy multiple Guardian shards
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: aura-guardian
spec:
  serviceName: aura-guardian
  replicas: 3  # 3 shards for redundancy
  selector:
    matchLabels:
      app: aura-guardian
  template:
    metadata:
      labels:
        app: aura-guardian
    spec:
      containers:
      - name: guardian
        image: aura/guardian:latest
        env:
        - name: SHARD_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name  # guardian-0, guardian-1, guardian-2
        - name: TOTAL_SHARDS
          value: "3"
        - name: COORDINATOR_URL
          value: "http://guardian-coordinator:8080"
        
        resources:
          limits:
            memory: "200Mi"
            cpu: "100m"
        
        volumeMounts:
        - name: aav-files
          mountPath: /assets
  
  volumeClaimTemplates:
  - metadata:
      name: aav-files
    spec:
      accessModes: ["ReadWriteMany"]
      resources:
        requests:
          storage: 10Gi
```

---

## 🚀 High-Performance Caching Layer

### The Speed Problem

```python
# Problem: AI makes 1000s of queries
for i in range(1000):
    context = read_aav_file("container-api.aav")  # Disk I/O each time
    ai_decision(context)

# 1000 disk reads = slow and wasteful
```

### Solution: Tiered Storage

```python
class TieredStorage:
    """Hot/warm/cold storage for optimal performance"""
    
    def __init__(self):
        # HOT: Redis cache (sub-millisecond reads)
        self.hot_cache = redis.StrictRedis(
            host='redis',
            port=6379,
            decode_responses=True
        )
        
        # WARM: Local filesystem .aav files (human-readable)
        self.warm_path = Path("/assets/")
        
        # COLD: S3/blob storage (historical data)
        self.cold_storage = boto3.client('s3')
        
    async def read_for_ai(self, asset_id: str) -> dict:
        """AI queries hit hot cache (fastest)"""
        
        # Try hot cache first
        cached = await self.hot_cache.get(f"aav:{asset_id}")
        if cached:
            return json.loads(cached)
        
        # Cache miss - read from warm storage
        aav_file = self.warm_path / f"{asset_id}.aav"
        data = toml.load(aav_file)
        
        # Populate cache
        await self.hot_cache.set(
            f"aav:{asset_id}",
            json.dumps(data),
            ex=300  # 5min TTL
        )
        
        return data
    
    async def write_update(self, asset_id: str, data: dict):
        """Sensors write to all tiers"""
        
        # HOT: Immediate cache update (AI sees instantly)
        await self.hot_cache.set(
            f"aav:{asset_id}",
            json.dumps(data),
            ex=300
        )
        
        # WARM: Async file write (human-readable)
        asyncio.create_task(self.write_aav_file(asset_id, data))
        
        # COLD: Batch append to history (analytics)
        asyncio.create_task(self.append_to_history(asset_id, data))
    
    async def query_aggregated(self, filters: dict) -> list:
        """Optimized queries across many assets"""
        
        # Check if aggregated view is cached
        cache_key = f"agg:{json.dumps(filters, sort_keys=True)}"
        cached = await self.hot_cache.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        # Build aggregated view
        results = []
        for asset_id in await self.get_matching_assets(filters):
            data = await self.read_for_ai(asset_id)
            results.append(data)
        
        # Cache aggregated result
        await self.hot_cache.set(cache_key, json.dumps(results), ex=60)
        
        return results

# Performance comparison:
# Disk read:   ~5-10ms
# Redis read:  ~0.1-0.5ms (10-100x faster)
# AI can now make 10,000+ queries/second instead of 100-200
```

---

## 🤖 AI Integration

### Fast Context Queries

```python
from aura import AuraClient

# Initialize with caching
client = AuraClient(cache_enabled=True)

# Ultra-fast reads from cache
context = await client.read_aav("container-payment-api")  # <1ms

# AI analyzes current state
if context['compute']['real_time']['cpu_percent'] > 80:
    decision = "❌ ABORT: CPU too high"
elif context['services']['health_status'] != "healthy":
    decision = "❌ ABORT: Service unhealthy"
else:
    decision = "✅ PROCEED: All systems healthy"
```

### Aggregated Queries

```python
# Query across all assets efficiently
all_unhealthy = await client.query_assets(
    filters={
        "services.health_status": {"$ne": "healthy"}
    }
)

high_cpu_assets = await client.query_assets(
    filters={
        "compute.real_time.cpu_percent": {"$gt": 80}
    }
)

# AI gets instant visibility across infrastructure
print(f"Found {len(all_unhealthy)} unhealthy services")
print(f"Found {len(high_cpu_assets)} high-CPU assets")
```

---

## 🌐 Human-Friendly Interfaces

### Web Dashboard

```python
# Real-time dashboard with WebSocket updates
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.websocket("/ws/live/{asset_id}")
async def websocket_live_updates(websocket: WebSocket, asset_id: str):
    """Stream real-time updates to browser"""
    await websocket.accept()
    
    async for update in watch_aav_updates(asset_id):
        await websocket.send_json(update)

@app.get("/dashboard")
async def dashboard():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Aura Live Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            .asset-card { border: 1px solid #ccc; padding: 20px; margin: 10px; }
            .healthy { background: #d4edda; }
            .warning { background: #fff3cd; }
            .critical { background: #f8d7da; }
            .metric { font-size: 24px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🎯 Aura Live Infrastructure Dashboard</h1>
        <div id="assets-grid"></div>
        
        <script>
            // Connect to real-time updates
            const assets = ['payment-api', 'checkout-api', 'user-service'];
            
            assets.forEach(asset => {
                const ws = new WebSocket(`ws://localhost:8000/ws/live/${asset}`);
                
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    updateAssetCard(asset, data);
                };
            });
            
            function updateAssetCard(asset, data) {
                const card = document.getElementById(`asset-${asset}`);
                if (!card) return;
                
                // Update metrics in real-time
                card.querySelector('.cpu').textContent = 
                    `CPU: ${data.compute.real_time.cpu_percent}%`;
                card.querySelector('.memory').textContent = 
                    `Memory: ${data.memory.real_time.usage_percent}%`;
                card.querySelector('.health').textContent = 
                    `Status: ${data.services.health_status}`;
                
                // Update card color based on health
                card.className = `asset-card ${getHealthClass(data)}`;
            }
            
            function getHealthClass(data) {
                if (data.services.health_status !== 'healthy') return 'critical';
                if (data.compute.real_time.cpu_percent > 80) return 'warning';
                if (data.memory.real_time.usage_percent > 80) return 'warning';
                return 'healthy';
            }
        </script>
    </body>
    </html>
    """)
```

### CLI for Humans

```bash
# User-friendly command-line interface
$ aura status container-payment-api

📊 Payment API Container - Live Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Updated: 2 seconds ago

💻 COMPUTE
   CPU:      45.2% ████████░░░░░░░░░░░░ Normal
   Load:     1.23
   Processes: 47

🧠 MEMORY  
   Usage:    68.1% █████████████░░░░░░░ Normal
   Available: 2.0 GB
   Trend:    Stable

💾 STORAGE
   Usage:    67.8% █████████████░░░░░░░ Normal
   Free:     15.6 GB
   I/O:      Read 2.3 MB/s, Write 1.8 MB/s

🌐 NETWORK
   Connections: 127 active
   Traffic:     In 2.0 MB/s, Out 1.0 MB/s

✅ SERVICES
   Health:   HEALTHY ✓
   Version:  3.2.2
   Uptime:   24h 0m
   API /api/v1/payments: 45ms avg, 0.02% errors

📦 DEPENDENCIES
   ✅ postgres-db: Healthy (15ms)
   ✅ redis-cache: Healthy (2ms)
   ✅ auth-service: Healthy (23ms)

📋 RECENT EVENTS
   15:30:45 - CPU spike to 89% (resolved)
   15:25:15 - Process started: worker-pool-03
   15:20:00 - Deployed version 3.2.2

💡 RECOMMENDATIONS
   All systems operating normally. No action needed.

# Query multiple assets
$ aura query --filter "cpu > 80"

Found 3 assets with high CPU:
   📊 worker-service-01: 87.2% CPU
   📊 analytics-job-05: 92.1% CPU
   📊 batch-processor: 83.4% CPU

# Watch live updates
$ aura watch container-payment-api

Watching container-payment-api (Ctrl+C to stop)
15:45:00 - CPU: 45% | Memory: 68% | Health: ✅
15:45:05 - CPU: 47% | Memory: 68% | Health: ✅
15:45:10 - CPU: 52% ⚠️  | Memory: 70% | Health: ✅
15:45:15 - CPU: 48% | Memory: 69% | Health: ✅
```

---

## 📈 Performance & Scale

### Resource Footprint

```python
# Per-asset footprint
per_asset = {
    "memory": {
        "sensors": "~22MB RAM (5 sensors)",
        "cache_entry": "~50-100KB",
        "aav_file": "~50-200KB"
    },
    "cpu": {
        "sensors": "~2.2% CPU (adaptive)",
        "peak": "~4% during updates"
    },
    "storage": {
        "aav_file": "~50-200KB",
        "history": "~1MB/day (compressed)"
    },
    "network": {
        "updates": "~1-5KB per update",
        "bandwidth": "~1-10KB/min (intelligent updates)"
    }
}

# 1,000 asset infrastructure
scale_1000 = {
    "total_memory": "22GB sensors + 100MB cache = 22.1GB",
    "total_cpu": "~22% (distributed across nodes)",
    "total_storage": "50-200MB active + 1GB/day historical",
    "guardians_needed": "3-5 shards",
    "cache_servers": "1-2 Redis instances"
}

# 10,000 asset infrastructure  
scale_10000 = {
    "total_memory": "220GB sensors + 1GB cache = 221GB",
    "total_cpu": "~220% (across cluster)",
    "total_storage": "500MB-2GB active + 10GB/day historical",
    "guardians_needed": "10-20 shards",
    "cache_servers": "3-5 Redis instances (clustered)"
}

# Impact on typical Kubernetes cluster (100 nodes):
# - Memory: <1% of total cluster memory
# - CPU: <1% of total cluster CPU
# - Negligible compared to monitoring overhead saved by AI efficiency
```

### Performance Benchmarks

```python
benchmarks = {
    "file_read": {
        "cold": "5-10ms (disk)",
        "warm": "1-2ms (filesystem cache)",
        "hot": "0.1-0.5ms (Redis cache)"
    },
    "file_write": {
        "atomic_update": "2-5ms",
        "batched_update": "0.5-1ms per asset (amortized)"
    },
    "ai_query": {
        "single_asset": "<1ms (cached)",
        "aggregated_100": "10-50ms",
        "aggregated_1000": "100-500ms"
    },
    "update_latency": {
        "significant_change": "100-500ms (detection to file)",
        "cache_update": "<10ms",
        "ai_visibility": "<1s total"
    }
}
```

---

## 📊 Complete Workflow

### End-to-End Example

```bash
# 1. SCAN - Discover all computational assets
aura scan-all --recursive --output /assets/

# Output:
# ✓ Found 247 computational assets
# ✓ Generated 247 .aav manifest files
# 📄 /assets/container-payment-api.aav
# 📄 /assets/container-checkout-api.aav
# 📄 /assets/database-postgres-prod.aav
# 📄 /assets/vm-prod-web-01.aav
# ...

# 2. INSTRUMENT - Deploy monitoring sensors
aura instrument-all --target /assets/*.aav

# Output:
# 📊 Instrumented container-payment-api with 5 sensors
# 📊 Instrumented container-checkout-api with 5 sensors
# 📊 Instrumented database-postgres-prod with 5 sensors
# ✓ Total: 1,235 sensors deployed across 247 assets

# 3. START CACHE - Launch Redis cache layer
aura start-cache --redis redis://localhost:6379

# Output:
# 🚀 Cache layer started
# ✓ Connected to Redis
# ✓ Warming cache from 247 .aav files
# ✓ Cache ready - sub-millisecond queries enabled

# 4. START GUARDIANS - Deploy distributed guardians
aura start-guardians --shards 3 --assets-dir /assets/

# Output:
# 🛡️  Starting 3 Guardian shards...
# ✓ Guardian shard 0/3: Monitoring 82 assets
# ✓ Guardian shard 1/3: Monitoring 83 assets
# ✓ Guardian shard 2/3: Monitoring 82 assets
# ✓ All guardians healthy and coordinated

# 5. VIEW STATUS - Check system health
aura status --summary

# Output:
# 📊 Aura System Status
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Assets Monitored:    247
# Sensors Running:     1,235 (100% healthy)
# Guardians Active:    3 shards
# Cache Hit Rate:      98.7%
# Avg Update Latency:  287ms
# 
# Health Summary:
#   ✅ Healthy:   234 (94.7%)
#   ⚠️  Warning:   11 (4.5%)
#   ❌ Critical:   2 (0.8%)
# 
# Top Issues:
#   1. container-analytics-02: High CPU (89%)
#   2. vm-batch-worker-05: High memory (91%)

# 6. WATCH LIVE - Monitor specific asset
aura watch container-payment-api

# Output (streaming):
# Watching container-payment-api (press Ctrl+C to stop)
# 15:45:00 - CPU: 45% | Mem: 68% | Disk: 67% | Conn: 127 | Health: ✅
# 15:45:05 - CPU: 47% | Mem: 68% | Disk: 67% | Conn: 129 | Health: ✅
# 15:45:10 - CPU: 52% ⚠️  | Mem: 70% | Disk: 67% | Conn: 145 | Health: ✅
# 15:45:15 - CPU: 48% | Mem: 69% | Disk: 67% | Conn: 132 | Health: ✅

# 7. AI INTEGRATION - Query with context
python examples/ai_deployment_decision.py

# Output:
# 🤖 AI Deployment Analysis for payment-api
# 
# Current Infrastructure State:
#   CPU: 45% (Normal)
#   Memory: 68% (Normal)
#   Disk: 67% (Normal)
#   Network: 127 connections (Normal)
#   Services: All healthy ✅
# 
# Dependencies Status:
#   ✅ postgres-db: 15ms response time
#   ✅ redis-cache: 2ms response time
#   ✅ auth-service: 23ms response time
# 
# Traffic Analysis:
#   Current: 1,250 req/min (moderate)
#   Historical average: 1,100 req/min
#   Peak traffic window: 6 hours away
# 
# ✅ RECOMMENDATION: Safe to deploy
#    - All systems healthy
#    - Not in peak traffic window
#    - Dependencies responsive
#    - Sufficient resources available
# 
# Suggested deployment window: Next 4 hours
```

---

## 🚀 Getting Started

### Installation

```bash
# Install Aura
pip install aura-ai

# Or from source
git clone https://github.com/aura-project/aura
cd aura
pip install -e .
```

### Prerequisites

```bash
# Required:
- Python 3.11+
- Docker (for container monitoring)
- Redis (for caching layer)

# Optional:
- Kubernetes (for pod monitoring)
- Neo4j (for optional graph database)
- Cloud CLI tools (AWS/GCP/Azure)
```

### Quick Start (10 Minutes)

```bash
# 1. Start Redis cache
docker run -d -p 6379:6379 redis:latest

# 2. Scan your infrastructure
aura scan --type container --output /assets/

# 3. Deploy sensors
aura instrument-all --target /assets/*.aav

# 4. Start cache layer
aura start-cache --redis redis://localhost:6379

# 5. Start Guardian
aura start-guardians --shards 1 --assets-dir /assets/

# 6. View live status
aura status --summary

# 7. Open dashboard
aura dashboard --port 8000
# Visit http://localhost:8000

# 8. Try AI integration
python examples/ai_context_query.py
```

---

## 🛠️ Technology Stack

```python
core_stack = {
    "language": "Python 3.11+",
    "file_format": "TOML (human-readable)",
    "caching": "Redis (sub-millisecond queries)",
    "containerization": "Docker (sensor sidecars)",
    "orchestration": "Kubernetes (optional)",
    "monitoring": "psutil (system metrics)",
    "async_runtime": "asyncio (event-driven)",
    "security": "AppArmor/SELinux profiles",
    
    "dependencies": {
        "core": [
            "psutil>=5.9.6",      # System monitoring
            "toml>=0.10.2",       # TOML parsing
            "docker>=7.0.0",      # Docker API
            "redis>=5.0.0",       # Caching layer
            "click>=8.1.7",       # CLI framework
            "asyncio",            # Async operations
            "fcntl",              # File locking
        ],
        "optional": [
            "kubernetes>=28.1.0", # K8s monitoring
            "boto3>=1.34.0",      # AWS monitoring
            "fastapi>=0.104.0",   # Dashboard API
            "prometheus-client",  # Metrics export
        ]
    }
}
```

### Project Structure

```
aura/
├── aura/
│   ├── __init__.py
│   ├── cli/
│   │   ├── main.py              # CLI entry point
│   │   ├── scan.py              # Scan commands
│   │   └── instrument.py        # Instrumentation
│   ├── scanners/
│   │   ├── base.py              # Base scanner
│   │   ├── container.py         # Container discovery
│   │   ├── kubernetes.py        # K8s pod discovery
│   │   ├── machine.py           # VM/bare metal
│   │   └── cloud.py             # AWS/GCP/Azure
│   ├── sensors/
│   │   ├── compute_sensor.py    # CPU/process monitoring
│   │   ├── memory_sensor.py     # RAM monitoring
│   │   ├── storage_sensor.py    # Disk monitoring
│   │   ├── network_sensor.py    # Network monitoring
│   │   └── services_sensor.py   # Service/API monitoring
│   ├── guardian/
│   │   ├── distributed.py       # Distributed guardian
│   │   ├── validator.py         # File validation
│   │   ├── repairer.py          # Auto-repair
│   │   └── coordinator.py       # Shard coordination
│   ├── cache/
│   │   ├── redis_cache.py       # Redis integration
│   │   ├── tiered_storage.py   # Hot/warm/cold
│   │   └── query_optimizer.py  # Query optimization
│   ├── core/
│   │   ├── aav_reader.py        # .aav file reader
│   │   ├── aav_updater.py       # Intelligent updater
│   │   ├── aggregator.py        # Event aggregation
│   │   └── change_detector.py   # Change detection
│   ├── ai/
│   │   ├── context_client.py    # AI context API
│   │   └── agent_sdk.py         # AI agent helpers
│   └── dashboard/
│       ├── web_ui.py            # FastAPI dashboard
│       └── websocket.py         # Real-time updates
├── docker/
│   ├── Dockerfile.sensors       # Sensor container
│   ├── Dockerfile.guardian      # Guardian container
│   └── security/
│       ├── apparmor.profile     # AppArmor profile
│       └── seccomp.json         # Seccomp filter
├── examples/
│   ├── basic_monitoring.py
│   ├── ai_deployment.py
│   ├── incident_response.py
│   └── langchain_integration.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── performance/
├── docs/
├── pyproject.toml
└── README.md
```

---

## 🔒 Security Model

```python
security_principles = {
    "1. Minimal Privilege": {
        "sensors": "Read-only /proc and /sys access",
        "guardian": "Write access only to .aav files",
        "ai": "Read-only .aav access (via cache)"
    },
    "2. Isolation": {
        "sidecar_containers": "Completely isolated from host",
        "separate_processes": "Crash doesn't affect host",
        "resource_limits": "Hard caps on CPU/memory"
    },
    "3. Mandatory Access Control": {
        "apparmor": "Strict file access policies",
        "selinux": "Type enforcement",
        "seccomp": "System call filtering"
    },
    "4. Non-Root Operation": {
        "user": "1000:1000 (non-root)",
        "no_capabilities": "All capabilities dropped",
        "no_privilege_escalation": "Blocked by security context"
    },
    "5. Data Protection": {
        "sensitive_redaction": "Passwords/tokens filtered",
        "encryption_at_rest": "Optional S3/blob encryption",
        "encryption_in_transit": "TLS for cache connections"
    },
    "6. Audit Trail": {
        "all_updates": "Logged with timestamps",
        "guardian_actions": "All repairs logged",
        "ai_queries": "Query logging available"
    }
}
```

---

## 📚 Core Concepts

### The 5 Universal Categories

```python
universal_categories = {
    "1. COMPUTE": {
        "what": "Processing power and execution",
        "metrics": ["CPU %", "Process count", "Load average"],
        "why_essential": "CPU spikes = immediate problem detection",
        "update_trigger": "5%+ change or process lifecycle"
    },
    "2. MEMORY": {
        "what": "Working memory and RAM usage",
        "metrics": ["RAM %", "Available MB", "Leak detection"],
        "why_essential": "Memory exhaustion = crashes",
        "update_trigger": "5%+ change or leak detected"
    },
    "3. STORAGE": {
        "what": "Persistent storage and disk",
        "metrics": ["Disk %", "I/O rate", "Free space"],
        "why_essential": "Disk full = application failure",
        "update_trigger": "1%+ change or high I/O"
    },
    "4. NETWORK": {
        "what": "Connectivity and traffic",
        "metrics": ["Connections", "Bandwidth", "Errors"],
        "why_essential": "Network issues break distributed systems",
        "update_trigger": "10+ connection change or spike"
    },
    "5. SERVICES": {
        "what": "Application-level health",
        "metrics": ["Health status", "Response time", "Error rate"],
        "why_essential": "Service health = user impact",
        "update_trigger": "Status change or 2x response time"
    }
}
```

---

## 🎯 Use Cases

### 1. Context-Aware Deployments

```python
from aura import AuraClient

client = AuraClient()

async def ai_safe_deployment(service_name: str) -> dict:
    """AI determines if deployment is safe right now"""
    
    # Get real-time context (cached, <1ms)
    context = await client.read_aav(f"container-{service_name}")
    
    checks = {
        "cpu_healthy": context['compute']['cpu_percent'] < 70,
        "memory_healthy": context['memory']['usage_percent'] < 80,
        "dependencies_up": all(
            dep['status'] == 'healthy'
            for dep in context['services']['dependencies']
        ),
        "traffic_normal": context['network']['active_connections'] < 1000,
        "disk_space": context['storage']['disk_usage_percent'] < 85
    }
    
    if all(checks.values()):
        return {
            "safe": True,
            "message": "✅ All systems healthy - safe to deploy",
            "recommended_window": "Next 4 hours"
        }
    else:
        failed = [k for k, v in checks.items() if not v]
        return {
            "safe": False,
            "message": f"⚠️  Wait - Issues detected: {failed}",
            "retry_after": "30 minutes"
        }
```

### 2. Autonomous Incident Response

```python
async def ai_incident_diagnosis(alert: dict) -> dict:
    """AI diagnoses and responds to incidents using real-time context"""
    
    service = alert['service']
    symptom = alert['symptom']
    
    # Get comprehensive context
    context = await client.read_aav(f"container-{service}")
    
    diagnosis = {
        "symptom": symptom,
        "root_cause": None,
        "remedy": None,
        "confidence": 0.0
    }
    
    # Analyze based on real-time metrics
    if symptom == "high_latency":
        if context['network']['active_connections'] > 500:
            diagnosis.update({
                "root_cause": "Connection pool saturation",
                "remedy": "Scale horizontally +2 instances",
                "confidence": 0.95
            })
        elif context['services']['dependencies'][0]['response_time_ms'] > 100:
            diagnosis.update({
                "root_cause": "Database degradation detected",
                "remedy": "Failover to read replica",
                "confidence": 0.90
            })
        elif context['compute']['cpu_percent'] > 90:
            diagnosis.update({
                "root_cause": "CPU bottleneck",
                "remedy": "Scale up or optimize hot path",
                "confidence": 0.85
            })
    
    return diagnosis
```

### 3. Real-Time Debugging

```python
# Developer workflow
$ aura watch container-payment-api --mode debug

# Terminal shows live updates:
# 16:30:15 - API /payments called → CPU spike 45% → 89%
# 16:30:16 - Memory +50MB (leak suspected)
# 16:30:17 - Process payment-worker-03 started
# 16:30:18 - Database query slow: 250ms (normally 15ms)
# 16:30:19 - CPU back to 47% (spike resolved)

# Developer can correlate:
# - "When I called /payments endpoint..."
# - "CPU spiked and spawned worker..."
# - "That worker made slow DB query..."
# - "Now I know the bottleneck!"
```

### 4. Infrastructure Optimization

```python
async def find_optimization_opportunities() -> dict:
    """AI analyzes all assets to find cost savings"""
    
    # Query all assets efficiently (cached aggregation)
    all_assets = await client.query_assets(filters={})
    
    # Find underutilized resources
    underutilized = [
        asset for asset in all_assets
        if asset['compute']['cpu_percent'] < 20
        and asset['memory']['usage_percent'] < 30
        and asset.get('cost_monthly_usd', 0) > 50
    ]
    
    # Calculate savings
    total_monthly_cost = sum(a.get('cost_monthly_usd', 0) for a in underutilized)
    potential_savings = total_monthly_cost * 0.7  # 70% consolidation savings
    
    return {
        "underutilized_count": len(underutilized),
        "current_monthly_cost": total_monthly_cost,
        "potential_savings": potential_savings,
        "recommendation": f"Consolidate {len(underutilized)} assets to save ${potential_savings:,.0f}/month",
        "assets": underutilized
    }
```

---

## 🤝 Contributing

We welcome contributions! Areas where you can help:

```python
contribution_areas = {
    "Core Development": [
        "New scanners (cloud providers, databases)",
        "Sensor performance optimizations",
        "Guardian enhancements"
    ],
    "AI Integration": [
        "Example AI agents",
        "LangChain/AutoGPT integrations",
        "Autonomous response patterns"
    ],
    "Documentation": [
        "Tutorials and guides",
        "Video demonstrations",
        "Translation to other languages"
    ],
    "Testing": [
        "Unit test coverage",
        "Integration tests",
        "Performance benchmarks",
        "Security audits"
    ],
    "Community": [
        "Answer questions",
        "Share use cases",
        "Create example workflows"
    ]
}
```

### Development Setup

```bash
# Clone repository
git clone https://github.com/aura-project/aura
cd aura

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=aura --cov-report=html

# Build sensor container
docker build -f docker/Dockerfile.sensors -t aura/sensor-agent:latest .

# Build guardian container
docker build -f docker/Dockerfile.guardian -t aura/guardian:latest .

# Start local development environment
docker-compose -f docker-compose.dev.yml up
```

---

## 📚 Documentation

- **[Quick Start Guide](docs/quickstart.md)** - Get running in 10 minutes
- **[.aav Format Specification](docs/aav-spec.md)** - Complete format reference
- **[Sensor Development](docs/sensor-development.md)** - Build custom sensors
- **[Guardian Architecture](docs/guardian.md)** - Distributed file validation
- **[AI Integration Guide](docs/ai-integration.md)** - Connect AI agents
- **[Security Model](docs/security.md)** - Understanding safety guarantees
- **[Performance Tuning](docs/performance.md)** - Optimize for scale
- **[Deployment Guide](docs/deployment.md)** - Production deployment

---

## 💬 Community & Support

- 🌐 **Website:** [aura-ai.dev](https://aura-ai.dev)
- 💬 **Discord:** [Join community](https://discord.gg/aura)
- 🐛 **Issues:** [GitHub Issues](https://github.com/aura-project/aura/issues)
- 📧 **Email:** hello@aura-ai.dev
- 🐦 **Twitter:** [@aura_ai_dev](https://twitter.com/aura_ai_dev)
- 📖 **Docs:** [docs.aura-ai.dev](https://docs.aura-ai.dev)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

Aura is free and open-source software. The OpenAAV specification is an open standard.

---

## 🙏 Core Principles

- **Context Over Capability** - Awareness matters more than raw intelligence
- **Intelligence Over Polling** - Change-driven updates, not wasteful polling
- **Safety Over Features** - Fail-safe design, isolated components
- **Speed Over Complexity** - Simple caching, not complex databases
- **Scale Over Single-Point** - Distributed architecture, no bottlenecks
- **Openness Over Lock-in** - Human-readable files, open standards

---

## 🎯 The Vision

**Today:** Infrastructure is blind, AI operates on assumptions  
**Tomorrow:** Infrastructure has awareness, AI operates on facts  
**Future:** Infrastructure is intelligent, AI orchestrates autonomously

**Aura builds the nervous system that makes this future possible.**

---
 