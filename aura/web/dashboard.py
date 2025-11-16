"""
Aura Web Dashboard - Simple web UI for viewing asset status.

Runs on port 8080 by default.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from aura.core.aav import AAVFile


class AuraDashboard:
    """Simple web dashboard for Aura."""

    def __init__(self, assets_dir: str = "./assets", port: int = 8080):
        """Initialize dashboard."""
        self.assets_dir = Path(assets_dir)
        self.port = port

    def get_all_assets(self) -> List[Dict]:
        """Get all assets with their current status."""
        assets = []

        for aav_file in self.assets_dir.glob("*.aav"):
            try:
                aav = AAVFile(aav_file)
                data = aav.read()

                # Extract key metrics
                asset_info = {
                    "id": data['asset']['id'],
                    "name": data['asset'].get('name', data['asset']['id']),
                    "type": data['asset'].get('type', 'unknown'),
                    "status": data['asset'].get('status', 'unknown'),
                    "last_updated": data['metadata'].get('last_updated', ''),
                    "cpu": data.get('compute', {}).get('real_time', {}).get('cpu_percent', 0),
                    "memory": data.get('memory', {}).get('real_time', {}).get('usage_percent', 0),
                    "disk": data.get('storage', {}).get('real_time', {}).get('disk_usage_percent', 0),
                    "load": data.get('compute', {}).get('real_time', {}).get('load_average', [0])[0] if data.get('compute', {}).get('real_time', {}).get('load_average') else 0,
                    "network": data.get('network', {}).get('real_time', {}).get('active_connections', 0),
                }

                assets.append(asset_info)

            except Exception as e:
                print(f"Error reading {aav_file}: {e}")
                continue

        return assets

    def generate_html(self, assets: List[Dict]) -> str:
        """Generate HTML dashboard."""

        # Calculate statistics
        total_assets = len(assets)
        healthy = sum(1 for a in assets if a['cpu'] < 70 and a['memory'] < 80)
        warning = sum(1 for a in assets if (a['cpu'] >= 70 or a['memory'] >= 80) and (a['cpu'] < 85 and a['memory'] < 90))
        critical = sum(1 for a in assets if a['cpu'] >= 85 or a['memory'] >= 90)

        # Get most recent update time
        most_recent = ""
        if assets:
            recent_asset = max(assets, key=lambda x: x.get('last_updated', ''))
            most_recent = self.time_ago(recent_asset.get('last_updated', ''))

        # Generate asset rows
        rows_html = ""
        for asset in assets:
            cpu_class = "critical" if asset['cpu'] >= 85 else "warning" if asset['cpu'] >= 70 else "healthy"
            mem_class = "critical" if asset['memory'] >= 85 else "warning" if asset['memory'] >= 70 else "healthy"
            disk_class = "critical" if asset['disk'] >= 85 else "warning" if asset['disk'] >= 70 else "healthy"

            update_time = self.time_ago(asset['last_updated'])
            update_class = "healthy" if "second" in update_time or "1 minute" in update_time else "warning" if "minute" in update_time else "critical"

            rows_html += f"""
            <tr>
                <td>
                    <strong>{asset['name']}</strong><br>
                    <small style="color: #666;">{asset['type']}</small><br>
                    <small class="{update_class}" style="font-size: 11px;">⏰ {update_time}</small>
                </td>
                <td class="{cpu_class}">{asset['cpu']:.1f}%</td>
                <td class="{mem_class}">{asset['memory']:.1f}%</td>
                <td class="{disk_class}">{asset['disk']:.1f}%</td>
                <td>{asset['load']:.2f}</td>
                <td>{asset['network']}</td>
                <td><small>{update_time}</small></td>
            </tr>
            """

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Aura Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #666;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card h3 {{
            font-size: 36px;
            margin-bottom: 10px;
        }}
        .stat-card p {{
            color: #666;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 1px;
        }}
        .stat-healthy {{ color: #10b981; }}
        .stat-warning {{ color: #f59e0b; }}
        .stat-critical {{ color: #ef4444; }}

        .assets-table {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: #f3f4f6;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #e5e7eb;
        }}
        td {{
            padding: 15px;
            border-bottom: 1px solid #e5e7eb;
        }}
        tr:hover {{
            background: #f9fafb;
        }}
        .healthy {{
            color: #10b981;
            font-weight: 600;
        }}
        .warning {{
            color: #f59e0b;
            font-weight: 600;
        }}
        .critical {{
            color: #ef4444;
            font-weight: 600;
        }}
        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
        }}
        .auto-refresh {{
            background: #3b82f6;
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            font-size: 12px;
            display: inline-block;
            margin-top: 10px;
        }}
    </style>
    <script>
        // Auto-refresh every 5 seconds
        setTimeout(function() {{
            window.location.reload();
        }}, 5000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 Aura Dashboard</h1>
            <p>Real-time infrastructure monitoring</p>
            <div style="margin-top: 15px;">
                <span class="auto-refresh">🔄 Auto-refresh: 5s</span>
                <span class="auto-refresh" style="margin-left: 10px;">⏰ Last update: {most_recent}</span>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3 class="stat-healthy">{total_assets}</h3>
                <p>Total Assets</p>
            </div>
            <div class="stat-card">
                <h3 class="stat-healthy">{healthy}</h3>
                <p>Healthy</p>
            </div>
            <div class="stat-card">
                <h3 class="stat-warning">{warning}</h3>
                <p>Warnings</p>
            </div>
            <div class="stat-card">
                <h3 class="stat-critical">{critical}</h3>
                <p>Critical</p>
            </div>
        </div>

        <div class="assets-table">
            <table>
                <thead>
                    <tr>
                        <th>Asset</th>
                        <th>CPU</th>
                        <th>Memory</th>
                        <th>Disk</th>
                        <th>Load</th>
                        <th>Network</th>
                        <th>Updated</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>Aura - Universal AI Asset Authority</p>
            <p>🕒 Page refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (updates every 5s)</p>
            {f'<p>📊 Most recent data: {most_recent}</p>' if most_recent else ''}
        </div>
    </div>
</body>
</html>
"""
        return html

    def time_ago(self, timestamp_str: str) -> str:
        """Convert timestamp to 'X ago' format."""
        try:
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1] + '+00:00'
            ts = datetime.fromisoformat(timestamp_str)
            now = datetime.now(ts.tzinfo)
            diff = (now - ts).total_seconds()

            if diff < 60:
                return f"{int(diff)}s ago"
            elif diff < 3600:
                return f"{int(diff / 60)}m ago"
            elif diff < 86400:
                return f"{int(diff / 3600)}h ago"
            else:
                return f"{int(diff / 86400)}d ago"
        except Exception:
            return "unknown"

    async def handle_request(self, reader, writer):
        """Handle HTTP request."""
        try:
            # Read request
            request = await reader.read(1024)

            # Get assets
            assets = self.get_all_assets()

            # Generate HTML
            html = self.generate_html(assets)

            # Send response
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{html}"
            writer.write(response.encode())
            await writer.drain()

        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def start(self):
        """Start the web server."""
        server = await asyncio.start_server(
            self.handle_request,
            '0.0.0.0',
            self.port
        )

        print(f"🌐 Aura Dashboard running on http://0.0.0.0:{self.port}")
        print(f"📊 Monitoring: {self.assets_dir}")
        print(f"🔄 Auto-refresh: 5 seconds")
        print(f"\nPress Ctrl+C to stop")

        async with server:
            await server.serve_forever()


def main():
    """Run dashboard."""
    import sys

    assets_dir = sys.argv[1] if len(sys.argv) > 1 else "./assets"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080

    dashboard = AuraDashboard(assets_dir=assets_dir, port=port)

    try:
        asyncio.run(dashboard.start())
    except KeyboardInterrupt:
        print("\n\n✅ Dashboard stopped")


if __name__ == "__main__":
    main()
