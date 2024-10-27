# Nginx vs Apache Performance (Latency - Throughput - Saturation - Availability | HTTP/2 - TLS - Gzip)

You can find tutorial [here](https://youtu.be/UGp4LmocE7o).

## Apache

```bash
## Update VM

export HOST_NAME="apache"

sudo apt update && sudo apt -y upgrade
sudo sed -i "s/ubuntu/$HOST_NAME/" /etc/hostname
sudo sed -i "s/ubuntu/$HOST_NAME/" /etc/hosts
sudo reboot

## Installation
export APACHE_VERION="2.4.62" APR_VERSION="1.7.5" APR_UTIL_VERSION="1.6.3" PCRE_VERSION="10.44" EXPAT_VERSION="2.6.3"

sudo apt -y install build-essential zlib1g-dev libssl-dev libnghttp2-dev

wget https://dlcdn.apache.org/httpd/httpd-${APACHE_VERION}.tar.gz
tar -zxf httpd-${APACHE_VERION}.tar.gz
sudo mv httpd-${APACHE_VERION} /opt/httpd

wget https://dlcdn.apache.org//apr/apr-${APR_VERSION}.tar.gz
tar -zxf apr-${APR_VERSION}.tar.gz
sudo mv apr-${APR_VERSION} /opt/httpd/srclib/apr
sed -i 's|$RM "$cfgfile"|$RM -f "$cfgfile"|g' /opt/httpd/srclib/apr/configure

wget https://dlcdn.apache.org//apr/apr-util-${APR_UTIL_VERSION}.tar.gz
tar -zxf apr-util-${APR_UTIL_VERSION}.tar.gz
sudo mv apr-util-${APR_UTIL_VERSION} /opt/httpd/srclib/apr-util

wget https://github.com/PCRE2Project/pcre2/releases/download/pcre2-${PCRE_VERSION}/pcre2-${PCRE_VERSION}.tar.gz
tar -zxf pcre2-${PCRE_VERSION}.tar.gz
cd pcre2-${PCRE_VERSION}
./configure --prefix=/usr/local/pcre
make
sudo make install
cd ..

wget https://github.com/libexpat/libexpat/releases/download/R_2_6_3/expat-${EXPAT_VERSION}.tar.gz
tar -zxf expat-${EXPAT_VERSION}.tar.gz
cd expat-${EXPAT_VERSION}
./configure --prefix=/usr/local/expat
make
sudo make install
cd ..

cd /opt/httpd/
env PCRE_CONFIG=/usr/local/pcre/bin/pcre2-config \
./configure \
--enable-deflate \
--enable-ssl \
--enable-http2 \
--with-included-apr \
--prefix=/usr/local/apache2 \
--with-pcre=/usr/local/pcre \
--with-expat=/usr/local/expat

make
sudo make install

sudo mkdir -p /data /etc/ssl/certs/ /etc/ssl/private/

## Local
export SSH_KEY="~/.ssh/id_ed25519" SSH_USER="aputra" SERVER_IP="192.168.50.38"
scp -r -i ${SSH_KEY} /Users/antonputra/devel/tutorials/lessons/219/my-website/out ${SSH_USER}@${SERVER_IP}:/tmp/
scp -r -i ${SSH_KEY} /Users/antonputra/devel/private-tests/tls/certs/apache-antonputra-pvt-key.pem ${SSH_USER}@${SERVER_IP}:/tmp/
scp -r -i ${SSH_KEY} /Users/antonputra/devel/private-tests/tls/certs/apache-antonputra-pvt.pem ${SSH_USER}@${SERVER_IP}:/tmp/

## Remote
sudo mv /tmp/out/ /data/my-website/
sudo mv /tmp/apache-antonputra-pvt-key.pem /etc/ssl/private/apache-antonputra-pvt-key.pem
sudo mv /tmp/apache-antonputra-pvt.pem /etc/ssl/certs/apache-antonputra-pvt.pem

sudo tee /usr/local/apache2/conf/httpd.conf <<EOF
ServerRoot "/usr/local/apache2"

Listen 80

LoadModule authn_file_module modules/mod_authn_file.so
LoadModule ssl_module modules/mod_ssl.so
LoadModule socache_shmcb_module modules/mod_socache_shmcb.so
LoadModule authn_core_module modules/mod_authn_core.so
LoadModule authz_host_module modules/mod_authz_host.so
LoadModule authz_groupfile_module modules/mod_authz_groupfile.so
LoadModule authz_user_module modules/mod_authz_user.so
LoadModule authz_core_module modules/mod_authz_core.so
LoadModule access_compat_module modules/mod_access_compat.so
LoadModule auth_basic_module modules/mod_auth_basic.so
LoadModule reqtimeout_module modules/mod_reqtimeout.so
LoadModule filter_module modules/mod_filter.so
LoadModule mime_module modules/mod_mime.so
LoadModule log_config_module modules/mod_log_config.so
LoadModule env_module modules/mod_env.so
LoadModule headers_module modules/mod_headers.so
LoadModule setenvif_module modules/mod_setenvif.so
LoadModule version_module modules/mod_version.so
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
LoadModule proxy_ajp_module modules/mod_proxy_ajp.so
LoadModule proxy_wstunnel_module modules/mod_proxy_wstunnel.so
LoadModule proxy_balancer_module modules/mod_proxy_balancer.so
LoadModule proxy_connect_module modules/mod_proxy_connect.so
LoadModule rewrite_module modules/mod_rewrite.so
LoadModule slotmem_shm_module modules/mod_slotmem_shm.so
LoadModule lbmethod_byrequests_module modules/mod_lbmethod_byrequests.so
LoadModule http2_module modules/mod_http2.so
LoadModule unixd_module modules/mod_unixd.so
LoadModule status_module modules/mod_status.so
LoadModule autoindex_module modules/mod_autoindex.so
LoadModule dir_module modules/mod_dir.so
LoadModule alias_module modules/mod_alias.so
LoadModule deflate_module modules/mod_deflate.so

<IfModule unixd_module>
User daemon
Group daemon
</IfModule>

ServerAdmin me@antonputra.com

<Directory />
    Options Indexes FollowSymLinks Includes ExecCGI
    AllowOverride All
    Order deny,allow
    Allow from all
</Directory>

DocumentRoot "/usr/local/apache2/htdocs"

<Directory "/usr/local/apache2/htdocs">
    Options Indexes FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>

<IfModule dir_module>
    DirectoryIndex index.html
</IfModule>

<Files ".ht*">
    Require all denied
</Files>

ErrorLog "logs/error_log"
LogLevel warn

<IfModule log_config_module>
    LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
    LogFormat "%h %l %u %t \"%r\" %>s %b" common
    <IfModule logio_module>
      LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" %I %O" combinedio
    </IfModule>
    CustomLog "logs/access_log" common
</IfModule>

<IfModule alias_module>
    ScriptAlias /cgi-bin/ "/usr/local/apache2/cgi-bin/"
</IfModule>

<IfModule cgid_module>
</IfModule>

<Directory "/usr/local/apache2/cgi-bin">
    AllowOverride None
    Options None
    Require all granted
</Directory>

<IfModule headers_module>
    RequestHeader unset Proxy early
</IfModule>

<IfModule mime_module>
    TypesConfig conf/mime.types
    AddType application/x-compress .Z
    AddType application/x-gzip .gz .tgz
</IfModule>

Include conf/my-website.conf

<IfModule proxy_html_module>
Include conf/extra/proxy-html.conf
</IfModule>

<IfModule ssl_module>
SSLRandomSeed startup builtin
SSLRandomSeed connect builtin
</IfModule>
EOF

sudo tee /usr/local/apache2/conf/my-website.conf <<EOF
<VirtualHost *:80>
    SetOutputFilter DEFLATE
    ServerAdmin me@antonputra.com
    ServerName apache.antonputra.pvt
    DocumentRoot /data/my-website
</VirtualHost>

Listen 443

<VirtualHost *:443>
    SetOutputFilter DEFLATE
    ServerAdmin me@antonputra.com
    ServerName apache.antonputra.pvt
    DocumentRoot /data/my-website

	SSLEngine On

	Protocols h2 http/1.1

    SSLCertificateFile "/etc/ssl/certs/apache-antonputra-pvt.pem"
    SSLCertificateKeyFile "/etc/ssl/private/apache-antonputra-pvt-key.pem"
</VirtualHost>

<VirtualHost *:443>
	ServerName api-apache.antonputra.pvt
	SSLEngine On

	Protocols h2 http/1.1

    SSLCertificateFile "/etc/ssl/certs/apache-antonputra-pvt.pem"
    SSLCertificateKeyFile "/etc/ssl/private/apache-antonputra-pvt-key.pem"

	ProxyPass /api/devices balancer://myapp/api/devices

	<Proxy balancer://myapp>
		BalancerMember http://myapp-apache-0.antonputra.pvt:8080
        BalancerMember http://myapp-apache-1.antonputra.pvt:8080
	</Proxy>
</VirtualHost>
EOF

sudo /usr/local/apache2/bin/apachectl -k restart


## Tail access logs
tail -f /usr/local/apache2/logs/access_log
```
