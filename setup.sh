sudo cp bosch-sign.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start bosch-sign
sudo systemctl enable bosch-sign

sudo cp bosch-mqtt.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start bosch-mqtt
sudo systemctl enable bosch-mqtt