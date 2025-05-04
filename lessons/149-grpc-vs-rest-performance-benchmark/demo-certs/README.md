### Generate Certificate Authority

```bash
cfssl gencert -initca ca-csr.json | cfssljson -bare ca
```

### Generate Certificate for the client

```bash
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=demo rest-antonputra-pvt-csr.json | cfssljson -bare rest-antonputra-pvt
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=demo grpc-antonputra-pvt-csr.json | cfssljson -bare grpc-antonputra-pvt
```
