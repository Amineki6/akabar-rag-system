#!/bin/bash

# --- 1. Variables ---
USERNAME="deployer"

# --- 2. System Updates & Install Docker (Official Repo) ---
apt-get update
apt-get install -y ca-certificates curl gnupg

# Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Add the Docker repository to Apt sources
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker and tools
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin fail2ban unattended-upgrades

# Enable automatic security updates
dpkg-reconfigure -f noninteractive unattended-upgrades

# --- 3. Create 'deployer' User & Setup SSH ---
useradd --create-home --shell "/bin/bash" --groups sudo "$USERNAME"
echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/90-cloud-init-users

mkdir -p /home/$USERNAME/.ssh

# Copy key from default 'ubuntu' user
cp /home/ubuntu/.ssh/authorized_keys /home/$USERNAME/.ssh/authorized_keys

chmod 700 /home/$USERNAME/.ssh
chmod 600 /home/$USERNAME/.ssh/authorized_keys
chown -R "$USERNAME:$USERNAME" /home/$USERNAME/.ssh

# --- 4. Hardening SSH ---
sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# --- 5. Firewall (UFW) ---
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# --- 6. Fix Docker Permissions (Run this EARLY) ---
# We do this before disk operations so it applies even if mounting hangs
usermod -aG docker "$USERNAME"

# --- 7. Robust Storage Setup (Nitro Compatible) ---
mkdir -p /mnt/mongo_data

# Detect the disk (Check for Nitro nvme1n1 OR Standard xvdf)
DATA_DISK=""
for i in {1..60}; do
if [ -b "/dev/nvme1n1" ]; then
    DATA_DISK="/dev/nvme1n1"
    break
elif [ -b "/dev/xvdf" ]; then
    DATA_DISK="/dev/xvdf"
    break
fi
sleep 1
done

if [ -z "$DATA_DISK" ]; then
    echo "ERROR: Could not find data volume!" > /var/log/mount_error.log
    exit 1
fi

# Mount the disk
mount "$DATA_DISK" /mnt/mongo_data

# Add to fstab using UUID (Safe against device name changes)
DISK_UUID=$(blkid -s UUID -o value "$DATA_DISK")
echo "UUID=$DISK_UUID /mnt/mongo_data ext4 defaults,nofail 0 2" >> /etc/fstab

systemctl enable docker
systemctl start docker