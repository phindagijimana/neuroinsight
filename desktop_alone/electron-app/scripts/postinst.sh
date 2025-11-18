#!/bin/bash
# Post-installation script for NeuroInsight

set -e

# Create desktop entry if it doesn't exist
if [ -f "/usr/share/applications/neuroinsight-standalone.desktop" ]; then
    echo "Desktop entry already exists"
else
    echo "Creating desktop entry..."
    cat > /usr/share/applications/neuroinsight-standalone.desktop << 'EOF'
[Desktop Entry]
Name=NeuroInsight
Comment=Hippocampal Asymmetry Analysis Tool
Exec=/opt/NeuroInsight/neuroinsight-standalone
Icon=neuroinsight-standalone
Type=Application
Categories=Science;MedicalSoftware;Education;Medical
StartupWMClass=NeuroInsight
EOF
    chmod 644 /usr/share/applications/neuroinsight-standalone.desktop
fi

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database
fi

# Create application directory structure
mkdir -p "/home/$SUDO_USER/.local/share/NeuroInsight"
mkdir -p "/home/$SUDO_USER/Documents/NeuroInsight/uploads"
mkdir -p "/home/$SUDO_USER/Documents/NeuroInsight/outputs"

# Set proper permissions
if [ -n "$SUDO_USER" ]; then
    chown -R "$SUDO_USER:$SUDO_USER" "/home/$SUDO_USER/.local/share/NeuroInsight"
    chown -R "$SUDO_USER:$SUDO_USER" "/home/$SUDO_USER/Documents/NeuroInsight"
fi

echo "NeuroInsight installation completed successfully!"
