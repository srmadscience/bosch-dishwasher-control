cd /home/pi/hcpy
source venv/bin/activate
python3 hc2mqtt.py --config config.ini | grep FOUND