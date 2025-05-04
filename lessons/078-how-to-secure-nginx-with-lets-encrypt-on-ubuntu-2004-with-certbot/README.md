# How to Secure Nginx with Lets Encrypt on Ubuntu 20.04 with Certbot?

[YouTube Tutorial](https://youtu.be/R5d-hN9UtpU)

## 1. Create EC2 Instance in AWS Ubuntu 20.04 LTS
- Create EC2 instance
  - `Ubuntu 20.04`
  - `t3.micro` (**cpu cores > 1**)
  - `public subnet`
  - `enable public ip`
- Create Security Group `nginx`
  - open port `80`, and `443`
- Create `devops` kep pair
- Update permissions on `devops` key pair
  - Keys need to be only readable by you `chmod 400 devops.pem`
## 2. Install Nginx Ubuntu 20.04 LTS
- SSH to the Ubuntu server
```bash
ssh -i devops.pem ubuntu@34.229.113.7
```
- Update Ubuntu packages
```bash
sudo apt update
```
- Check version of `nginx` to be installed
```bash
apt policy nginx
```
- Check current versions of `nginx` [here](http://nginx.org/en/download.html)
- Add `nginx` deb repository
```bash
sudo vi /etc/apt/sources.list.d/nginx.list
```
```
deb https://nginx.org/packages/ubuntu/ focal nginx
deb-src https://nginx.org/packages/ubuntu/ focal nginx
```
> deb lines are relative to binary packages, that you can install with apt.
deb-src lines are relative to source packages (as downloaded by apt-get source $package) and next compiled.
Source packages are needed only if you want to compile some package yourself, or inspect the source code for a bug. Ordinary users don't need to include such repositories.
- Update Ubuntu packages
```bash
sudo apt update
```
- Add GPG key
```bash
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ABF5BD827BD9BF62
```
- Update Ubuntu packages
```bash
sudo apt update
```
- Check version of `nginx` to be installed
```bash
apt policy nginx
```
- Install `nginx`
```bash
sudo apt install nginx=1.20.1-1~focal
```
- Start `nginx`
```bash
sudo systemctl start nginx
```
- Enable `nginx`
```bash
sudo systemctl enable nginx
```
- Check `nginx` status
```bash
sudo systemctl status nginx
```
> (Can't open PID file /run/nginx.pid (yet?) after start: Operation not permitted)
- Go to browser

## 3. Nginx Setup Server Block
- Check the main `nginx` config
```bash
cat /etc/nginx/nginx.conf
```
- Check default `nginx` config
```bash
cat /etc/nginx/conf.d/default.conf
```
- Create folder for our website
```bash
sudo mkdir -p /var/www/devopsbyexample.io/html
```
- Update ownership
```bash
sudo chown -R $USER:$USER /var/www/devopsbyexample.io/html
```
- Update permissions
```bash
sudo chmod -R 755 /var/www/devopsbyexample.io
```
- Create a web page
- `vi /var/www/devopsbyexample.io/html/index.html`
```html
<html>
    <head>
        <title>Welcome to devopsbyexample.io!</title>
    </head>
    <body>
        <h1>Success!  The devopsbyexample.io server block is working!</h1>
    </body>
</html>
```
- Create `sites-available` directory
```bash
sudo mkdir /etc/nginx/sites-available/
```
- Create `sites-enabled` directory
```bash
sudo mkdir /etc/nginx/sites-enabled
```
- Create `nginx` server block
```bash
sudo vi /etc/nginx/sites-available/devopsbyexample.io
```

```conf
server {
        listen 80;

        root /var/www/devopsbyexample.io/html;
        index index.html;

        server_name devopsbyexample.io www.devopsbyexample.io;

        location / {
                try_files $uri $uri/ =404;
        }
}
```
- Add include statement
```bash
sudo vi /etc/nginx/nginx.conf
```
```
include /etc/nginx/sites-enabled/*;
```
- Create a symlink
```bash
sudo ln -s /etc/nginx/sites-available/devopsbyexample.io /etc/nginx/sites-enabled/
```
- Test `nginx` config
```bash
sudo nginx -t
```
- Reload `nginx` config
```bash
sudo nginx -s reload
```
- Create A records
- Check DNS (if you are using cloudflare enable full strict by ssl/tsl>overview>full_strict)
```
dig devopsbyexample.io
dig www.devopsbyexample.io
```

## 4. Install Certbot on Ubuntu 20.04 LTS
- Go to official certbot [page](https://certbot.eff.org/lets-encrypt/ubuntufocal-nginx.html)
- Go to install snap [page](https://snapcraft.io/docs/installing-snap-on-ubuntu)
- Check snap version
```bash
snap version
```
- If you don't have it `apt policy snapd` and `apt install snapd`
- Ensure that your version of snapd is up to date
```bash
sudo snap install core; sudo snap refresh core
```
- Remove certbot-auto and any Certbot OS packages
```bash
sudo apt-get remove certbot
```
- Install Certbot
```bash
sudo snap install --classic certbot
```
- Prepare the Certbot command
```bash
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```
- Check certbot version
```
sudo certbot --version
```

## 5. Secure Nginx with Lets Encrypt on Ubuntu 20.04 LTS
- Test certbot
```bash
sudo certbot --nginx --test-cert
```
- Open nginx block
```bash
cat /etc/nginx/sites-available/devopsbyexample.io
```
- Go to browser https://devopsbyexample.io
- Issue real certificate
```
sudo certbot --nginx
```
- Go to browser https://devopsbyexample.io
- Go to browser https://www.devopsbyexample.io
- Test renewal
```bash
sudo certbot renew --dry-run
```
- Check systemctl times
```bash
systemctl list-timers
```

## Clean Up
- Delete EC2 instance
- Delete security group `nginx`
- Delete key pair `devops`
- Remove A records

## Links
- [Ubuntu Releases](https://wiki.ubuntu.com/Releases)
- [Nginx Download](http://nginx.org/en/download.html)
- [Nginx Installation](https://www.nginx.com/resources/wiki/start/topics/tutorials/install/)
- [Failed to read PID from file /run/nginx.pid](https://bugs.launchpad.net/ubuntu/+source/nginx/+bug/1581864)
- [Sites-Available/Sites-Enabled Not Here?](https://www.digitalocean.com/community/questions/sites-available-sites-enabled-not-here)
- [Certbot](https://certbot.eff.org/lets-encrypt/ubuntufocal-nginx.html)
- [Installing snap on Ubuntu](https://snapcraft.io/docs/installing-snap-on-ubuntu)
