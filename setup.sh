sudo cp bosch-sign.service /lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start bosch-sign
sudo systemctl enable bosch-sign