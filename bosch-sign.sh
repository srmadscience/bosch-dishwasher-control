cd /home/pi/bosch-dishwasher-control
source env/bin/activate
while
  :
do
  cd ~/bosch-dishwasher-control/e-Paper/RaspberryPi_JetsonNano/python/examples
  python3 update_sign.py /home/pi/hcpy 30
  if
    [ "$?" == 42 ]
  then
    echo waiting for MQTT...
    sleep 30
  else
    exit 1
  fi
done
