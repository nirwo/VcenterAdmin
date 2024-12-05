<<<<<<< HEAD
# VcenterAdmin
administrate vcenter
=======
# vSphere Manager

A Flask-based web application for managing VMware vSphere infrastructure. This application provides a modern web interface for managing virtual machines, viewing performance metrics, and performing common VM operations.

## Features

- Connect to vCenter Server
- View and manage virtual machines
- Dynamic filtering and searching of VMs
- Perform VM operations (power on, power off, reset)
- View performance metrics and dashboards
- Responsive modern UI

## Prerequisites

- Python 3.8 or higher
- VMware vCenter Server
- Network access to vCenter Server

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your configuration:
   ```
   SECRET_KEY=your-secret-key
   ```

## Running the Application

1. Activate the virtual environment if not already activated
2. Run the Flask application:
   ```bash
   python app.py
   ```
3. Open a web browser and navigate to `http://localhost:5000`
4. Log in with your vCenter credentials

## Security Considerations

- The application uses HTTPS for secure communication with vCenter
- Credentials are never stored and are only used for the current session
- Session data is encrypted using Flask's secure session management
- SSL certificate verification can be enabled in production

## Contributing

Feel free to submit issues and enhancement requests!
>>>>>>> 11604816 (all)
