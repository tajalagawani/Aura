# Aura VPS Deployment Guide

## Quick VPS Deploy (2 Commands)

```bash
# SSH to your VPS
ssh root@92.112.181.127

# Clone and deploy
git clone https://github.com/tajalagawani/Aura.git && cd Aura && ./deploy-vps.sh
```

That's it! Aura will be fully deployed with:
- ✅ Real-time monitoring service (auto-starts on boot)
- ✅ Web dashboard on port 8080
- ✅ Automatic AAV file updates
- ✅ Systemd services for reliability

## What Happens During Deployment

The `deploy-vps.sh` script automatically:

1. ✅ Checks Python 3.11+ (installs if needed)
2. ✅ Creates `aura` system user
3. ✅ Creates directories:
   - `/opt/aura` - Installation directory
   - `/var/lib/aura/assets` - AAV files directory
4. ✅ Installs Aura package
5. ✅ Creates two systemd services:
   - `aura-monitor.service` - Real-time monitoring
   - `aura-dashboard.service` - Web dashboard
6. ✅ Starts services and collects initial metrics
7. ✅ Shows you the dashboard URL

## After Deployment

### Access Web Dashboard

Open in your browser:
```
http://92.112.181.127:8080
```

You'll see a beautiful dashboard with:
- 📊 Total assets, healthy/warning/critical counts
- 📈 Real-time metrics table (auto-refreshes every 5 seconds)
- 🎨 Color-coded status (green/yellow/red)
- ⏰ Last updated timestamps

### Service Management

```bash
# Check service status
sudo systemctl status aura-monitor
sudo systemctl status aura-dashboard

# Restart services
sudo systemctl restart aura-monitor
sudo systemctl restart aura-dashboard

# View logs (live tail)
sudo journalctl -u aura-monitor -f
sudo journalctl -u aura-dashboard -f

# Stop services
sudo systemctl stop aura-monitor
sudo systemctl stop aura-dashboard
```

### View AAV Files

```bash
# List all AAV files
ls -lh /var/lib/aura/assets/

# View AAV file content
cat /var/lib/aura/assets/*.aav

# Watch file updates in real-time
watch -n 1 "cat /var/lib/aura/assets/*.aav | grep cpu_percent"
```

## Services Explained

### aura-monitor.service

This service:
- Runs continuously (24/7)
- Updates AAV files in real-time
- Monitors: CPU, Memory, Disk, Network
- Auto-restarts on failure
- Starts automatically on boot

Location: `/etc/systemd/system/aura-monitor.service`

### aura-dashboard.service

This service:
- Runs web server on port 8080
- Serves the dashboard UI
- Reads AAV files from `/var/lib/aura/assets`
- Auto-refreshes every 5 seconds
- Auto-restarts on failure

Location: `/etc/systemd/system/aura-dashboard.service`

## Firewall Configuration

If you have a firewall, open port 8080:

```bash
# UFW (Ubuntu)
sudo ufw allow 8080/tcp
sudo ufw reload

# firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload

# iptables
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables-save > /etc/iptables/rules.v4
```

## Customization

### Change Dashboard Port

Edit the service file:

```bash
sudo nano /etc/systemd/system/aura-dashboard.service
```

Change the `ExecStart` line:
```
ExecStart=/usr/bin/python3 -m aura.web.dashboard /var/lib/aura/assets 9000
```

Then reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart aura-dashboard
```

### Monitor Multiple Assets

To monitor additional servers, install Aura on each server:

```bash
# On each server
git clone https://github.com/tajalagawani/Aura.git
cd Aura
./deploy-vps.sh
```

Each server will have its own dashboard at `http://<server-ip>:8080`

### Centralized Dashboard (Advanced)

To view all servers from one dashboard:

1. **Use shared storage:**
   ```bash
   # Mount NFS share for assets
   sudo mkdir -p /mnt/shared-assets
   sudo mount -t nfs nfs-server:/exports/aura /mnt/shared-assets

   # Update service to use shared storage
   sudo nano /etc/systemd/system/aura-monitor.service
   # Change: /var/lib/aura/assets to /mnt/shared-assets
   ```

2. **Or collect AAV files periodically:**
   ```bash
   # On dashboard server, collect from all servers
   scp root@server1:/var/lib/aura/assets/*.aav /var/lib/aura/assets/
   scp root@server2:/var/lib/aura/assets/*.aav /var/lib/aura/assets/
   ```

## Monitoring the Monitoring

Check that AAV files are being updated:

```bash
# Check file modification time
stat /var/lib/aura/assets/*.aav

# Watch updates in real-time
watch -n 1 "ls -lh /var/lib/aura/assets/"

# Check last_updated field
cat /var/lib/aura/assets/*.aav | grep last_updated
```

## Troubleshooting

### Services not starting

```bash
# Check logs
sudo journalctl -u aura-monitor -n 50
sudo journalctl -u aura-dashboard -n 50

# Check service status
sudo systemctl status aura-monitor
sudo systemctl status aura-dashboard
```

### Dashboard not accessible

```bash
# Check if service is running
sudo systemctl status aura-dashboard

# Check if port is listening
sudo netstat -tulpn | grep 8080

# Test locally
curl http://localhost:8080
```

### High CPU/Memory usage

```bash
# Check resource usage
sudo systemctl status aura-monitor

# Adjust sensor intervals (edit sensor code)
sudo nano /opt/aura/aura/sensors/base.py
# Change: self.interval = 5  # to higher value
```

### AAV files not updating

```bash
# Check monitor service
sudo systemctl status aura-monitor

# Restart monitor
sudo systemctl restart aura-monitor

# Check permissions
ls -la /var/lib/aura/assets/
```

## Uninstall

To completely remove Aura:

```bash
# Stop and disable services
sudo systemctl stop aura-monitor aura-dashboard
sudo systemctl disable aura-monitor aura-dashboard

# Remove service files
sudo rm /etc/systemd/system/aura-monitor.service
sudo rm /etc/systemd/system/aura-dashboard.service
sudo systemctl daemon-reload

# Remove installation
sudo rm -rf /opt/aura
sudo rm -rf /var/lib/aura

# Remove user (optional)
sudo userdel aura
```

## Production Recommendations

1. **Use NGINX reverse proxy:**
   ```nginx
   server {
       listen 80;
       server_name aura.yourdomain.com;

       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
       }
   }
   ```

2. **Enable HTTPS with Let's Encrypt:**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d aura.yourdomain.com
   ```

3. **Setup log rotation:**
   ```bash
   sudo nano /etc/logrotate.d/aura
   ```
   ```
   /var/log/aura/*.log {
       daily
       rotate 7
       compress
       missingok
       notifempty
   }
   ```

4. **Monitor disk space:**
   AAV files are small (~5KB), but monitor growth:
   ```bash
   du -sh /var/lib/aura/assets/
   ```

## Support

If you encounter issues:

1. Check logs: `sudo journalctl -u aura-monitor -f`
2. Verify services: `sudo systemctl status aura-*`
3. Test manually: `python3 -m aura.service.monitor /var/lib/aura/assets`

## Summary

After deployment, you have:

- ✅ **Monitoring service**: Running 24/7, updating AAV files in real-time
- ✅ **Web dashboard**: Accessible at http://92.112.181.127:8080
- ✅ **Auto-start**: Services start automatically on boot
- ✅ **Auto-restart**: Services restart on failure
- ✅ **Systemd integration**: Full system management

The AAV files are continuously updated at:
```
/var/lib/aura/assets/<hostname>.aav
```

Access the beautiful web dashboard:
```
http://92.112.181.127:8080
```

Everything runs automatically - just enjoy the real-time monitoring! 🎉
