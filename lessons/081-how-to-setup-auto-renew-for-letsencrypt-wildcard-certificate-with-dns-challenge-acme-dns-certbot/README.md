# How to Setup Auto-Renew for Letsencrypt WILDCARD Certificate with DNS challenge?

[YouTube Tutorial](https://youtu.be/7jEzioFsyNo)

## Allocate Elastic IP to EC2 Instance
- Add tag `Name` = `server`

## Create Ubuntu EC2 Instance
- Launch `Ubuntu 20.04` EC2 instance
- Create `server` SG
- Create `devops` key pair
- Associate Elastic IP address with EC2
- Update `devops` key pair permissions
```bash
chmod 400 devops.pem
```
- SSH to the EC2 instance
```bash
ssh -i devops.pem ubuntu@<public-ip>
```

## Install acme-dns Server
- Create folder for `acme-dns` and change directory
```bash
sudo mkdir /opt/acme-dns
cd !$
```
- Download and extract tar with `acme-dns` from GitHub
```bash
sudo curl -L -o acme-dns.tar.gz \
https://github.com/joohoi/acme-dns/releases/download/v0.8/acme-dns_0.8_linux_amd64.tar.gz
sudo tar -zxf acme-dns.tar.gz
```
- List files
```bash
ls
```
- Clean Up
```bash
sudo rm acme-dns.tar.gz
```
- Create soft link
```bash
sudo ln -s \
/opt/acme-dns/acme-dns /usr/local/bin/acme-dns
```
- Create a minimal `acme-dns` user
```bash
sudo adduser \
--system \
--gecos "acme-dns Service" \
--disabled-password \
--group \
--home /var/lib/acme-dns \
acme-dns
```
- Update default acme-dns config compare with IP from the AWS console. CAn't bind to the public address need to use private one.
```bash
ip addr
```
```bash
sudo mkdir -p /etc/acme-dns
sudo mv /opt/acme-dns/config.cfg /etc/acme-dns/
sudo vim /etc/acme-dns/config.cfg
```
- Move the systemd service and reload
```bash
cat acme-dns.service
sudo mv \
acme-dns.service /etc/systemd/system/acme-dns.service
sudo systemctl daemon-reload
```
- Start and enable acme-dns server
```bash
sudo systemctl enable acme-dns.service
sudo systemctl start acme-dns.service
```
- Check acme-dns for posible errors
```bash
sudo systemctl status acme-dns.service
```
- Use journalctl to debug in case of errors
```bash
journalctl --unit acme-dns --no-pager --follow
```
- Create A record for your domain
```bash
auth.devopsbyexample.io IN A <public-ip>
```
- Create NS record for auth.devopsbyexample.io pointing to auth.devopsbyexample.io. This means, that auth.devopsbyexample.io is responsible for any *.auth.devopsbyexample.io records
```bash
auth.devopsbyexample.io IN NS auth.devopsbyexample.io
```
- Test acme-dns server (Split the screen)
```bash
journalctl -u acme-dns --no-pager --follow
```
- From local host try to resolve random DNS record
```
dig api.devopsbyexample.io
dig api.auth.devopsbyexample.io
dig 7gvhsbvf.auth.devopsbyexample.io
```

## Install acme-dns-client
```bash
sudo mkdir /opt/acme-dns-client
cd !$

sudo curl -L \
-o acme-dns-client.tar.gz \
https://github.com/acme-dns/acme-dns-client/releases/download/v0.2/acme-dns-client_0.2_linux_amd64.tar.gz

sudo tar -zxf acme-dns-client.tar.gz
ls
sudo rm acme-dns-client.tar.gz
sudo ln -s \
/opt/acme-dns-client/acme-dns-client /usr/local/bin/acme-dns-client
```
## Install Certbot
```bash
cd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```
## Get Letsencrypt Wildcard Certificate
- Create a new acme-dns account for your domain and set it up
```bash
sudo acme-dns-client register \
-d devopsbyexample.io -s http://localhost:8080
```
```
dig _acme-challenge.devopsbyexample.io
```
- Get wildcard certificate
```bash
sudo certbot certonly \
  --manual \
  --test-cert \
  --preferred-challenges dns \
  --manual-auth-hook 'acme-dns-client' \
  -d *.devopsbyexample.io
```

```
sudo openssl x509 -text -noout \
-in /etc/letsencrypt/live/devopsbyexample.io/fullchain.pem
```
- Renew certificate (test)
```bash
sudo certbot renew \
  --manual \
  --test-cert \
  --dry-run \
  --preferred-challenges dns \
  --manual-auth-hook 'acme-dns-client'
```
```
dig -t txt _acme-challenge.devopsbyexample.io
```
## Setup Auto-Renew for Letsencrypt WILDCARD Certificate
- Setup cronjob
```bash
sudo crontab -e
0 */12 * * * certbot renew --manual --test-cert --preferred-challenges dns --manual-auth-hook 'acme-dns-client'
```
## Clen Up
- Terminate EC2 Instance
- Delete `devops` key pair
- Delete `server` SG
- Release `server` Elastic IP
- Delete DNS records from google domains

## Links
- [acme-dns](https://github.com/joohoi/acme-dns)
- [acme-dns-client](https://github.com/acme-dns/acme-dns-client)
