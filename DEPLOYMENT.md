# Aura VPS Deployment Guide

## Quick Start (One Command)

```bash
cd /root && rm -rf Aura && git clone https://github.com/tajalagawani/Aura.git && cd Aura && chmod +x deploy.sh && ./deploy.sh
```

## What the Deployment Script Does

The `deploy.sh` script is a production-grade installer that automatically:

✅ **Pre-flight Checks**
- Verifies running as root
- Checks internet connection
- Installs Git if needed

✅ **Python Installation**
- Installs Python 3.11+ if needed
- Sets up pip

✅ **User & Directories**
- Creates `aura` service user
- Creates `/opt/aura` (installation)
- Creates `/var/lib/aura/assets` (AAV files)
- Creates `/var/log/aura` (logs)

✅ **Repository**
- Clones from GitHub
- Backs up existing installation

✅ **Package Installation**
- Installs Aura package
- Installs optional dependencies

✅ **Services**
- Creates systemd services
- Configures auto-restart
- Sets resource limits
- Applies security hardening

✅ **Auto-Update**
- Creates update script
- Configures systemd timer (checks every 5 min)
- Enables automatic updates

✅ **Firewall**
- Opens ports 22 (SSH) and 8080 (Dashboard)
- Enables ufw

✅ **Initial Scan**
- Runs system scanner
- Runs port scanner
- Creates initial AAV files

✅ **Health Checks**
- Verifies services running
- Checks dashboard responding
- Validates AAV files created

## Post-Deployment

### Access Dashboard

```
http://YOUR_VPS_IP:8080
```

### Check Services

```bash
systemctl status aura-monitor
systemctl status aura-dashboard
systemctl status aura-update.timer
```

### View Logs

```bash
journalctl -u aura-monitor -f
journalctl -u aura-dashboard -f
tail -f /var/log/aura/monitor.log
```

### Run Scanners

```bash
aura scan all
aura scan ports --include-stats
aura scan processes --min-cpu 5.0
```

### View Assets

```bash
aura status --summary
ls -lh /var/lib/aura/assets/
```

## Features

See `ONE_LINER.txt` for complete feature list and troubleshooting guide.
