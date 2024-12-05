from waitress import serve
from app import app
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vsphere_manager.log'),
        logging.StreamHandler()
    ]
)

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))
    
    print(f"Starting vSphere Manager on http://localhost:{port}")
    print("Press Ctrl+C to quit")
    
    # Run with Waitress
    serve(app, host='0.0.0.0', port=port, threads=4)
