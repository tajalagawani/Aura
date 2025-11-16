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
                    "file_path": str(aav_file.name),
                }

                assets.append(asset_info)

            except Exception as e:
                print(f"Error reading {aav_file}: {e}")
                continue

        return assets

    def get_aav_content(self, filename: str) -> str:
        """Get raw AAV file content."""
        try:
            aav_file = self.assets_dir / filename
            if not aav_file.exists():
                return f"Error: File {filename} not found"

            return aav_file.read_text()
        except Exception as e:
            return f"Error reading file: {e}"

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

        # Separate assets by type
        servers = [a for a in assets if a['type'] in ['system', 'server']]
        ports = [a for a in assets if a['type'] == 'port']
        processes = [a for a in assets if a['type'] == 'process']
        containers = [a for a in assets if a['type'] == 'container']

        # Generate servers section
        rows_html = ""

        if servers:
            rows_html += '<tr style="background: #f3f4f6;"><td colspan="7" style="font-weight: bold; padding: 10px;">🖥️ SERVERS</td></tr>'
            for asset in servers:
                cpu_class = "critical" if asset['cpu'] >= 85 else "warning" if asset['cpu'] >= 70 else "healthy"
                mem_class = "critical" if asset['memory'] >= 85 else "warning" if asset['memory'] >= 70 else "healthy"
                disk_class = "critical" if asset['disk'] >= 85 else "warning" if asset['disk'] >= 70 else "healthy"

                # Status emoji
                status_emoji = "🔴" if asset['cpu'] >= 85 or asset['memory'] >= 85 else "⚠️" if asset['cpu'] >= 70 or asset['memory'] >= 70 else "✅"

                rows_html += f"""
                <tr onclick="viewAAV('{asset['file_path']}')" style="cursor: pointer;">
                    <td>
                        <span style="font-size: 20px;">{status_emoji}</span>
                        <strong style="margin-left: 10px;">{asset['name']}</strong>
                    </td>
                    <td class="{cpu_class}" style="font-size: 16px;">{asset['cpu']:.1f}%</td>
                    <td class="{mem_class}" style="font-size: 16px;">{asset['memory']:.1f}%</td>
                    <td class="{disk_class}" style="font-size: 16px;">{asset['disk']:.1f}%</td>
                    <td style="font-size: 16px;">{asset['load']:.2f}</td>
                    <td style="font-size: 16px;">{asset['network']}</td>
                    <td>
                        <button onclick="event.stopPropagation(); viewAAV('{asset['file_path']}')"
                                style="padding: 8px 16px; background: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 13px; font-weight: 600;">
                            📄 Details
                        </button>
                    </td>
                </tr>
                """

        if ports:
            rows_html += '<tr style="background: #f3f4f6;"><td colspan="7" style="font-weight: bold; padding: 10px;">🔌 OPEN PORTS ({len(ports)} services)</td></tr>'
            for asset in ports[:10]:  # Show top 10 ports only
                service_emoji = "🌐" if "http" in asset['name'].lower() else "🔐" if "ssh" in asset['name'].lower() else "💾" if "mongo" in asset['name'].lower() or "mysql" in asset['name'].lower() else "📡"

                rows_html += f"""
                <tr onclick="viewAAV('{asset['file_path']}')" style="cursor: pointer;">
                    <td>
                        <span style="font-size: 20px;">{service_emoji}</span>
                        <strong style="margin-left: 10px;">{asset['name']}</strong>
                    </td>
                    <td colspan="5" style="color: #666;">Network: {asset['network']} connections</td>
                    <td>
                        <button onclick="event.stopPropagation(); viewAAV('{asset['file_path']}')"
                                style="padding: 8px 16px; background: #3b82f6; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 13px; font-weight: 600;">
                            📄 Details
                        </button>
                    </td>
                </tr>
                """

            if len(ports) > 10:
                rows_html += f'<tr><td colspan="7" style="text-align: center; color: #666; padding: 10px;">+ {len(ports) - 10} more ports...</td></tr>'

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

        /* Modal styles */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.7);
        }}
        .modal-content {{
            background-color: white;
            margin: 2% auto;
            padding: 0;
            border-radius: 10px;
            width: 90%;
            max-width: 1200px;
            height: 90%;
            display: flex;
            flex-direction: column;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        .modal-header {{
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .modal-header h2 {{
            margin: 0;
            font-size: 20px;
        }}
        .close {{
            color: white;
            font-size: 35px;
            font-weight: bold;
            cursor: pointer;
            line-height: 1;
        }}
        .close:hover {{
            opacity: 0.8;
        }}
        .modal-body {{
            padding: 20px;
            overflow-y: auto;
            flex: 1;
        }}
        .aav-content {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
            overflow-x: auto;
        }}
        .copy-btn {{
            background: #10b981;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin: 10px 0;
        }}
        .copy-btn:hover {{
            background: #059669;
        }}
    </style>
    <script>
        let autoRefreshTimer;

        // Auto-refresh every 5 seconds (only when modal is closed)
        function startAutoRefresh() {{
            autoRefreshTimer = setTimeout(function() {{
                window.location.reload();
            }}, 5000);
        }}

        function stopAutoRefresh() {{
            if (autoRefreshTimer) {{
                clearTimeout(autoRefreshTimer);
            }}
        }}

        // Start auto-refresh on page load
        window.onload = function() {{
            startAutoRefresh();
        }};

        // View AAV file
        function viewAAV(filename) {{
            stopAutoRefresh();

            const modal = document.getElementById('aavModal');
            const modalTitle = document.getElementById('modalTitle');
            const aavContent = document.getElementById('aavContent');

            modalTitle.textContent = '📄 ' + filename;
            aavContent.textContent = 'Loading...';
            modal.style.display = 'block';

            fetch('/aav/' + filename)
                .then(response => response.text())
                .then(data => {{
                    aavContent.textContent = data;
                }})
                .catch(error => {{
                    aavContent.textContent = 'Error loading AAV file: ' + error;
                }});
        }}

        // Close modal
        function closeModal() {{
            document.getElementById('aavModal').style.display = 'none';
            startAutoRefresh();
        }}

        // Copy AAV content
        function copyAAV() {{
            const aavContent = document.getElementById('aavContent');
            navigator.clipboard.writeText(aavContent.textContent).then(function() {{
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = '✅ Copied!';
                setTimeout(function() {{
                    btn.textContent = originalText;
                }}, 2000);
            }});
        }}

        // Close modal when clicking outside
        window.onclick = function(event) {{
            const modal = document.getElementById('aavModal');
            if (event.target == modal) {{
                closeModal();
            }}
        }}

        // Close modal with Escape key
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                closeModal();
            }}
        }});
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 Infrastructure Monitor</h1>
            <p style="font-size: 18px; margin-top: 10px;">Simple view of your servers and services</p>
            <div style="margin-top: 15px;">
                <span class="auto-refresh">🔄 Updates every 5 seconds</span>
                <span class="auto-refresh" style="margin-left: 10px;">⏰ Last check: {most_recent}</span>
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3 class="stat-healthy">{len([a for a in assets if a['type'] in ['system', 'server']])}</h3>
                <p>SERVERS</p>
            </div>
            <div class="stat-card">
                <h3 class="stat-healthy">{healthy}</h3>
                <p>✅ RUNNING GOOD</p>
            </div>
            <div class="stat-card">
                <h3 class="stat-warning">{warning}</h3>
                <p>⚠️ NEED ATTENTION</p>
            </div>
            <div class="stat-card">
                <h3 class="stat-critical">{critical}</h3>
                <p>🔴 PROBLEMS</p>
            </div>
        </div>

        <div class="assets-table">
            <table>
                <thead>
                    <tr>
                        <th style="font-size: 16px;">NAME</th>
                        <th style="font-size: 16px;">CPU USAGE</th>
                        <th style="font-size: 16px;">MEMORY</th>
                        <th style="font-size: 16px;">DISK</th>
                        <th style="font-size: 16px;">LOAD</th>
                        <th style="font-size: 16px;">CONNECTIONS</th>
                        <th style="font-size: 16px;">ACTION</th>
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

    <!-- AAV Viewer Modal -->
    <div id="aavModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">AAV File Viewer</h2>
                <span class="close" onclick="closeModal()">&times;</span>
            </div>
            <div class="modal-body">
                <button class="copy-btn" onclick="copyAAV()">📋 Copy to Clipboard</button>
                <div class="aav-content" id="aavContent">Loading...</div>
            </div>
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
            request_line = request.decode('utf-8').split('\r\n')[0]

            # Parse request
            parts = request_line.split(' ')
            if len(parts) >= 2:
                method = parts[0]
                path = parts[1]

                # Handle AAV file requests
                if path.startswith('/aav/'):
                    filename = path[5:]  # Remove '/aav/' prefix
                    aav_content = self.get_aav_content(filename)

                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n{aav_content}"
                    writer.write(response.encode('utf-8'))
                    await writer.drain()
                    return

            # Default: serve dashboard
            assets = self.get_all_assets()
            html = self.generate_html(assets)

            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n\r\n{html}"
            writer.write(response.encode('utf-8'))
            await writer.drain()

        except Exception as e:
            print(f"Error handling request: {e}")
            error_response = f"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nError: {e}"
            writer.write(error_response.encode())
            await writer.drain()
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
