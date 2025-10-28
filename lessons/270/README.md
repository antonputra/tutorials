# How to Create a Fully Private AWS EKS Cluster? (Client VPN & Resolve Private Route 53 DNS Locally)

You can find tutorial [here](https://youtu.be/Zv4c4YC-aAM).

## Commands

```bash
sudo apt-get update && sudo apt-get -y upgrade
curl -fsSL https://swupdate.openvpn.net/repos/repo-public.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/openvpn.gpg
echo "deb [signed-by=/etc/apt/keyrings/openvpn.gpg] http://build.openvpn.net/debian/openvpn/stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/openvpn.list
sudo apt-get update
sudo apt-get install -y openvpn
wget https://github.com/OpenVPN/easy-rsa/releases/download/v3.2.4/EasyRSA-3.2.4.tgz
tar -zxf EasyRSA-3.2.4.tgz
sudo mv EasyRSA-3.2.4/ /etc/openvpn/easy-rsa
sudo ln -s /etc/openvpn/easy-rsa/easyrsa /usr/local/bin/
cd /etc/openvpn/easy-rsa
easyrsa init-pki
easyrsa build-ca nopass
easyrsa gen-req openvpn-server nopass
easyrsa sign-req server openvpn-server
openvpn --genkey secret ta.key
sudo vim /etc/sysctl.conf
sudo sysctl -p
sudo iptables -t nat -S
ip route list default
sudo iptables -t nat -I POSTROUTING -s 10.8.0.0/24 -o ens5 -j MASQUERADE
sudo apt-get install iptables-persistent
sudo vim /etc/openvpn/server/server.conf
cat /etc/passwd | grep nobody
cat /etc/group | grep nogroup
sudo systemctl start openvpn-server@server
sudo systemctl status openvpn-server@server
sudo systemctl enable openvpn-server@server
journalctl --no-pager --full -u openvpn-server@server -f
easyrsa gen-req example-1 nopass
easyrsa sign-req client example-1
cat /etc/openvpn/easy-rsa/pki/ca.crt
cat /etc/openvpn/easy-rsa/pki/issued/example-1.crt
cat /etc/openvpn/easy-rsa/pki/private/example-1.key
cat /etc/openvpn/easy-rsa/ta.key
netstat -nr -f inet
journalctl --no-pager --full -u openvpn-server@server -f
aws eks update-kubeconfig --name dev-main --region us-east-1
```
