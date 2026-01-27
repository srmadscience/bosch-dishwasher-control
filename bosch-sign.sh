while
  :
do
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