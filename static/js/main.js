// DataTable instance
let vmTable;
let performanceChart;
let refreshInterval;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize DataTable
    vmTable = $('#vm-table').DataTable({
        pageLength: 25,
        order: [[0, 'asc']],
        columns: [
            { data: 'name' },
            { data: 'power_state' },
            { data: 'guest_os' },
            { data: 'cpu' },
            { data: 'memory_mb' },
            { data: 'ip_address' },
            {
                data: null,
                render: function(data, type, row) {
                    const powerState = row.power_state;
                    return `
                        <div class="btn-group">
                            ${powerState === 'poweredOff' ? 
                                `<button class="btn btn-sm btn-success" onclick="vmAction('${row.name}', 'power_on')">
                                    <i class="bi bi-play-fill"></i>
                                </button>` : ''}
                            ${powerState === 'poweredOn' ? 
                                `<button class="btn btn-sm btn-warning" onclick="vmAction('${row.name}', 'reset')">
                                    <i class="bi bi-arrow-clockwise"></i>
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="vmAction('${row.name}', 'power_off')">
                                    <i class="bi bi-stop-fill"></i>
                                </button>` : ''}
                            <button class="btn btn-sm btn-info" onclick="showVMDetails('${row.name}')">
                                <i class="bi bi-info-circle"></i>
                            </button>
                        </div>`;
                }
            }
        ]
    });

    // Load initial data
    refreshVMData();
    
    // Set up auto-refresh
    refreshInterval = setInterval(refreshVMData, 30000);  // Refresh every 30 seconds

    // Initialize performance chart
    initializePerformanceChart();

    // Set up event listeners
    document.getElementById('refresh-vms').addEventListener('click', refreshVMData);
    document.getElementById('metric-selector').addEventListener('change', updatePerformanceChart);

    // Set up tab change handlers
    $('a[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
        if (e.target.getAttribute('data-bs-target') === '#performance') {
            updatePerformanceChart();
        }
    });
});

function refreshVMData() {
    fetch('/api/vms')
        .then(response => response.json())
        .then(data => {
            vmTable.clear();
            vmTable.rows.add(data.vms);
            vmTable.draw();
        })
        .catch(error => {
            console.error('Error fetching VM data:', error);
            showAlert('Error refreshing VM data', 'danger');
        });
}

function vmAction(vmName, action) {
    const modal = new bootstrap.Modal(document.getElementById('vmActionModal'));
    document.getElementById('vm-name').textContent = vmName;
    document.getElementById('action-text').textContent = action.replace('_', ' ');
    
    document.getElementById('confirm-action').onclick = function() {
        fetch('/api/vm/action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                vm_name: vmName,
                action: action
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                modal.hide();
                showAlert(`Successfully performed ${action} on VM ${vmName}`, 'success');
                setTimeout(refreshVMData, 2000);  // Refresh after 2 seconds
            } else {
                throw new Error(data.error || 'Action failed');
            }
        })
        .catch(error => {
            console.error('Error performing VM action:', error);
            showAlert(`Error performing ${action} on VM ${vmName}`, 'danger');
        });
    };
    
    modal.show();
}

function showVMDetails(vmName) {
    Promise.all([
        fetch(`/api/vm/${vmName}/snapshots`).then(r => r.json()),
        fetch(`/api/vm/${vmName}/networks`).then(r => r.json())
    ])
    .then(([snapshotData, networkData]) => {
        const modal = new bootstrap.Modal(document.getElementById('vmDetailsModal'));
        const detailsBody = document.getElementById('vm-details-body');
        
        let html = '<h5>Snapshots</h5>';
        if (snapshotData.snapshots && snapshotData.snapshots.length > 0) {
            html += '<ul>';
            snapshotData.snapshots.forEach(snapshot => {
                html += `<li>${snapshot.name} (${snapshot.creation_time})</li>`;
            });
            html += '</ul>';
        } else {
            html += '<p>No snapshots available</p>';
        }

        html += '<h5 class="mt-3">Networks</h5>';
        if (networkData.networks && networkData.networks.length > 0) {
            html += '<ul>';
            networkData.networks.forEach(network => {
                html += `<li>${network.name} (${network.network_type})</li>`;
            });
            html += '</ul>';
        } else {
            html += '<p>No network information available</p>';
        }

        detailsBody.innerHTML = html;
        modal.show();
    })
    .catch(error => {
        console.error('Error fetching VM details:', error);
        showAlert('Error fetching VM details', 'danger');
    });
}

function initializePerformanceChart() {
    const chartDiv = document.getElementById('performance-chart');
    performanceChart = Plotly.newPlot(chartDiv, [{
        x: [],
        y: [],
        type: 'scatter'
    }], {
        title: 'Performance Metrics',
        xaxis: { title: 'Time' },
        yaxis: { title: 'Usage' }
    });
}

function updatePerformanceChart() {
    const metric = document.getElementById('metric-selector').value;
    const selectedVM = vmTable.rows({ selected: true }).data()[0];
    
    if (!selectedVM) {
        showAlert('Please select a VM to view performance metrics', 'warning');
        return;
    }

    fetch(`/api/vm/performance?vm_name=${selectedVM.name}&metric_type=${metric}`)
        .then(response => response.json())
        .then(data => {
            const update = {
                x: [data.timestamps],
                y: [data.values]
            };

            const layout = {
                title: `${metric.toUpperCase()} Usage Over Time`,
                xaxis: { title: 'Time' },
                yaxis: { title: metric === 'cpu' ? 'Percentage' : 'Usage' }
            };

            Plotly.update('performance-chart', update, layout);
        })
        .catch(error => {
            console.error('Error updating performance chart:', error);
            showAlert('Error updating performance metrics', 'danger');
        });
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});
