!#/bin/bash
# Copy and paste the lines below to install the 64-bit EL 6.x set.
#
BOOTSTRAP_TAR="bootstrap-trunk-x86_64-20170127.tar.gz"
BOOTSTRAP_SHA="dcb6128284e7e8529a8a770d55cf93d97550558c"

# Download the bootstrap kit to the current directory.
curl -O https://pkgsrc.joyent.com/packages/Linux/el6/bootstrap/${BOOTSTRAP_TAR}

# Verify the SHA1 checksum.
echo "${BOOTSTRAP_SHA}  ${BOOTSTRAP_TAR}" > check-shasum
sha1sum -c check-shasum

# Verify PGP signature.  This step is optional, and requires gpg.
curl -O https://pkgsrc.joyent.com/packages/Linux/el6/bootstrap/${BOOTSTRAP_TAR}.asc
curl -sS https://pkgsrc.joyent.com/pgp/56AAACAF.asc | gpg2 --import
gpg2 --verify ${BOOTSTRAP_TAR}{.asc,}

# Install bootstrap kit to /usr/pkg
sudo tar -zxpf ${BOOTSTRAP_TAR} -C /

# Add paths
echo 'export PATH=/usr/pkg/sbin:/usr/pkg/bin:$PATH'
echo 'export MANPATH=/usr/pkg/man:$MANPATH'
