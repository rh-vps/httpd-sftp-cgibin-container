#!/usr/bin/env python3

print("Content-Type: text/plain\n")
print("CGI script is running correctly")


import os, sys, paramiko

# File requested from browser (/media/file1.txt -> PATH_INFO=/file1.txt)
filename = os.environ.get("PATH_INFO", "/").lstrip("/")

# SFTP connection details from environment
SFTP_HOST = os.environ.get("SFTP_HOST", "")
SFTP_USER = os.environ.get("SFTP_USER", "sftp-user")
SFTP_PASS = os.environ.get("SFTP_PASS", "password")
SFTP_DIR  = os.environ.get("SFTP_DIR", "/media")

try:
    # Connect to SFTP
    transport = paramiko.Transport((SFTP_HOST, 22))
    transport.connect(username=SFTP_USER, password=SFTP_PASS)
    sftp = paramiko.SFTPClient.from_transport(transport)

    remote_path = f"{SFTP_DIR}/{filename}"

    # Fetch file
    with sftp.open(remote_path, 'rb') as f:
        content = f.read()

    # Send response headers + file
    print("Content-Type: application/octet-stream")
    print(f"Content-Disposition: attachment; filename=\"{filename}\"")
    print("")
    sys.stdout.buffer.write(content)

    sftp.close()
    transport.close()

except Exception as e:
    print("Status: 404 Not Found")
    print("Content-Type: text/plain\n")
    print(f"Error fetching {filename}: {e}")
