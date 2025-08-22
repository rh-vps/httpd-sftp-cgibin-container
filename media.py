#!/usr/bin/env python3
import os
import sys
import paramiko
import html
import traceback
import stat

# --- Environment variables ---
SFTP_HOST = os.environ.get("SFTP_HOST")
SFTP_USER = os.environ.get("SFTP_USER")
SFTP_PASS = os.environ.get("SFTP_PASS")
SFTP_DIR  = os.environ.get("SFTP_DIR")  # relative to chroot

# CGI PATH_INFO → requested subpath under SFTP_DIR
path_info = os.environ.get("PATH_INFO", "")
relative_path = path_info.lstrip("/")  # e.g. "/foo/bar" → "foo/bar"

def sftp_connect():
    """Return connected (sftp, transport)"""
    transport = paramiko.Transport((SFTP_HOST, 22))
    transport.connect(username=SFTP_USER, password=SFTP_PASS)
    return paramiko.SFTPClient.from_transport(transport), transport

try:
    sftp, transport = sftp_connect()

    # Always anchor in SFTP_DIR
    remote_path = os.path.join(SFTP_DIR, relative_path) if relative_path else SFTP_DIR

    try:
        st = sftp.stat(remote_path)
    except FileNotFoundError:
        print("Status: 404 Not Found")
        print("Content-Type: text/plain\n")
        print(f"Path '{remote_path}' not found on SFTP server.")
        sys.exit(0)

    if stat.S_ISDIR(st.st_mode):
        # Directory listing
        files = sorted(sftp.listdir(remote_path))
        script_name = os.environ.get("SCRIPT_NAME", "/")

        print("Content-Type: text/html\n")
        print(f"<html><body><h2>Listing for {html.escape(script_name + path_info)}</h2><ul>")
        for f in files:
            safe = html.escape(f)
            link = f"{script_name}{path_info.rstrip('/')}/{safe}"
            print(f'<li><a href="{link}">{safe}</a></li>')
        print("</ul></body></html>")
    else:
        # File download
        filename = os.path.basename(remote_path)

        # 🔽 Force lowercase extension
        name, ext = os.path.splitext(filename)
        filename = name + ext.lower()

        print("Content-Type: application/octet-stream")
        print(f'Content-Disposition: attachment; filename="{filename}"\n')
        sys.stdout.flush()

        with sftp.open(remote_path, "rb") as f:
            while chunk := f.read(32768):
                sys.stdout.buffer.write(chunk)
                sys.stdout.buffer.flush()

    sftp.close()
    transport.close()

except Exception:
    print("Status: 500 Internal Server Error")
    print("Content-Type: text/plain\n")
    traceback.print_exc(file=sys.stdout)
