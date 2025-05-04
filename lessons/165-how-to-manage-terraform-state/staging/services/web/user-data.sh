#!/bin/bash

cat > index.html <<EOF
<h1>Hello, World!</h1>
<p>PostgreSQL address: ${postgres_address}</p>
<p>PostgreSQL port: ${postgres_port}</p>
EOF

nohup busybox httpd -f -p ${server_port} &
