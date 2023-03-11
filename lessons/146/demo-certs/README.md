### Generate Certificate Authority

```bash
cfssl gencert -initca ca-csr.json | cfssljson -bare ca
```

### Generate Certificate for the client

```bash
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=demo api-nginx-antonputra-pvt-csr.json | cfssljson -bare api-nginx-antonputra-pvt
```
