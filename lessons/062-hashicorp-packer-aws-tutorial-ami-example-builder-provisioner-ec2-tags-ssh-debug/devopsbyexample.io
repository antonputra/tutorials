server {
  listen 80;

  root /var/www/devopsbyexample.io/html;
  index index.html;

  server_name devopsbyexample.io;

  location / {
    try_files $uri $uri/ =404;
  }
}
