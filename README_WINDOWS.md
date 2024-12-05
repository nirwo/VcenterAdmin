# vSphere Manager - Windows Installation Guide

This guide will help you set up and run the vSphere Manager application on Windows.

## Prerequisites

1. Python 3.8 or higher (64-bit recommended)
2. Git (optional)
3. Access to a VMware vCenter Server
4. Network connectivity to vCenter Server

## Installation Steps

1. **Download the Code**
   - Download and extract the ZIP file
   - Or clone using Git: `git clone <repository-url>`

2. **Install Python**
   - Download Python from [python.org](https://www.python.org/downloads/)
   - During installation, make sure to:
     - Check "Add Python to PATH"
     - Check "Install pip"

3. **Set Up the Application**
   - Open Command Prompt as Administrator
   - Navigate to the project directory:
     ```cmd
     cd path\to\vsphere-manager
     ```
   - Run the setup script:
     ```cmd
     setup.bat
     ```

## Running the Application

1. **Activate the Virtual Environment**
   ```cmd
   venv\Scripts\activate
   ```

2. **Start the Application**
   ```cmd
   python run.py
   ```

3. **Access the Application**
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - Log in with your vCenter credentials

## Troubleshooting

### SSL Certificate Issues
If you encounter SSL certificate warnings, the application is configured to ignore them by default for development purposes. In a production environment, you should properly configure SSL certificates.

### Connection Issues
- Ensure you can ping your vCenter server
- Verify your credentials are correct
- Check if any firewall rules are blocking the connection

### Python Installation Issues
- Make sure you're using 64-bit Python
- Verify Python is in your system PATH
- Try running Command Prompt as Administrator

## Security Notes

1. The application uses HTTPS for secure communication with vCenter
2. Credentials are never stored and are only used for the current session
3. Session data is encrypted
4. For production use, consider:
   - Enabling SSL certificate verification
   - Setting up proper firewall rules
   - Using a reverse proxy for HTTPS

## Logging

Logs are stored in `vsphere_manager.log` in the application directory. Check this file for troubleshooting information.

## Support

If you encounter any issues:
1. Check the log file
2. Verify your Python and package versions
3. Ensure all prerequisites are met
4. Check your network connectivity to vCenter

## Updating

To update the application:
1. Back up your `.env` file
2. Download/pull the latest code
3. Run `setup.bat` again
4. Restore your `.env` file
