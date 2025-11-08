# Setting Up Nginx Reverse Proxy for Internal Access

## Overview

Instead of SSH tunnels, set up a proper internal URL like:
- `http://neuroinsight.urmc.rochester.edu`
- `http://hpc-node.rochester.edu:8000`

Lab members can access directly without SSH tunnels.

---

## Prerequisites

- Root/sudo access on HPC server (or contact IT)
- Open port 80 or 443 on server firewall
- Optional: Internal DNS entry

---

## Option A: Nginx with Port 80 (HTTP)

### 1. Install Nginx

```bash
# On RHEL/CentOS
sudo yum install nginx

# On Ubuntu/Debian
sudo apt-get install nginx
```

### 2. Create Nginx Config

```bash
sudo nano /etc/nginx/conf.d/neuroinsight.conf
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name neuroinsight.urmc.rochester.edu;  # or your server's hostname
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Increase upload size for MRI files
    client_max_body_size 500M;
    
    # Backend API
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts for long-running uploads
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
    }
}
```

### 3. Test and Enable

```bash
# Test configuration
sudo nginx -t

# Enable and start
sudo systemctl enable nginx
sudo systemctl start nginx

# Restart if already running
sudo systemctl restart nginx
```

### 4. Firewall (if needed)

```bash
# Open port 80
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

### 5. Access

Lab members now go directly to:
```
http://your-hpc-server.rochester.edu
```

No SSH tunnel needed!

---

## Option B: Nginx with HTTPS (Secure - Recommended)

### 1. Get SSL Certificate

**Option 1: Self-Signed (Internal only)**
```bash
# Generate certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/neuroinsight.key \
  -out /etc/nginx/ssl/neuroinsight.crt

# Answer prompts (use your institution's info)
```

**Option 2: Let's Encrypt (If public DNS)**
```bash
sudo yum install certbot python3-certbot-nginx
sudo certbot --nginx -d neuroinsight.urmc.rochester.edu
```

**Option 3: Institutional Certificate**
- Contact your IT department
- They can provide an official certificate

### 2. Nginx HTTPS Config

```bash
sudo nano /etc/nginx/conf.d/neuroinsight.conf
```

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name neuroinsight.urmc.rochester.edu;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name neuroinsight.urmc.rochester.edu;
    
    # SSL certificates
    ssl_certificate /etc/nginx/ssl/neuroinsight.crt;
    ssl_certificate_key /etc/nginx/ssl/neuroinsight.key;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Upload size
    client_max_body_size 500M;
    
    # Proxy to backend
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
    }
}
```

### 3. Enable and Restart

```bash
sudo nginx -t
sudo systemctl restart nginx
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 4. Access

Lab members go to:
```
https://neuroinsight.urmc.rochester.edu
```

Fully secure, no SSH tunnel!

---

## Option C: Simple Port Forward (No Nginx)

If you can't install Nginx, just allow external access to port 8000:

```bash
# Open firewall
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

Update `.env` to bind to all interfaces:

```bash
# In docker-compose.yml or .env
# Change backend port binding from:
# ports:
#   - "127.0.0.1:8000:8000"
# To:
# ports:
#   - "0.0.0.0:8000:8000"
```

Restart:
```bash
cd /mnt/nfs/home/urmc-sh.rochester.edu/pndagiji/hippo
docker-compose down
docker-compose up -d
```

Lab members access:
```
http://hpc-server-name:8000
```

**⚠️ Warning**: Less secure, only use on trusted internal network!

---

## DNS Setup (Optional but Recommended)

Contact your IT to create a DNS entry:

```
neuroinsight.urmc.rochester.edu → 123.45.67.89 (your HPC IP)
```

This gives you a friendly URL instead of IP address.

---

## Testing

### From Server:
```bash
curl http://localhost:8000
# Should return HTML
```

### From Lab Member's Computer:
```bash
# Test if accessible
curl http://neuroinsight.urmc.rochester.edu
# or
curl http://hpc-server-ip:8000
```

### In Browser:
```
http://neuroinsight.urmc.rochester.edu
# Should show NeuroInsight interface
```

---

## Troubleshooting

### "502 Bad Gateway"
- Backend not running: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`

### "Connection refused"
- Firewall blocking: Check firewall rules
- Nginx not running: `sudo systemctl status nginx`
- Wrong proxy_pass URL in nginx config

### "413 Request Entity Too Large"
- Increase `client_max_body_size` in nginx config
- Restart nginx

### Can't access from outside
- Firewall not open: `sudo firewall-cmd --list-all`
- Wrong IP/hostname
- Network routing issue (contact IT)

---

## Security Recommendations

1. **Restrict Access by IP** (if possible):
   ```nginx
   # In nginx config, add:
   allow 123.45.0.0/16;  # Your institution's IP range
   deny all;
   ```

2. **Add Basic Authentication** (temporary solution):
   ```bash
   sudo yum install httpd-tools
   sudo htpasswd -c /etc/nginx/.htpasswd labuser
   ```
   
   Add to nginx config:
   ```nginx
   auth_basic "NeuroInsight Access";
   auth_basic_user_file /etc/nginx/.htpasswd;
   ```

3. **Monitor Access**:
   ```bash
   # View nginx access logs
   sudo tail -f /var/log/nginx/access.log
   ```

---

## Next Steps

1. ✅ Choose your preferred method (HTTPS recommended)
2. ✅ Set up nginx configuration
3. ✅ Test from your computer
4. ✅ Share URL with lab members
5. ✅ Monitor usage and performance

---

## Need Help?

- **Nginx docs**: https://nginx.org/en/docs/
- **IT Support**: Contact your institution's IT for firewall/DNS
- **SSL Issues**: Check certificate paths and permissions

