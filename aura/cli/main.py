"""
Aura CLI - Beautiful Command Line Interface.

Provides commands for:
- Viewing live infrastructure status
- Querying assets with filters
- Watching real-time updates
- Validating file integrity
- Deployment safety checks

Example:
    $ aura status container-payment-api
    $ aura query --filter "cpu > 80"
    $ aura watch container-payment-api
"""

import asyncio
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import click

from aura import __version__
from aura.ai.context_client import AuraClient
from aura.core.aav import AAVFile
from aura.guardian.validator import AAVValidator


def format_bar(percent: float, width: int = 20) -> str:
    """Create a visual bar for percentage display."""
    filled = int((percent / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    return bar


def get_status_emoji(percent: float, warning: float = 70, critical: float = 85) -> str:
    """Get status emoji based on percentage."""
    if percent >= critical:
        return "🔴"
    elif percent >= warning:
        return "⚠️ "
    else:
        return "✅"


def get_status_text(percent: float, warning: float = 70, critical: float = 85) -> str:
    """Get status text based on percentage."""
    if percent >= critical:
        return "Critical"
    elif percent >= warning:
        return "Warning"
    else:
        return "Normal"


def time_ago(timestamp_str: str) -> str:
    """Convert timestamp to 'X seconds/minutes ago' format."""
    try:
        # Parse timestamp
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str[:-1] + '+00:00'
        ts = datetime.fromisoformat(timestamp_str)
        now = datetime.now(timezone.utc)

        diff = (now - ts).total_seconds()

        if diff < 60:
            return f"{int(diff)} seconds ago"
        elif diff < 3600:
            return f"{int(diff / 60)} minutes ago"
        elif diff < 86400:
            return f"{int(diff / 3600)} hours ago"
        else:
            return f"{int(diff / 86400)} days ago"
    except Exception:
        return "unknown"


def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)

    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    """
    Aura - Universal AI Asset Authority.

    Provides real-time infrastructure context for AI agents.
    """
    pass


@cli.command()
@click.argument("asset_id", required=False)
@click.option(
    "--assets-dir",
    default="./assets",
    help="Directory containing .aav files"
)
@click.option(
    "--summary",
    is_flag=True,
    help="Show summary view of all assets"
)
def status(asset_id: Optional[str], assets_dir: str, summary: bool) -> None:
    """
    Display infrastructure status.

    Show detailed status for a single asset or summary of all assets.

    Examples:
        $ aura status container-payment-api --assets-dir ./assets
        $ aura status --summary --assets-dir ./assets
    """
    assets_path = Path(assets_dir)

    if not assets_path.exists():
        click.echo(f"❌ Assets directory not found: {assets_dir}", err=True)
        sys.exit(1)

    aav_files = list(assets_path.glob("*.aav"))

    if not aav_files:
        click.echo(f"📭 No assets found in {assets_dir}")
        click.echo(f"\nTo create sample data, run:")
        click.echo(f"  python quick_test.py")
        return

    # Show specific asset
    if asset_id:
        show_asset_status(asset_id, assets_dir)
        return

    # Show summary of all assets
    if summary:
        show_summary_status(assets_path, aav_files)
    else:
        show_all_assets(assets_path, aav_files)


def show_asset_status(asset_id: str, assets_dir: str) -> None:
    """Show detailed status for a single asset."""
    aav_file = Path(assets_dir) / f"{asset_id}.aav"

    if not aav_file.exists():
        click.echo(f"❌ Asset not found: {asset_id}", err=True)
        sys.exit(1)

    try:
        aav = AAVFile(aav_file)
        data = aav.read()

        # Header
        asset_name = data['asset'].get('name', asset_id)
        asset_type = data['asset'].get('type', 'unknown')
        last_updated = data['metadata'].get('last_updated', '')

        click.echo(f"\n📊 {asset_name} - Live Status")
        click.echo("━" * 60)
        click.echo(f"Updated: {time_ago(last_updated)}\n")

        # COMPUTE
        compute = data.get('compute', {}).get('real_time', {})
        cpu = compute.get('cpu_percent', 0)
        load = compute.get('load_average', [0, 0, 0])
        processes = compute.get('process_count', 0)

        cpu_status = get_status_text(cpu)
        click.echo(f"💻 COMPUTE")
        click.echo(f"   CPU:       {cpu:5.1f}% {format_bar(cpu)} {cpu_status}")
        click.echo(f"   Load:      {load[0]:.2f}" if load else "   Load:      N/A")
        click.echo(f"   Processes: {processes}")

        # MEMORY
        memory = data.get('memory', {}).get('real_time', {})
        mem_pct = memory.get('usage_percent', 0)
        mem_avail = memory.get('available_mb', 0) / 1024  # Convert to GB
        mem_trend = data.get('memory', {}).get('analysis', {}).get('trend', 'stable')

        mem_status = get_status_text(mem_pct)
        click.echo(f"\n🧠 MEMORY")
        click.echo(f"   Usage:     {mem_pct:5.1f}% {format_bar(mem_pct)} {mem_status}")
        click.echo(f"   Available: {mem_avail:.1f} GB")
        click.echo(f"   Trend:     {mem_trend.title()}")

        # STORAGE
        storage = data.get('storage', {}).get('real_time', {})
        disk_pct = storage.get('disk_usage_percent', 0)
        disk_free = storage.get('free_gb', 0)
        io_read = storage.get('io_read_mb_per_sec', 0)
        io_write = storage.get('io_write_mb_per_sec', 0)

        disk_status = get_status_text(disk_pct)
        click.echo(f"\n💾 STORAGE")
        click.echo(f"   Usage:     {disk_pct:5.1f}% {format_bar(disk_pct)} {disk_status}")
        click.echo(f"   Free:      {disk_free:.1f} GB")
        click.echo(f"   I/O:       Read {io_read:.1f} MB/s, Write {io_write:.1f} MB/s")

        # NETWORK
        network = data.get('network', {}).get('real_time', {})
        connections = network.get('active_connections', 0)
        traffic_in = network.get('bytes_recv_mb_per_sec', 0)
        traffic_out = network.get('bytes_sent_mb_per_sec', 0)

        click.echo(f"\n🌐 NETWORK")
        click.echo(f"   Connections: {connections} active")
        if traffic_in or traffic_out:
            click.echo(f"   Traffic:     In {traffic_in:.1f} MB/s, Out {traffic_out:.1f} MB/s")

        # SERVICES
        services = data.get('services', {})
        app_data = services.get('application', {})
        health = app_data.get('health_status', 'unknown')
        version = app_data.get('version', 'unknown')
        uptime = app_data.get('uptime_seconds', 0)

        health_icon = "✅" if health == "healthy" else "❌"
        click.echo(f"\n{health_icon} SERVICES")
        click.echo(f"   Health:    {health.upper()} {'✓' if health == 'healthy' else '✗'}")
        if version != 'unknown':
            click.echo(f"   Version:   {version}")
        if uptime > 0:
            click.echo(f"   Uptime:    {format_uptime(uptime)}")

        # RECENT EVENTS
        events = compute.get('events', {}).get('recent', data.get('compute', {}).get('events', {}).get('recent', []))
        if events and len(events) > 0:
            click.echo(f"\n📋 RECENT EVENTS")
            for event in events[:3]:  # Show last 3 events
                ts = event.get('timestamp', '')
                event_type = event.get('event', '')
                pid = event.get('pid', '')
                click.echo(f"   {time_ago(ts)} - {event_type.replace('_', ' ').title()}")

        # RECOMMENDATIONS
        click.echo(f"\n💡 RECOMMENDATIONS")
        if cpu >= 85 or mem_pct >= 85 or disk_pct >= 85:
            click.echo(f"   ⚠️  High resource usage detected. Consider scaling.")
        else:
            click.echo(f"   All systems operating normally. No action needed.")

        click.echo()

    except Exception as e:
        click.echo(f"❌ Error reading asset: {e}", err=True)
        sys.exit(1)


def show_summary_status(assets_path: Path, aav_files: list) -> None:
    """Show summary view of all assets."""
    click.echo(f"\n📊 Aura Status - {len(aav_files)} assets monitored\n")
    click.echo("━" * 100)

    healthy_count = 0
    warning_count = 0
    critical_count = 0

    for aav_file in aav_files:
        try:
            aav = AAVFile(aav_file)
            data = aav.read()

            asset_id = data['asset']['id']
            asset_type = data['asset'].get('type', 'unknown')

            cpu = data.get('compute', {}).get('real_time', {}).get('cpu_percent', 0)
            memory = data.get('memory', {}).get('real_time', {}).get('usage_percent', 0)
            disk = data.get('storage', {}).get('real_time', {}).get('disk_usage_percent', 0)

            # Determine overall status
            max_usage = max(cpu, memory, disk)
            if max_usage >= 85:
                status_emoji = "🔴"
                critical_count += 1
            elif max_usage >= 70:
                status_emoji = "⚠️ "
                warning_count += 1
            else:
                status_emoji = "✅"
                healthy_count += 1

            click.echo(
                f"{status_emoji} {asset_id:35} | {asset_type:12} | "
                f"CPU: {cpu:5.1f}% | Mem: {memory:5.1f}% | Disk: {disk:5.1f}%"
            )

        except Exception as e:
            click.echo(f"❌ {aav_file.name:35} | Error: {e}")

    click.echo("━" * 100)
    click.echo(f"\n📈 Summary: ✅ {healthy_count} healthy  |  ⚠️  {warning_count} warnings  |  🔴 {critical_count} critical\n")


def show_all_assets(assets_path: Path, aav_files: list) -> None:
    """Show detailed view of all assets."""
    click.echo(f"\n📊 Aura Status - {len(aav_files)} assets monitored\n")

    for aav_file in aav_files[:5]:  # Show first 5 in detail
        try:
            aav = AAVFile(aav_file)
            data = aav.read()

            asset_id = data['asset']['id']
            cpu = data.get('compute', {}).get('real_time', {}).get('cpu_percent', 0)
            memory = data.get('memory', {}).get('real_time', {}).get('usage_percent', 0)
            disk = data.get('storage', {}).get('real_time', {}).get('disk_usage_percent', 0)

            click.echo(f"📦 {asset_id}")
            click.echo(f"   💻 CPU:    {cpu:5.1f}% {format_bar(cpu, 15)}")
            click.echo(f"   🧠 Memory: {memory:5.1f}% {format_bar(memory, 15)}")
            click.echo(f"   💾 Disk:   {disk:5.1f}% {format_bar(disk, 15)}")
            click.echo()

        except Exception as e:
            click.echo(f"❌ Error reading {aav_file.name}: {e}\n")

    if len(aav_files) > 5:
        click.echo(f"... and {len(aav_files) - 5} more assets")
        click.echo(f"\nUse --summary for overview of all assets")


@cli.command()
@click.argument("asset_id")
@click.option(
    "--assets-dir",
    default="./assets",
    help="Directory containing .aav files"
)
@click.option(
    "--interval",
    default=5,
    type=int,
    help="Update interval in seconds"
)
def watch(asset_id: str, assets_dir: str, interval: int) -> None:
    """
    Watch live updates for an asset.

    Updates every N seconds. Press Ctrl+C to stop.

    Example:
        $ aura watch container-payment-api --assets-dir ./assets
    """
    aav_file = Path(assets_dir) / f"{asset_id}.aav"

    if not aav_file.exists():
        click.echo(f"❌ Asset not found: {asset_id}", err=True)
        sys.exit(1)

    click.echo(f"\n👀 Watching {asset_id} (Ctrl+C to stop)\n")

    try:
        while True:
            try:
                aav = AAVFile(aav_file)
                data = aav.read()

                cpu = data.get('compute', {}).get('real_time', {}).get('cpu_percent', 0)
                memory = data.get('memory', {}).get('real_time', {}).get('usage_percent', 0)
                disk = data.get('storage', {}).get('real_time', {}).get('disk_usage_percent', 0)
                health = data.get('services', {}).get('application', {}).get('health_status', 'unknown')

                timestamp = datetime.now().strftime("%H:%M:%S")
                cpu_emoji = "⚠️ " if cpu > 70 else ""
                mem_emoji = "⚠️ " if memory > 70 else ""
                health_icon = "✅" if health == "healthy" else "❌"

                click.echo(
                    f"{timestamp} - CPU: {cpu_emoji}{cpu:5.1f}% | "
                    f"Mem: {mem_emoji}{memory:5.1f}% | "
                    f"Disk: {disk:5.1f}% | "
                    f"Health: {health_icon}"
                )

            except Exception as e:
                click.echo(f"{datetime.now().strftime('%H:%M:%S')} - ❌ Error: {e}")

            time.sleep(interval)

    except KeyboardInterrupt:
        click.echo("\n\n✅ Stopped watching")


@cli.command()
@click.option(
    "--assets-dir",
    default="./assets",
    help="Directory containing .aav files"
)
@click.option(
    "--filter",
    "filter_expr",
    help='Filter expression (e.g., "cpu > 80")'
)
def query(assets_dir: str, filter_expr: Optional[str]) -> None:
    """
    Query assets with filters.

    Examples:
        $ aura query --filter "cpu > 80" --assets-dir ./assets
        $ aura query --filter "memory > 70" --assets-dir ./assets
    """
    assets_path = Path(assets_dir)
    aav_files = list(assets_path.glob("*.aav"))

    if filter_expr:
        click.echo(f"🔍 Query: {filter_expr}\n")

        # Simple filter parsing
        results = []
        for aav_file in aav_files:
            try:
                aav = AAVFile(aav_file)
                data = aav.read()

                asset_id = data['asset']['id']
                cpu = data.get('compute', {}).get('real_time', {}).get('cpu_percent', 0)
                memory = data.get('memory', {}).get('real_time', {}).get('usage_percent', 0)

                # Simple filter evaluation
                matches = False
                if 'cpu' in filter_expr:
                    threshold = float(filter_expr.split('>')[1].strip()) if '>' in filter_expr else 0
                    matches = cpu > threshold
                elif 'memory' in filter_expr:
                    threshold = float(filter_expr.split('>')[1].strip()) if '>' in filter_expr else 0
                    matches = memory > threshold

                if matches:
                    results.append({'id': asset_id, 'cpu': cpu, 'memory': memory})

            except Exception:
                continue

        if results:
            click.echo(f"Found {len(results)} assets matching filter:\n")
            for result in results:
                if 'cpu' in filter_expr:
                    click.echo(f"   📊 {result['id']:30} CPU: {result['cpu']:.1f}%")
                else:
                    click.echo(f"   📊 {result['id']:30} Memory: {result['memory']:.1f}%")
        else:
            click.echo("No assets match the filter.")
    else:
        click.echo(f"📊 {len(aav_files)} assets available")
        click.echo("\nUse --filter to query. Examples:")
        click.echo("  --filter 'cpu > 80'")
        click.echo("  --filter 'memory > 70'")


@cli.command()
@click.option(
    "--assets-dir",
    default="./assets",
    help="Directory containing .aav files"
)
def validate(assets_dir: str) -> None:
    """Validate all .aav files for integrity."""
    click.echo("🔍 Validating .aav files...\n")

    validator = AAVValidator()
    assets_path = Path(assets_dir)
    aav_files = list(assets_path.glob("*.aav"))

    if not aav_files:
        click.echo(f"No .aav files found in {assets_dir}")
        return

    results = validator.validate_batch(aav_files)
    summary = validator.get_summary(results)

    click.echo(f"📊 Validation Results:")
    click.echo(f"━" * 60)
    click.echo(f"  Total Files: {summary['total_files']}")
    click.echo(f"  ✅ Valid:    {summary['valid']}")
    click.echo(f"  ❌ Invalid:  {summary['invalid']}")
    click.echo(f"  ⚠️  Warnings: {summary['total_warnings']}")
    click.echo(f"  ❌ Errors:   {summary['total_errors']}")

    if summary['invalid'] > 0:
        click.echo(f"\n❌ Invalid files:")
        for result in results:
            if not result.valid:
                click.echo(f"  • {result.file_path.name}")
                for error in result.errors[:2]:
                    click.echo(f"      {error}")


@cli.command()
@click.argument("asset_id")
@click.option(
    "--assets-dir",
    default="./assets",
    help="Directory containing .aav files"
)
def deploy_check(asset_id: str, assets_dir: str) -> None:
    """
    Check if it's safe to deploy to an asset.

    Example:
        $ aura deploy-check container-payment-api --assets-dir ./assets
    """
    client = AuraClient(assets_dir=assets_dir)

    try:
        result = asyncio.run(client.is_safe_to_deploy(asset_id))

        click.echo(f"\n🚀 Deployment Check: {asset_id}")
        click.echo("━" * 60)

        if result["safe"]:
            click.echo(f"✅ {result['recommendation']}\n")
            sys.exit(0)
        else:
            click.echo(f"⚠️  {result['recommendation']}\n")
            click.echo("Failed checks:")
            for check, passed in result["checks"].items():
                icon = "✅" if passed else "❌"
                check_name = check.replace('_', ' ').title()
                click.echo(f"  {icon} {check_name}")
            click.echo()
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def version() -> None:
    """Show Aura version."""
    click.echo(f"Aura v{__version__}")
    click.echo("Universal AI Asset Authority")


if __name__ == "__main__":
    cli()
