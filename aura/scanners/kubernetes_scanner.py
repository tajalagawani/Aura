"""
Kubernetes Scanner - Discovers Kubernetes pods.

Automatically finds K8s pods and creates AAV files.
"""

import logging
from typing import Dict, List, Any

from aura.scanners.base_scanner import BaseScanner

logger = logging.getLogger(__name__)


class KubernetesScanner(BaseScanner):
    """
    Scanner for Kubernetes pods.

    Discovers running Kubernetes pods and creates monitoring files.

    Example:
        >>> scanner = KubernetesScanner(
        ...     assets_dir="./assets",
        ...     namespace="default"
        ... )
        >>> count = await scanner.discover_and_instrument()
    """

    def __init__(self, assets_dir: str = "./assets", namespace: str = "default"):
        """
        Initialize Kubernetes scanner.

        Args:
            assets_dir: Directory for AAV files
            namespace: Kubernetes namespace to scan
        """
        super().__init__(assets_dir)
        self.namespace = namespace

    async def scan(self) -> List[Dict[str, Any]]:
        """
        Scan for Kubernetes pods.

        Returns:
            List of discovered pods
        """
        try:
            from kubernetes import client, config

            # Load kubeconfig
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()

            v1 = client.CoreV1Api()

            # List pods
            pods_list = v1.list_namespaced_pod(self.namespace)

            pods = []
            for pod in pods_list.items:
                asset = {
                    "id": f"pod-{pod.metadata.name}",
                    "name": pod.metadata.name,
                    "type": "pod",
                    "metadata": {
                        "namespace": pod.metadata.namespace,
                        "labels": pod.metadata.labels or {},
                        "phase": pod.status.phase,
                        "node": pod.spec.node_name,
                        "ip": pod.status.pod_ip,
                    }
                }
                pods.append(asset)

            logger.info(f"Found {len(pods)} Kubernetes pods in namespace {self.namespace}")
            return pods

        except ImportError:
            logger.warning("Kubernetes library not installed. Install with: pip install kubernetes")
            return []
        except Exception as e:
            logger.error(f"Kubernetes scan failed: {e}")
            return []

    def get_pod_metrics(self, pod_name: str) -> Dict[str, Any]:
        """
        Get pod metrics from Kubernetes metrics API.

        Args:
            pod_name: Pod name

        Returns:
            Pod metrics
        """
        try:
            from kubernetes import client, config

            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()

            # Get metrics from metrics server
            api = client.CustomObjectsApi()
            metrics = api.get_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=self.namespace,
                plural="pods",
                name=pod_name
            )

            return {
                "cpu": metrics.get('containers', [{}])[0].get('usage', {}).get('cpu', '0'),
                "memory": metrics.get('containers', [{}])[0].get('usage', {}).get('memory', '0'),
            }

        except Exception as e:
            logger.error(f"Failed to get metrics for pod {pod_name}: {e}")
            return {}
