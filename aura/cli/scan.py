"""
Scanner CLI commands for asset discovery.
"""

import asyncio
import click
from pathlib import Path

from aura.scanners import (
    CloudScanner,
    DockerScanner,
    KubernetesScanner,
    PortScanner,
    ProcessScanner,
    SystemScanner,
    VMScanner,
)


@click.group()
def scan():
    """Scan and discover assets automatically."""
    pass


@scan.command()
@click.option('--assets-dir', default='./assets', help='Assets directory')
def all(assets_dir):
    """Run all scanners and discover all assets."""
    click.echo("🔍 Running all scanners...")

    async def run_all_scanners():
        total_discovered = 0

        # System scanner
        click.echo("\n📊 Scanning system...")
        scanner = SystemScanner(assets_dir=assets_dir)
        count = await scanner.discover_and_instrument()
        click.echo(f"   ✓ Discovered {count} system")
        total_discovered += count

        # Port scanner
        click.echo("\n🔌 Scanning ports...")
        scanner = PortScanner(assets_dir=assets_dir)
        count = await scanner.discover_and_instrument()
        click.echo(f"   ✓ Discovered {count} ports")
        total_discovered += count

        # Process scanner
        click.echo("\n⚙️  Scanning processes...")
        scanner = ProcessScanner(assets_dir=assets_dir, min_cpu_percent=5.0)
        count = await scanner.discover_and_instrument()
        click.echo(f"   ✓ Discovered {count} processes")
        total_discovered += count

        # Docker scanner
        click.echo("\n🐳 Scanning Docker containers...")
        scanner = DockerScanner(assets_dir=assets_dir)
        count = await scanner.discover_and_instrument()
        click.echo(f"   ✓ Discovered {count} containers")
        total_discovered += count

        # Kubernetes scanner
        click.echo("\n☸️  Scanning Kubernetes pods...")
        scanner = KubernetesScanner(assets_dir=assets_dir)
        count = await scanner.discover_and_instrument()
        click.echo(f"   ✓ Discovered {count} pods")
        total_discovered += count

        # VM scanner
        click.echo("\n💻 Scanning virtual machines...")
        scanner = VMScanner(assets_dir=assets_dir)
        count = await scanner.discover_and_instrument()
        click.echo(f"   ✓ Discovered {count} VMs")
        total_discovered += count

        # Cloud scanner
        click.echo("\n☁️  Scanning cloud instances...")
        scanner = CloudScanner(assets_dir=assets_dir)
        count = await scanner.discover_and_instrument()
        click.echo(f"   ✓ Discovered {count} cloud instances")
        total_discovered += count

        click.echo(f"\n✅ Total: Discovered {total_discovered} assets")
        click.echo(f"📁 AAV files saved to: {assets_dir}")

    asyncio.run(run_all_scanners())


@scan.command()
@click.option('--assets-dir', default='./assets', help='Assets directory')
def system(assets_dir):
    """Scan system information."""
    click.echo("📊 Scanning system...")

    async def run():
        scanner = SystemScanner(assets_dir=assets_dir)
        count = await scanner.discover_and_instrument()
        click.echo(f"✅ Discovered {count} system")

    asyncio.run(run())


@scan.command()
@click.option('--assets-dir', default='./assets', help='Assets directory')
@click.option('--include-stats/--no-stats', default=True, help='Include connection stats')
def ports(assets_dir, include_stats):
    """Scan for open ports and services."""
    click.echo("🔌 Scanning ports...")

    async def run():
        scanner = PortScanner(assets_dir=assets_dir, include_stats=include_stats)
        count = await scanner.discover_and_instrument()
        click.echo(f"✅ Discovered {count} listening ports")

        # Show top ports
        stats = scanner.get_all_port_stats()
        if stats.get('top_ports'):
            click.echo("\n📊 Top ports by connections:")
            for port_stat in stats['top_ports'][:5]:
                click.echo(f"   {port_stat['port']:5d} - {port_stat['service']:20s} ({port_stat['connections']} connections)")

    asyncio.run(run())


@scan.command()
@click.option('--assets-dir', default='./assets', help='Assets directory')
@click.option('--min-cpu', default=1.0, help='Minimum CPU percent to include')
@click.option('--min-memory', default=100.0, help='Minimum memory MB to include')
def processes(assets_dir, min_cpu, min_memory):
    """Scan for running processes."""
    click.echo("⚙️  Scanning processes...")

    async def run():
        scanner = ProcessScanner(
            assets_dir=assets_dir,
            min_cpu_percent=min_cpu,
            min_memory_mb=min_memory
        )
        count = await scanner.discover_and_instrument()
        click.echo(f"✅ Discovered {count} processes")

    asyncio.run(run())


@scan.command()
@click.option('--assets-dir', default='./assets', help='Assets directory')
def docker(assets_dir):
    """Scan for Docker containers."""
    click.echo("🐳 Scanning Docker containers...")

    async def run():
        scanner = DockerScanner(assets_dir=assets_dir)
        count = await scanner.discover_and_instrument()
        click.echo(f"✅ Discovered {count} containers")

    asyncio.run(run())


@scan.command()
@click.option('--assets-dir', default='./assets', help='Assets directory')
@click.option('--namespace', default='default', help='Kubernetes namespace')
def kubernetes(assets_dir, namespace):
    """Scan for Kubernetes pods."""
    click.echo(f"☸️  Scanning Kubernetes pods in namespace '{namespace}'...")

    async def run():
        scanner = KubernetesScanner(assets_dir=assets_dir, namespace=namespace)
        count = await scanner.discover_and_instrument()
        click.echo(f"✅ Discovered {count} pods")

    asyncio.run(run())


@scan.command()
@click.option('--assets-dir', default='./assets', help='Assets directory')
@click.option('--hypervisor', default='auto', help='Hypervisor type (vmware, virtualbox, kvm, auto)')
def vms(assets_dir, hypervisor):
    """Scan for virtual machines."""
    click.echo(f"💻 Scanning VMs ({hypervisor})...")

    async def run():
        scanner = VMScanner(assets_dir=assets_dir, hypervisor=hypervisor)
        count = await scanner.discover_and_instrument()
        click.echo(f"✅ Discovered {count} VMs")

    asyncio.run(run())


@scan.command()
@click.option('--assets-dir', default='./assets', help='Assets directory')
@click.option('--provider', default='auto', help='Cloud provider (aws, azure, gcp, auto)')
@click.option('--region', default=None, help='Cloud region')
def cloud(assets_dir, provider, region):
    """Scan for cloud instances."""
    click.echo(f"☁️  Scanning cloud instances ({provider})...")

    async def run():
        scanner = CloudScanner(assets_dir=assets_dir, cloud_provider=provider, region=region)
        count = await scanner.discover_and_instrument()
        click.echo(f"✅ Discovered {count} cloud instances")

    asyncio.run(run())
