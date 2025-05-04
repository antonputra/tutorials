# How to Get Letsencrypt Wildcard Certificate (Using Letsencrypt Nginx DNS Challenge)

[YouTube Tutorial](https://youtu.be/VJPfdXN-dSc)

## Prerequisites
- Ubuntu 20.04
- Nginx
- Certbot
- Watch this before: How to Secure Nginx with Lets Encrypt on Ubuntu 20.04 with Certbot? - https://youtu.be/R5d-hN9UtpU

## 1. Get Letsencrypt Wildcard Certificate
- Request wildcard certificate
```bash
sudo certbot certonly --manual --preferred-challenges dns --test-cert
```
- Enter `*.devopsbyexample.io`
- Create `TXT` record with following value: `_acme-challenge.devopsbyexample.io.` - `<generated value>`
- [Anycast](https://en.wikipedia.org/wiki/Anycast)
- Verify with dig -t txt 
```bash
dig -t txt +short _acme-challenge.devopsbyexample.io
```
- Press enter
> Certificate is saved at: /etc/letsencrypt/live/devopsbyexample.io/fullchain.pem  
> Key is saved at:         /etc/letsencrypt/live/devopsbyexample.io/privkey.pem

- Decode certificate
```bash
sudo openssl x509 -in /etc/letsencrypt/live/devopsbyexample.io/fullchain.pem -text -noout
```
## 2. Set Up Nginx SSL Wildcard Server Block
- Create folder for website
```bash
sudo mkdir -p /usr/share/devopsbyexample.io/html
```
- Update ownership
```bash
sudo chown -R $USER:$USER /usr/share/devopsbyexample.io/html
```
- Update permissions
```bash
sudo chmod -R 755 /usr/share/devopsbyexample.io
```
- Create `index.html` page
```bash
vi /usr/share/devopsbyexample.io/html/index.html
```
```html
<html>
    <head>
        <title>Welcome!</title>
    </head>
    <body>
        <h1>Wildcard server block is working!</h1>
    </body>
</html>
```
- Create nginx server block
```bash
sudo vi /etc/nginx/conf.d/devopsbyexample.io.conf
```
```conf
server {
    listen 80;

    root /usr/share/devopsbyexample.io/html;
    index index.html;

    server_name *.devopsbyexample.io;

    location / {
            try_files $uri $uri/ =404;
    }
}
```
- Test nginx config
```bash
sudo nginx -t
```
- Reload nginx config
```bash
sudo nginx -s reload
```
- Create `api.devopsbyexample.io` and `hello.devopsbyexample.io` A records
- Try `https://api.devopsbyexample.io/`
- Verify with dig
```bash
dig +short api.devopsbyexample.io
```
```bash
dig +short hello.devopsbyexample.io
```
- Check in the browser http://api.devopsbyexample.io

## 3. Secure Nginx with Lets Encrypt Certificate
- Update nginx config
```bash
sudo vi /etc/nginx/conf.d/devopsbyexample.io.conf
```
```conf
server {
    listen 80;
    server_name *devopsbyexample.io;
    return 301 https://$host$request_uri;
}

server {
    listen              443 ssl;
    ssl_certificate     /etc/letsencrypt/live/devopsbyexample.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/devopsbyexample.io/privkey.pem;
    ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ...
}
```
- Test nginx config
```bash
sudo nginx -t
```
- Fix `server_name`
- Reload nginx config
```bash
sudo nginx -s reload
```
- Go to `https://api.devopsbyexample.io/` and `https://hello.devopsbyexample.io/`

## Links
- [Challenge Types](https://letsencrypt.org/docs/challenge-types/)
