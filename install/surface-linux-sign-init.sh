#!/usr/bin/env bash

set -e

# assume on Ubuntu

cd "$HOME"

cat << EOF > "$HOME/mokconfig.cnf"
# This definition stops the following lines failing if HOME isn't
# defined.
HOME                    = .
RANDFILE                = $ENV::HOME/.rnd 
[ req ]
distinguished_name      = req_distinguished_name
x509_extensions         = v3
string_mask             = utf8only
prompt                  = no

[ req_distinguished_name ]
countryName             = us
stateOrProvinceName     = ca
localityName            = berkeley
0.organizationName      = UCB
commonName              = Secure Boot Signing Key
emailAddress            = christian.kolen@gmail.com

[ v3 ]
subjectKeyIdentifier    = hash
authorityKeyIdentifier  = keyid:always,issuer
basicConstraints        = critical,CA:FALSE
extendedKeyUsage        = codeSigning,1.3.6.1.4.1.311.10.3.6
nsComment               = "OpenSSL Generated Certificate"
EOF

openssl req -config "$HOME/mokconfig.cnf" \
    -new -x509 -newkey rsa:2048 \
    -nodes -days 36500 -outform DER \
    -keyout "MOK.priv" \
    -out "MOK.der"

openssl x509 -in MOK.der -inform DER -outform PEM -out MOK.pem

sudo mokutil --import MOK.der

echo "Do: reboot, Enroll MOK, Continue, Yes, reboot"
