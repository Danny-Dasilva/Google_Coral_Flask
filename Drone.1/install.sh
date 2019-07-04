sudo pip3 install svgwrite
if grep -s -q "MX8MQ" /sys/firmware/devicetree/base/model; then
  echo "Installing DevBoard specific dependencies"
  sudo apt-get install python3-pip
  sudo apt-get install python3-dev
  python3 -m pip install python-periphery
  sudo pip3 install adafruit-circuitpython-servokit
  wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/libgpiod.sh
  chmod +x libgpiod.sh
  ./libgpiod.sh

else
  # Install gstreamer
  sudo apt-get install -y gstreamer1.0-plugins-bad gstreamer1.0-plugins-good py$

  if grep -s -q "Raspberry Pi" /sys/firmware/devicetree/base/model; then
    echo "Installing Raspberry Pi specific dependencies"
    sudo apt-get install python3-rpi.gpio
    # Add v4l2 video module to kernel
    if ! grep -q "bcm2835-v4l2" /etc/modules; then
      echo bcm2835-v4l2 | sudo tee -a /etc/modules
    fi
    sudo modprobe bcm2835-v4l2
  fi
fi
