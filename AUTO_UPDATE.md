# Aura Auto-Update System

Automatically pulls and installs updates from GitHub every 5 minutes.

## Quick Setup

On your VPS, run:

```bash
cd /root/Aura
git pull
chmod +x setup-auto-update.sh
sudo ./setup-auto-update.sh
```

That's it! Aura will now auto-update every 5 minutes.

## How It Works

1. **Timer**: Systemd timer runs every 5 minutes
2. **Check**: Script checks GitHub for new commits
3. **Update**: If updates found, pulls changes and reinstalls
4. **Restart**: Automatically restarts monitoring and dashboard services
5. **Log**: All updates logged to `/var/log/aura-update.log`

## What Gets Updated

When you push changes to GitHub:
- ✅ Code changes (sensors, dashboard, services)
- ✅ Bug fixes
- ✅ New features
- ✅ Configuration updates

The VPS will automatically:
1. Detect the changes (within 5 minutes)
2. Pull the latest code
3. Reinstall the package
4. Restart services
5. Continue monitoring without interruption

## Management Commands

### Check Auto-Update Status

```bash
# Check timer status
sudo systemctl status aura-update.timer

# Check last update
sudo systemctl status aura-update.service

# View update log
tail -f /var/log/aura-update.log

# View systemd journal
sudo journalctl -u aura-update.service -f
```

### Manual Update

Trigger an update immediately:

```bash
sudo systemctl start aura-update.service
```

### Disable Auto-Updates

```bash
# Stop timer
sudo systemctl stop aura-update.timer

# Disable timer (won't start on boot)
sudo systemctl disable aura-update.timer
```

### Re-enable Auto-Updates

```bash
sudo systemctl enable aura-update.timer
sudo systemctl start aura-update.timer
```

## Update Frequency

Default: **Every 5 minutes**

To change frequency, edit the timer:

```bash
sudo nano /etc/systemd/system/aura-update.timer
```

Change this line:
```
OnUnitActiveSec=5min
```

Options:
- `OnUnitActiveSec=1min` - Every 1 minute (very frequent)
- `OnUnitActiveSec=10min` - Every 10 minutes
- `OnUnitActiveSec=30min` - Every 30 minutes
- `OnUnitActiveSec=1h` - Every hour

Then reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart aura-update.timer
```

## Monitoring Updates

### Watch Updates Live

```bash
tail -f /var/log/aura-update.log
```

### Check Update History

```bash
cat /var/log/aura-update.log
```

### Example Log Output

```
[2025-11-16 18:30:00] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2025-11-16 18:30:00] 🔍 Checking for Aura updates...
[2025-11-16 18:30:01] 📥 New updates available!
[2025-11-16 18:30:01]    Current: a1b2c3d
[2025-11-16 18:30:01]    Latest:  e4f5g6h
[2025-11-16 18:30:01] 📦 Pulling updates...
[2025-11-16 18:30:05] 🔧 Reinstalling Aura package...
[2025-11-16 18:30:10] 🔄 Restarting services...
[2025-11-16 18:30:13] ✅ Monitor service: RUNNING
[2025-11-16 18:30:13] ✅ Dashboard service: RUNNING
[2025-11-16 18:30:13] ✅ Update complete! (now at e4f5g6h)
[2025-11-16 18:30:13] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Troubleshooting

### Updates Not Running

```bash
# Check timer is active
sudo systemctl status aura-update.timer

# Check for errors
sudo journalctl -u aura-update.service -n 50

# Manually trigger to see errors
sudo systemctl start aura-update.service
```

### Services Failed After Update

```bash
# Check service status
sudo systemctl status aura-monitor
sudo systemctl status aura-dashboard

# View logs
sudo journalctl -u aura-monitor -n 50
sudo journalctl -u aura-dashboard -n 50

# Manually restart
sudo systemctl restart aura-monitor
sudo systemctl restart aura-dashboard
```

### Git Pull Conflicts

If auto-update fails due to conflicts:

```bash
# Reset to remote version
cd /opt/aura
sudo git reset --hard origin/master
sudo git pull
sudo systemctl restart aura-monitor aura-dashboard
```

## Development Workflow

With auto-update enabled, your workflow is simple:

1. **Make changes locally** on your machine
2. **Commit changes**:
   ```bash
   git add -A
   git commit -m "fix: improve sensor accuracy"
   ```
3. **Push to GitHub**:
   ```bash
   git push origin master
   ```
4. **Wait 5 minutes** - VPS automatically updates!
5. **Check dashboard** - Changes are live!

## Safety Features

- ✅ **Zero Downtime**: Services restart gracefully
- ✅ **Logging**: All updates logged for audit trail
- ✅ **Error Handling**: Failed updates don't break services
- ✅ **Atomic**: Pull succeeds or rolls back
- ✅ **Fast**: Updates complete in <10 seconds

## Uninstall Auto-Update

To remove the auto-update system:

```bash
# Stop and disable timer
sudo systemctl stop aura-update.timer
sudo systemctl disable aura-update.timer

# Remove service files
sudo rm /etc/systemd/system/aura-update.service
sudo rm /etc/systemd/system/aura-update.timer

# Remove script
sudo rm /opt/aura/auto-update.sh

# Reload systemd
sudo systemctl daemon-reload
```

## Production Recommendations

1. **Test changes locally first** before pushing
2. **Use branches** for experimental features
3. **Monitor logs** after pushing updates
4. **Keep update frequency** at 5-10 minutes for production

## Summary

Auto-update enabled means:
- ✅ Push code changes to GitHub
- ✅ VPS automatically updates within 5 minutes
- ✅ Services restart automatically
- ✅ Zero manual intervention needed
- ✅ Full logging of all updates

Your development cycle is now:
**Code → Commit → Push → Wait 5 min → Live on VPS** 🚀
