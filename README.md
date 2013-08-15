# Daemon Nginx uWSGI
==================

Daemon writing in python language it's developed on a mac osx lion, Nginx build on /usr/local/ and nginx build on a virtualenv

For execute you need change some paths to find nginx and uWSGI services.

***Note: you need have installed psutil if you don't have installed it***

run the command 

```bash
sudo easy_install psutil
```


How to use the script after install locate it into your root project /path/your/projectName/, the configuration for uswgi will be [projectName]_uwsgi.ini and this configuration will be locate on /path/your/projectName/conf

* **projectName_uwsgi.ini**

```bash
[uwsgi]
chdir=/path/your/projectName
socket=:8000
processes=4
idle=3600
master=true
pidfile=/tmp/projectName.pid
vacuum=True
max-requests=5000
daemonize=/var/log/uwsgi/projectName.log
env = DJANGO_SETTINGS_MODULE=ProjectName.settings
module = django.core.handlers.wsgi:WSGIHandler()
```

* **projectName_nginx.conf**

```bash
# projectName_nginx.conf
# the upstream component nginx needs to connect to
upstream django {
    server unix:///path/your/projectName/conf/projectName.sock; # for a file socket
    server osparidin.local:8000; # for a web port socket (we'll use this first)
    }

# configuration of the server
server {
    # the port your site will be served on
    listen      80;
    # the domain name it will serve for
    server_name osparidin.local; # substitute your machine's IP address or FQDN
    access_log /var/log/nginx/projectName.net_access.log;
    error_log /var/log/nginx/projectName.net_error.log;
    charset     utf-8;

    # max upload size
    client_max_body_size 75M;   # adjust to taste

    # Django media
    location /media  {
        alias /path/your/projectName/media;  # your Django project's media files - amend as required
    }

    location /static {
        alias /path/your/ProjectName/static; # your Django project's static files - amend as required
    }

    # Finally, send all non-media requests to the Django server.
    location / {
        uwsgi_pass  django;
        include     uwsgi_params; # the uwsgi_params file you installed
        }
}
```
* **nginx.conf**
*my file is locate on /usr/local/conf you need has created /usr/local/conf/site-enabled directory*

```bash
worker_processes 1;

error_log /var/log/nginx/error_log info;

events {
        worker_connections 256;
}

http {
        include /usr/local/conf/mime.types;
        default_type application/octet-stream;

        log_format main
                '$remote_addr - $remote_user [$time_local] '
                '"$request" $status $bytes_sent '
                '"$http_referer" "$http_user_agent" '
                '"$gzip_ratio"';

        client_header_timeout 10m;
        client_body_timeout 10m;
        send_timeout 10m;

        connection_pool_size 256;
        client_header_buffer_size 1k;
        large_client_header_buffers 4 2k;
        request_pool_size 4k;

        gzip on;
        gzip_min_length 1100;
        gzip_buffers 4 8k;
        gzip_types text/plain text/css application/x-javascript text/xml application/xml application/xml+rss text/javascript;

        output_buffers 1 32k;
        postpone_output 1460;

        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;

        keepalive_timeout 75 20;

        ignore_invalid_headers on;

        include sites-enabled/*.conf;
}
```

