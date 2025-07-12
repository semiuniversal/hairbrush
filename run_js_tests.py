import subprocess
import os
import sys

def main():
    js_dir = os.path.join(os.path.dirname(__file__), 'web_controller', 'static', 'js')
    os.chdir(js_dir)
    print('Running JS tests in:', js_dir)
    # Check for Node.js
    try:
        subprocess.run(['node', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(['npm', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        print('Error: Node.js and npm are required to run JS tests. Please install them and try again.')
        sys.exit(1)
    # Install dependencies if needed
    if not os.path.isdir('node_modules'):
        print('Installing npm dependencies...')
        subprocess.run(['npm', 'install'], check=True)
    # Run tests
    print('Running Vitest...')
    result = subprocess.run(['npm', 'test'])
    sys.exit(result.returncode)

if __name__ == '__main__':
    main() 