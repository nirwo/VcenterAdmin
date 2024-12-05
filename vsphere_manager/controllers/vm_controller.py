from flask import jsonify, request
from typing import Dict, Any, Tuple
from ..utils.vsphere_client import VSphereClient
import logging

logger = logging.getLogger(__name__)

class VMController:
    def __init__(self):
        self.vsphere_client = VSphereClient()

    def get_all_vms(self) -> Tuple[Dict[str, Any], int]:
        """Get all VMs with their properties"""
        try:
            vms = self.vsphere_client.get_all_vms()
            return {'vms': vms}, 200
        except Exception as e:
            logger.error(f"Error getting VMs: {str(e)}")
            return {'error': 'Failed to retrieve VMs'}, 500

    def perform_vm_action(self) -> Tuple[Dict[str, Any], int]:
        """Perform action on VM"""
        try:
            data = request.get_json()
            vm_name = data.get('vm_name')
            action = data.get('action')

            if not vm_name or not action:
                return {'error': 'Missing required parameters'}, 400

            success = self.vsphere_client.perform_vm_action(vm_name, action)
            if success:
                return {'status': 'success', 'message': f'Successfully performed {action} on VM {vm_name}'}, 200
            else:
                return {'error': f'Failed to perform {action} on VM {vm_name}'}, 500

        except Exception as e:
            logger.error(f"Error performing VM action: {str(e)}")
            return {'error': 'Failed to perform VM action'}, 500

    def get_vm_performance(self) -> Tuple[Dict[str, Any], int]:
        """Get VM performance metrics"""
        try:
            vm_name = request.args.get('vm_name')
            metric_type = request.args.get('metric_type', 'cpu')

            if not vm_name:
                return {'error': 'Missing VM name'}, 400

            vm = self.vsphere_client.get_vm_by_name(vm_name)
            if not vm:
                return {'error': 'VM not found'}, 404

            metrics = self.vsphere_client.get_performance_metrics(vm, metric_type)
            return metrics, 200

        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return {'error': 'Failed to get performance metrics'}, 500

    def get_vm_snapshots(self, vm_name: str) -> Tuple[Dict[str, Any], int]:
        """Get VM snapshots"""
        try:
            snapshots = self.vsphere_client.get_vm_snapshots(vm_name)
            return {'snapshots': snapshots}, 200
        except Exception as e:
            logger.error(f"Error getting snapshots: {str(e)}")
            return {'error': 'Failed to get snapshots'}, 500

    def create_snapshot(self) -> Tuple[Dict[str, Any], int]:
        """Create VM snapshot"""
        try:
            data = request.get_json()
            vm_name = data.get('vm_name')
            snapshot_name = data.get('snapshot_name')
            description = data.get('description', '')

            if not vm_name or not snapshot_name:
                return {'error': 'Missing required parameters'}, 400

            success = self.vsphere_client.create_snapshot(vm_name, snapshot_name, description)
            if success:
                return {'status': 'success', 'message': f'Successfully created snapshot {snapshot_name}'}, 200
            else:
                return {'error': 'Failed to create snapshot'}, 500

        except Exception as e:
            logger.error(f"Error creating snapshot: {str(e)}")
            return {'error': 'Failed to create snapshot'}, 500

    def get_vm_networks(self, vm_name: str) -> Tuple[Dict[str, Any], int]:
        """Get VM network information"""
        try:
            networks = self.vsphere_client.get_vm_networks(vm_name)
            return {'networks': networks}, 200
        except Exception as e:
            logger.error(f"Error getting network information: {str(e)}")
            return {'error': 'Failed to get network information'}, 500
