# bosch-dishwasher-control, or 'MQTT at home, for Fun And Profit!'



## My dishwasher uses MQTT? Really?




https://api-docs.home-connect.com/programs-and-options/#dishwasher

## Someone has already done a *ton* of work on this, so I used that...

https://github.com/hcpy2-0/hcpy
https://github.com/srmadscience/hcpy-hacked

https://github.com/srmadscience/hcpy-hacked/commit/ce5798fe9dd56af76dad954cd5c306f8ce91b3e1


## You'll need to run MQTT...

https://mosquitto.org/download/

## Finding a display to use...

https://thepihut.com/products/3-7-e-ink-display-hat-for-raspberry-pi-480x280

https://www.waveshare.com/wiki/3.7inch_e-Paper_HAT_Manual#Working_With_Raspberry_Pi

## Turning the MQTT data into something I can put on a sign...

## Next Steps and Things I Noticed

### Under the covers Bosch are using minutes, and then turning them into seconds

This causes problems when you take 'time remaining' and add it to 'now', as time remaining is only accurate to 60 seconds. Your end date ends up flipping back and forth between two values.

