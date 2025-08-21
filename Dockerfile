FROM registry.access.redhat.com/ubi9/httpd-24

USER root

# Install python3 + paramiko for SFTP
RUN dnf install -y python3 python3-pip openssh-clients && \
    pip3 install paramiko && \
    dnf clean all

# Enable CGI in Apache
RUN sed -i 's|^#LoadModule cgid_module|LoadModule cgid_module|' /etc/httpd/conf/httpd.conf && \
    sed -i 's|^#LoadModule cgi_module|LoadModule cgi_module|' /etc/httpd/conf/httpd.conf

# Copy CGI script and Apache config
COPY media.py /var/www/cgi-bin/media.py
COPY media.conf /etc/httpd/conf.d/media.conf

# Permissions
RUN chmod 755 /var/www/cgi-bin/media.py

# Fix line endings + permissions
RUN sed -i 's/\r$//' /var/www/cgi-bin/media.py && \
    chmod +x /var/www/cgi-bin/media.py

USER 1001

EXPOSE 8080
EXPOSE 8443

CMD ["/usr/bin/run-httpd"]
