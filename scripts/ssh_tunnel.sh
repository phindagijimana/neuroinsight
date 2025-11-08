#!/bin/bash
# SSH Tunnel Helper for NeuroInsight
# This script helps you connect to the NeuroInsight app via SSH tunnel

echo "=================================================="
echo "  NeuroInsight - SSH Tunnel Setup"
echo "=================================================="
echo ""
echo "Run this command on YOUR LOCAL MACHINE:"
echo ""
echo "ssh -L 8000:localhost:8000 -L 56052:localhost:56052 pndagiji@ood.urmc-sh.rochester.edu"
echo ""
echo "Then access the app at:"
echo "  Frontend: http://localhost:56052"
echo "  Backend:  http://localhost:8000"
echo ""
echo "=================================================="
echo ""
echo "Optional: Add to your ~/.ssh/config for easier access:"
echo ""
cat << 'EOF'
Host neuroinsight
    HostName ood.urmc-sh.rochester.edu
    User pndagiji
    LocalForward 8000 localhost:8000
    LocalForward 56052 localhost:56052
    # Optional: Keep connection alive
    ServerAliveInterval 60
    ServerAliveCountMax 3

EOF
echo ""
echo "Then simply run: ssh neuroinsight"
echo "=================================================="

