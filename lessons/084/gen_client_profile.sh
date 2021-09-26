#!/bin/bash

KEY_DIR=/etc/openvpn/easy-rsa
OUTPUT_DIR=/etc/openvpn/client-configs
BASE_CONFIG=/etc/openvpn/client-configs/base.ovpn

cat ${BASE_CONFIG} \
    <(echo -e '<ca>') \
    ${KEY_DIR}/pki/ca.crt \
    <(echo -e '</ca>\n<cert>') \
    ${KEY_DIR}/pki/issued/${1}.crt \
    <(echo -e '</cert>\n<key>') \
    ${KEY_DIR}/pki/private/${1}.key \
    <(echo -e '</key>\n<tls-crypt>') \
    ${KEY_DIR}/ta.key \
    <(echo -e '</tls-crypt>') \
    > ${OUTPUT_DIR}/${1}.ovpn
