# Archive3 Apache Setup

The following is an example configuration for an Apache vhost.

This serves static content and pass all other requests to the uwsgi handler.

```
<VirtualHost *:80>
    ServerName archive3.org
    ServerAlias www.archive3.org
    CustomLog /var/log/apache2/access_log-archive3.org combined
    ErrorLog /var/log/apache2/error_log-archive3.org
    ProxyPreserveHost On
    ProxyPass "/" "http://127.0.0.1:9090/"
    ProxyPassReverse "/" "http://127.0.0.1:9090/"
</VirtualHost>

```