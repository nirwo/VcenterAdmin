from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import ssl
import atexit
from datetime import datetime, timedelta
import threading
from typing import Dict, List, Optional, Any
import logging
import sys
import platform

# Configure logging with Windows-compatible file handling
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vsphere_manager.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VSphereClient:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(VSphereClient, cls).__new__(cls)
                cls._instance.service_instance = None
                cls._instance.connected = False
            return cls._instance

    def connect(self, host: str, user: str, password: str, port: int = 443) -> bool:
        """Connect to vSphere server"""
        try:
            # Create SSL context
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.verify_mode = ssl.CERT_NONE
            
            # Handle IPv6 addresses for Windows compatibility
            if ':' in host and not host.startswith('['):
                host = f'[{host}]'

            self.service_instance = SmartConnect(
                host=host,
                user=user,
                pwd=password,
                port=port,
                sslContext=context
            )

            if self.service_instance:
                atexit.register(Disconnect, self.service_instance)
                self.connected = True
                logger.info(f"Successfully connected to vSphere server: {host}")
                return True

        except Exception as e:
            logger.error(f"Failed to connect to vSphere: {str(e)}")
            self.connected = False
            return False

    def get_all_vms(self) -> List[Dict[str, Any]]:
        """Get all virtual machines with their properties"""
        if not self.connected:
            return []

        try:
            content = self.service_instance.RetrieveContent()
            container = content.rootFolder
            view_type = [vim.VirtualMachine]
            recursive = True
            container_view = content.viewManager.CreateContainerView(container, view_type, recursive)

            vms = []
            for vm in container_view.view:
                try:
                    vm_info = {
                        'name': vm.name,
                        'power_state': vm.runtime.powerState,
                        'guest_os': vm.config.guestFullName if vm.config else 'N/A',
                        'cpu': vm.config.hardware.numCPU if vm.config else 0,
                        'memory_mb': vm.config.hardware.memoryMB if vm.config else 0,
                        'ip_address': vm.guest.ipAddress if vm.guest else 'N/A',
                        'moid': vm._moId,
                        'guest_state': vm.guest.guestState if vm.guest else 'N/A',
                        'boot_time': vm.runtime.bootTime.isoformat() if vm.runtime.bootTime else None,
                        'host': vm.runtime.host.name if vm.runtime.host else 'N/A'
                    }
                    vms.append(vm_info)
                except Exception as vm_error:
                    logger.error(f"Error processing VM {vm.name}: {str(vm_error)}")
                    continue

            container_view.Destroy()
            return vms

        except Exception as e:
            logger.error(f"Error getting VMs: {str(e)}")
            return []

    def get_vm_by_name(self, name: str) -> Optional[vim.VirtualMachine]:
        """Get VM object by name"""
        if not self.connected:
            return None

        try:
            content = self.service_instance.RetrieveContent()
            container = content.rootFolder
            view_type = [vim.VirtualMachine]
            recursive = True
            container_view = content.viewManager.CreateContainerView(container, view_type, recursive)

            for vm in container_view.view:
                if vm.name == name:
                    container_view.Destroy()
                    return vm

            container_view.Destroy()
            return None

        except Exception as e:
            logger.error(f"Error getting VM by name: {str(e)}")
            return None

    def get_performance_metrics(self, vm: vim.VirtualMachine, metric_type: str) -> Dict[str, List[float]]:
        """Get performance metrics for a VM"""
        if not self.connected:
            return {}

        try:
            content = self.service_instance.RetrieveContent()
            perfManager = content.perfManager

            # Define metric mappings
            metric_mappings = {
                'cpu': ['cpu.usage.average'],
                'memory': ['mem.usage.average'],
                'disk': ['disk.usage.average', 'disk.read.average', 'disk.write.average'],
                'network': ['net.received.average', 'net.transmitted.average']
            }

            # Get metric IDs
            metric_ids = []
            for metric in perfManager.perfCounter:
                if any(counter_name in metric.nameInfo.key for counter_name in metric_mappings.get(metric_type, [])):
                    metric_ids.append(metric.key)

            # Build query spec
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)

            query = vim.PerformanceManager.QuerySpec(
                maxSample=60,
                entity=vm,
                metricId=metric_ids,
                startTime=start_time,
                endTime=end_time,
                intervalId=20
            )

            # Get the stats
            stats = perfManager.QueryStats(querySpec=[query])
            if not stats:
                return {}

            # Process results
            result = {
                'timestamps': [],
                'values': []
            }

            for val in stats[0].value:
                if val.id.counterId in metric_ids:
                    result['values'].extend([float(x) for x in val.value])
                    result['timestamps'].extend(
                        [(start_time + timedelta(seconds=20 * i)).isoformat() 
                         for i in range(len(val.value))]
                    )

            return result

        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return {}

    def perform_vm_action(self, vm_name: str, action: str) -> bool:
        """Perform action on VM"""
        if not self.connected:
            return False

        try:
            vm = self.get_vm_by_name(vm_name)
            if not vm:
                logger.error(f"VM not found: {vm_name}")
                return False

            action_map = {
                "power_on": (lambda v: v.PowerOnVM_Task(), "poweredOff"),
                "power_off": (lambda v: v.PowerOffVM_Task(), "poweredOn"),
                "reset": (lambda v: v.ResetVM_Task(), "poweredOn"),
                "suspend": (lambda v: v.SuspendVM_Task(), "poweredOn"),
                "shutdown": (lambda v: v.ShutdownGuest(), "poweredOn"),
                "reboot": (lambda v: v.RebootGuest(), "poweredOn")
            }

            if action in action_map:
                action_func, required_state = action_map[action]
                if vm.runtime.powerState == required_state or action in ["reset", "reboot"]:
                    action_func(vm)
                    logger.info(f"Successfully initiated {action} on VM {vm_name}")
                    return True
                else:
                    logger.error(f"Invalid state for {action}: {vm.runtime.powerState}")
                    return False
            else:
                logger.error(f"Invalid action: {action}")
                return False

        except Exception as e:
            logger.error(f"Error performing VM action: {str(e)}")
            return False

    def get_vm_snapshots(self, vm_name: str) -> List[Dict[str, Any]]:
        """Get VM snapshots"""
        if not self.connected:
            return []

        try:
            vm = self.get_vm_by_name(vm_name)
            if not vm:
                return []

            snapshots = []
            if vm.snapshot:
                for snapshot in vm.snapshot.rootSnapshotList:
                    snapshots.append({
                        'name': snapshot.name,
                        'description': snapshot.description,
                        'creation_time': snapshot.createTime.isoformat(),
                        'state': snapshot.state
                    })

            return snapshots

        except Exception as e:
            logger.error(f"Error getting snapshots: {str(e)}")
            return []

    def create_snapshot(self, vm_name: str, snapshot_name: str, description: str = "") -> bool:
        """Create VM snapshot"""
        if not self.connected:
            return False

        try:
            vm = self.get_vm_by_name(vm_name)
            if not vm:
                return False

            task = vm.CreateSnapshot_Task(
                name=snapshot_name,
                description=description,
                memory=True,
                quiesce=False
            )
            return True

        except Exception as e:
            logger.error(f"Error creating snapshot: {str(e)}")
            return False

    def get_vm_networks(self, vm_name: str) -> List[Dict[str, Any]]:
        """Get VM network information"""
        if not self.connected:
            return []

        try:
            vm = self.get_vm_by_name(vm_name)
            if not vm:
                return []

            networks = []
            for network in vm.network:
                network_info = {
                    'name': network.name,
                    'accessible': network.summary.accessible,
                    'network_type': type(network).__name__
                }
                networks.append(network_info)

            return networks

        except Exception as e:
            logger.error(f"Error getting network information: {str(e)}")
            return []

    def get_host_information(self) -> List[Dict[str, Any]]:
        """Get information about all hosts"""
        if not self.connected:
            return []

        try:
            content = self.service_instance.RetrieveContent()
            container = content.rootFolder
            view_type = [vim.HostSystem]
            recursive = True
            container_view = content.viewManager.CreateContainerView(container, view_type, recursive)

            hosts = []
            for host in container_view.view:
                try:
                    host_info = {
                        'name': host.name,
                        'power_state': host.runtime.powerState,
                        'connection_state': host.runtime.connectionState,
                        'maintenance_mode': host.runtime.inMaintenanceMode,
                        'cpu_cores': host.hardware.cpuInfo.numCpuCores if host.hardware else 0,
                        'memory_size_mb': host.hardware.memorySize / (1024*1024) if host.hardware else 0,
                        'cpu_usage': host.summary.quickStats.overallCpuUsage if host.summary.quickStats else 0,
                        'memory_usage': host.summary.quickStats.overallMemoryUsage if host.summary.quickStats else 0
                    }
                    hosts.append(host_info)
                except Exception as host_error:
                    logger.error(f"Error processing host {host.name}: {str(host_error)}")
                    continue

            container_view.Destroy()
            return hosts

        except Exception as e:
            logger.error(f"Error getting host information: {str(e)}")
            return []
