import os
import paramiko
from dotenv import load_dotenv

def transfer_files(export_folder, remote_host, remote_username, remote_password, remote_path):
    # Establish SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(remote_host, username=remote_username, password=remote_password)

    # Create SFTP client
    sftp = ssh.open_sftp()

    # Transfer files
    for filename in os.listdir(export_folder):
        if filename.endswith('.md'):  # Transfer only markdown files
            local_path = os.path.join(export_folder, filename)
            remote_file_path = os.path.join(remote_path, filename)

            try:
                # Check if the file already exists on the remote server
                sftp.stat(remote_file_path)
                print(f"File already exists on the remote server: {filename}")
            except IOError:
                # File does not exist on the remote server, transfer it
                sftp.put(local_path, remote_file_path)
                print(f"Transferred file: {filename}")

    # Close SFTP client and SSH connection
    sftp.close()
    ssh.close()

# Load the configuration from the .env file
load_dotenv()
export_folder = os.getenv('EXPORT_FOLDER')
remote_host = os.getenv('REMOTE_HOST')
remote_username = os.getenv('REMOTE_USERNAME')
remote_password = os.getenv('REMOTE_PASSWORD')
remote_path = os.getenv('REMOTE_PATH')
transfer_enabled = os.getenv('TRANSFER_ENABLED', 'false').lower() == 'true'

if transfer_enabled:
    transfer_files(export_folder, remote_host, remote_username, remote_password, remote_path)
else:
    print("File transfer is disabled.")
