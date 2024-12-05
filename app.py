from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from vsphere_manager.utils.vsphere_client import VSphereClient
from vsphere_manager.models.user import User
from vsphere_manager.controllers.vm_controller import VMController
from vsphere_manager.controllers.host_controller import HostController
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-this')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize controllers
vm_controller = VMController()
host_controller = HostController()

@login_manager.user_loader
def load_user(user_id):
    if 'vsphere_host' in session:
        return User(user_id, session['vsphere_host'])
    return None

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
        
        vsphere_client = VSphereClient()
        if vsphere_client.connect(host, username, password):
            user = User(username, host)
            login_user(user)
            session['vsphere_host'] = host
            flash('Successfully connected to vSphere')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials or connection failed')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('vsphere_host', None)
    logout_user()
    return redirect(url_for('login'))

# VM Routes
@app.route('/api/vms')
@login_required
def get_vms():
    response, status_code = vm_controller.get_all_vms()
    return jsonify(response), status_code

@app.route('/api/vm/action', methods=['POST'])
@login_required
def vm_action():
    response, status_code = vm_controller.perform_vm_action()
    return jsonify(response), status_code

@app.route('/api/vm/performance')
@login_required
def vm_performance():
    response, status_code = vm_controller.get_vm_performance()
    return jsonify(response), status_code

@app.route('/api/vm/<vm_name>/snapshots')
@login_required
def vm_snapshots(vm_name):
    response, status_code = vm_controller.get_vm_snapshots(vm_name)
    return jsonify(response), status_code

@app.route('/api/vm/snapshot', methods=['POST'])
@login_required
def create_snapshot():
    response, status_code = vm_controller.create_snapshot()
    return jsonify(response), status_code

@app.route('/api/vm/<vm_name>/networks')
@login_required
def vm_networks(vm_name):
    response, status_code = vm_controller.get_vm_networks(vm_name)
    return jsonify(response), status_code

# Host Routes
@app.route('/api/hosts')
@login_required
def get_hosts():
    response, status_code = host_controller.get_all_hosts()
    return jsonify(response), status_code

@app.route('/api/host/<host_name>/performance')
@login_required
def host_performance(host_name):
    response, status_code = host_controller.get_host_performance(host_name)
    return jsonify(response), status_code

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
