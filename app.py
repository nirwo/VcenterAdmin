from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import atexit
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-this')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Global variable to store vCenter connection
si = None

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def connect_vsphere(host, user, password, port=443):
    global si
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_NONE
    
    try:
        si = SmartConnect(host=host,
                         user=user,
                         pwd=password,
                         port=port,
                         sslContext=context)
        atexit.register(Disconnect, si)
        return True
    except Exception as e:
        print(f"Failed to connect to vSphere: {str(e)}")
        return False

def get_all_vms():
    if not si:
        return []
    
    content = si.RetrieveContent()
    container = content.rootFolder
    view_type = [vim.VirtualMachine]
    recursive = True
    container_view = content.viewManager.CreateContainerView(container, view_type, recursive)
    
    vms = []
    for vm in container_view.view:
        vm_info = {
            'name': vm.name,
            'power_state': vm.runtime.powerState,
            'guest_os': vm.config.guestFullName if vm.config else 'N/A',
            'cpu': vm.config.hardware.numCPU if vm.config else 0,
            'memory_mb': vm.config.hardware.memoryMB if vm.config else 0,
            'ip_address': vm.guest.ipAddress if vm.guest else 'N/A'
        }
        vms.append(vm_info)
    
    container_view.Destroy()
    return vms

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        host = request.form.get('host')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if connect_vsphere(host, username, password):
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials or connection failed')
    
    return render_template('login.html')

@app.route('/api/vms')
@login_required
def get_vms():
    vms = get_all_vms()
    return jsonify(vms)

@app.route('/api/vm/action', methods=['POST'])
@login_required
def vm_action():
    data = request.json
    vm_name = data.get('vm_name')
    action = data.get('action')
    
    # Implementation of VM actions will go here
    return jsonify({'status': 'success'})

@app.route('/api/performance')
@login_required
def get_performance_metrics():
    # Implementation of performance metrics retrieval will go here
    return jsonify({})

if __name__ == '__main__':
    app.run(debug=True)
