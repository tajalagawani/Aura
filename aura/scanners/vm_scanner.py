"""
VM Scanner - Discovers virtual machines.

Automatically finds VMs from various hypervisors and creates AAV files.
"""

import logging
from typing import Dict, List, Any

from aura.scanners.base_scanner import BaseScanner

logger = logging.getLogger(__name__)


class VMScanner(BaseScanner):
    """
    Scanner for virtual machines.

    Discovers VMs from VMware, VirtualBox, KVM, and other hypervisors.

    Example:
        >>> scanner = VMScanner(
        ...     assets_dir="./assets",
        ...     hypervisor="vmware"
        ... )
        >>> count = await scanner.discover_and_instrument()
    """

    def __init__(
        self,
        assets_dir: str = "./assets",
        hypervisor: str = "auto"
    ):
        """
        Initialize VM scanner.

        Args:
            assets_dir: Directory for AAV files
            hypervisor: Hypervisor type (vmware, virtualbox, kvm, auto)
        """
        super().__init__(assets_dir)
        self.hypervisor = hypervisor

    async def scan(self) -> List[Dict[str, Any]]:
        """
        Scan for virtual machines.

        Returns:
            List of discovered VMs
        """
        vms = []

        if self.hypervisor in ("vmware", "auto"):
            vms.extend(await self._scan_vmware())

        if self.hypervisor in ("virtualbox", "auto"):
            vms.extend(await self._scan_virtualbox())

        if self.hypervisor in ("kvm", "auto"):
            vms.extend(await self._scan_kvm())

        logger.info(f"Found {len(vms)} virtual machines")
        return vms

    async def _scan_vmware(self) -> List[Dict[str, Any]]:
        """Scan for VMware VMs."""
        try:
            from pyVmomi import vim
            from pyVim.connect import SmartConnect, Disconnect
            import ssl

            # This requires vCenter/ESXi credentials
            # For production, these should come from config
            logger.info("VMware scanning requires vCenter/ESXi credentials")
            return []

        except ImportError:
            logger.debug("VMware library not installed. Install with: pip install pyvmomi")
            return []
        except Exception as e:
            logger.error(f"VMware scan failed: {e}")
            return []

    async def _scan_virtualbox(self) -> List[Dict[str, Any]]:
        """Scan for VirtualBox VMs."""
        try:
            import virtualbox

            vbox = virtualbox.VirtualBox()
            vms = []

            for vm in vbox.machines:
                asset = {
                    "id": f"vm-{vm.id}",
                    "name": vm.name,
                    "type": "vm",
                    "metadata": {
                        "hypervisor": "virtualbox",
                        "vm_id": vm.id,
                        "state": str(vm.state),
                        "os_type": vm.os_type_id,
                        "memory_mb": vm.memory_size,
                        "cpu_count": vm.cpu_count,
                        "description": vm.description or "",
                    }
                }
                vms.append(asset)

            logger.info(f"Found {len(vms)} VirtualBox VMs")
            return vms

        except ImportError:
            logger.debug("VirtualBox library not installed. Install with: pip install pyvirtualbox")
            return []
        except Exception as e:
            logger.error(f"VirtualBox scan failed: {e}")
            return []

    async def _scan_kvm(self) -> List[Dict[str, Any]]:
        """Scan for KVM VMs."""
        try:
            import libvirt

            # Connect to local KVM
            conn = libvirt.open('qemu:///system')
            if conn is None:
                logger.warning("Failed to connect to KVM")
                return []

            vms = []

            # Get all domains (VMs)
            for domain_id in conn.listDomainsID():
                try:
                    domain = conn.lookupByID(domain_id)
                    info = domain.info()

                    asset = {
                        "id": f"vm-{domain.UUIDString()}",
                        "name": domain.name(),
                        "type": "vm",
                        "metadata": {
                            "hypervisor": "kvm",
                            "uuid": domain.UUIDString(),
                            "state": self._kvm_state_to_string(info[0]),
                            "max_memory_kb": info[1],
                            "memory_kb": info[2],
                            "cpu_count": info[3],
                            "cpu_time": info[4],
                        }
                    }
                    vms.append(asset)

                except Exception as e:
                    logger.debug(f"Error processing KVM domain: {e}")
                    continue

            # Also get inactive domains
            for name in conn.listDefinedDomains():
                try:
                    domain = conn.lookupByName(name)

                    asset = {
                        "id": f"vm-{domain.UUIDString()}",
                        "name": domain.name(),
                        "type": "vm",
                        "metadata": {
                            "hypervisor": "kvm",
                            "uuid": domain.UUIDString(),
                            "state": "shutoff",
                        }
                    }
                    vms.append(asset)

                except Exception as e:
                    logger.debug(f"Error processing inactive KVM domain: {e}")
                    continue

            conn.close()

            logger.info(f"Found {len(vms)} KVM VMs")
            return vms

        except ImportError:
            logger.debug("KVM library not installed. Install with: pip install libvirt-python")
            return []
        except Exception as e:
            logger.error(f"KVM scan failed: {e}")
            return []

    def _kvm_state_to_string(self, state: int) -> str:
        """Convert KVM state code to string."""
        states = {
            0: "nostate",
            1: "running",
            2: "blocked",
            3: "paused",
            4: "shutdown",
            5: "shutoff",
            6: "crashed",
            7: "suspended"
        }
        return states.get(state, "unknown")

    def get_vm_metrics(self, vm_id: str, hypervisor: str) -> Dict[str, Any]:
        """
        Get VM metrics.

        Args:
            vm_id: VM identifier
            hypervisor: Hypervisor type

        Returns:
            VM metrics
        """
        if hypervisor == "kvm":
            return self._get_kvm_metrics(vm_id)
        elif hypervisor == "virtualbox":
            return self._get_virtualbox_metrics(vm_id)
        else:
            return {}

    def _get_kvm_metrics(self, vm_id: str) -> Dict[str, Any]:
        """Get KVM VM metrics."""
        try:
            import libvirt

            conn = libvirt.open('qemu:///system')
            if conn is None:
                return {}

            domain = conn.lookupByUUIDString(vm_id)
            info = domain.info()

            metrics = {
                "state": self._kvm_state_to_string(info[0]),
                "max_memory_kb": info[1],
                "memory_kb": info[2],
                "cpu_count": info[3],
                "cpu_time_ns": info[4],
            }

            conn.close()
            return metrics

        except Exception as e:
            logger.error(f"Failed to get KVM metrics for {vm_id}: {e}")
            return {}

    def _get_virtualbox_metrics(self, vm_id: str) -> Dict[str, Any]:
        """Get VirtualBox VM metrics."""
        try:
            import virtualbox

            vbox = virtualbox.VirtualBox()
            vm = vbox.find_machine(vm_id)

            return {
                "state": str(vm.state),
                "memory_mb": vm.memory_size,
                "cpu_count": vm.cpu_count,
            }

        except Exception as e:
            logger.error(f"Failed to get VirtualBox metrics for {vm_id}: {e}")
            return {}
