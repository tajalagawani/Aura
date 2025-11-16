"""
Cloud Scanner - Discovers cloud instances.

Automatically finds cloud instances from AWS, Azure, GCP and creates AAV files.
"""

import logging
from typing import Dict, List, Any

from aura.scanners.base_scanner import BaseScanner

logger = logging.getLogger(__name__)


class CloudScanner(BaseScanner):
    """
    Scanner for cloud instances.

    Discovers instances from AWS EC2, Azure VMs, GCP Compute Engine.

    Example:
        >>> scanner = CloudScanner(
        ...     assets_dir="./assets",
        ...     cloud_provider="aws"
        ... )
        >>> count = await scanner.discover_and_instrument()
    """

    def __init__(
        self,
        assets_dir: str = "./assets",
        cloud_provider: str = "auto",
        region: str = None
    ):
        """
        Initialize Cloud scanner.

        Args:
            assets_dir: Directory for AAV files
            cloud_provider: Cloud provider (aws, azure, gcp, auto)
            region: Cloud region (optional)
        """
        super().__init__(assets_dir)
        self.cloud_provider = cloud_provider
        self.region = region

    async def scan(self) -> List[Dict[str, Any]]:
        """
        Scan for cloud instances.

        Returns:
            List of discovered instances
        """
        instances = []

        if self.cloud_provider in ("aws", "auto"):
            instances.extend(await self._scan_aws())

        if self.cloud_provider in ("azure", "auto"):
            instances.extend(await self._scan_azure())

        if self.cloud_provider in ("gcp", "auto"):
            instances.extend(await self._scan_gcp())

        logger.info(f"Found {len(instances)} cloud instances")
        return instances

    async def _scan_aws(self) -> List[Dict[str, Any]]:
        """Scan for AWS EC2 instances."""
        try:
            import boto3

            ec2 = boto3.client('ec2', region_name=self.region)
            instances = []

            # Get all instances
            response = ec2.describe_instances()

            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    # Get instance name from tags
                    name = instance.get('InstanceId')
                    for tag in instance.get('Tags', []):
                        if tag.get('Key') == 'Name':
                            name = tag.get('Value', name)
                            break

                    asset = {
                        "id": f"aws-{instance['InstanceId']}",
                        "name": name,
                        "type": "cloud_instance",
                        "metadata": {
                            "provider": "aws",
                            "instance_id": instance['InstanceId'],
                            "instance_type": instance.get('InstanceType', 'unknown'),
                            "state": instance.get('State', {}).get('Name', 'unknown'),
                            "availability_zone": instance.get('Placement', {}).get('AvailabilityZone', ''),
                            "private_ip": instance.get('PrivateIpAddress', ''),
                            "public_ip": instance.get('PublicIpAddress', ''),
                            "launch_time": instance.get('LaunchTime', '').isoformat() if instance.get('LaunchTime') else '',
                            "vpc_id": instance.get('VpcId', ''),
                            "subnet_id": instance.get('SubnetId', ''),
                        }
                    }
                    instances.append(asset)

            logger.info(f"Found {len(instances)} AWS EC2 instances")
            return instances

        except ImportError:
            logger.debug("AWS SDK not installed. Install with: pip install boto3")
            return []
        except Exception as e:
            logger.error(f"AWS scan failed: {e}")
            return []

    async def _scan_azure(self) -> List[Dict[str, Any]]:
        """Scan for Azure VMs."""
        try:
            from azure.identity import DefaultAzureCredential
            from azure.mgmt.compute import ComputeManagementClient

            # Get subscription ID from environment
            import os
            subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
            if not subscription_id:
                logger.warning("AZURE_SUBSCRIPTION_ID not set")
                return []

            credential = DefaultAzureCredential()
            compute_client = ComputeManagementClient(credential, subscription_id)

            instances = []

            # List all VMs
            for vm in compute_client.virtual_machines.list_all():
                # Get instance view for power state
                instance_view = compute_client.virtual_machines.instance_view(
                    vm.id.split('/')[4],  # resource group
                    vm.name
                )

                power_state = "unknown"
                for status in instance_view.statuses:
                    if status.code.startswith('PowerState'):
                        power_state = status.code.split('/')[-1]
                        break

                asset = {
                    "id": f"azure-{vm.vm_id}",
                    "name": vm.name,
                    "type": "cloud_instance",
                    "metadata": {
                        "provider": "azure",
                        "vm_id": vm.vm_id,
                        "vm_size": vm.hardware_profile.vm_size,
                        "state": power_state,
                        "location": vm.location,
                        "resource_group": vm.id.split('/')[4],
                        "os_type": vm.storage_profile.os_disk.os_type,
                    }
                }
                instances.append(asset)

            logger.info(f"Found {len(instances)} Azure VMs")
            return instances

        except ImportError:
            logger.debug("Azure SDK not installed. Install with: pip install azure-identity azure-mgmt-compute")
            return []
        except Exception as e:
            logger.error(f"Azure scan failed: {e}")
            return []

    async def _scan_gcp(self) -> List[Dict[str, Any]]:
        """Scan for GCP Compute Engine instances."""
        try:
            from google.cloud import compute_v1

            # Get project ID from environment
            import os
            project_id = os.environ.get('GCP_PROJECT_ID')
            if not project_id:
                logger.warning("GCP_PROJECT_ID not set")
                return []

            instances_client = compute_v1.InstancesClient()
            instances = []

            # List all zones
            zones_client = compute_v1.ZonesClient()
            zones = zones_client.list(project=project_id)

            for zone in zones:
                try:
                    # List instances in zone
                    zone_instances = instances_client.list(
                        project=project_id,
                        zone=zone.name
                    )

                    for instance in zone_instances:
                        # Get primary network interface
                        network_interface = instance.network_interfaces[0] if instance.network_interfaces else None
                        internal_ip = network_interface.network_i_p if network_interface else ''
                        external_ip = ''
                        if network_interface and network_interface.access_configs:
                            external_ip = network_interface.access_configs[0].nat_i_p

                        asset = {
                            "id": f"gcp-{instance.id}",
                            "name": instance.name,
                            "type": "cloud_instance",
                            "metadata": {
                                "provider": "gcp",
                                "instance_id": str(instance.id),
                                "machine_type": instance.machine_type.split('/')[-1],
                                "status": instance.status,
                                "zone": zone.name,
                                "internal_ip": internal_ip,
                                "external_ip": external_ip,
                                "creation_timestamp": instance.creation_timestamp,
                            }
                        }
                        instances.append(asset)

                except Exception as e:
                    logger.debug(f"Error scanning GCP zone {zone.name}: {e}")
                    continue

            logger.info(f"Found {len(instances)} GCP instances")
            return instances

        except ImportError:
            logger.debug("GCP SDK not installed. Install with: pip install google-cloud-compute")
            return []
        except Exception as e:
            logger.error(f"GCP scan failed: {e}")
            return []

    def get_instance_metrics(self, instance_id: str, provider: str) -> Dict[str, Any]:
        """
        Get cloud instance metrics.

        Args:
            instance_id: Instance ID
            provider: Cloud provider

        Returns:
            Instance metrics
        """
        if provider == "aws":
            return self._get_aws_metrics(instance_id)
        elif provider == "azure":
            return self._get_azure_metrics(instance_id)
        elif provider == "gcp":
            return self._get_gcp_metrics(instance_id)
        else:
            return {}

    def _get_aws_metrics(self, instance_id: str) -> Dict[str, Any]:
        """Get AWS instance metrics from CloudWatch."""
        try:
            import boto3
            from datetime import datetime, timedelta

            cloudwatch = boto3.client('cloudwatch', region_name=self.region)

            # Get CPU utilization for last 5 minutes
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(minutes=5)

            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Average']
            )

            cpu_avg = 0
            if response.get('Datapoints'):
                cpu_avg = response['Datapoints'][0].get('Average', 0)

            return {
                "cpu_utilization": round(cpu_avg, 2),
            }

        except Exception as e:
            logger.error(f"Failed to get AWS metrics for {instance_id}: {e}")
            return {}

    def _get_azure_metrics(self, vm_id: str) -> Dict[str, Any]:
        """Get Azure VM metrics."""
        try:
            # Azure metrics require monitor client
            logger.debug("Azure metrics not implemented yet")
            return {}

        except Exception as e:
            logger.error(f"Failed to get Azure metrics for {vm_id}: {e}")
            return {}

    def _get_gcp_metrics(self, instance_id: str) -> Dict[str, Any]:
        """Get GCP instance metrics."""
        try:
            # GCP metrics require monitoring client
            logger.debug("GCP metrics not implemented yet")
            return {}

        except Exception as e:
            logger.error(f"Failed to get GCP metrics for {instance_id}: {e}")
            return {}
