#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd3in7
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from datetime import datetime, timedelta
import os.path

import subprocess

logging.basicConfig(level=logging.DEBUG)


def read_hcpy_config(filedir):
    """Read key = value pairs from hcpy's config.ini (no sections, quoted values)."""
    config = {}
    try:
        with open(os.path.join(filedir, 'config.ini'), encoding="utf-8") as f:
            for line in f:
                line = line.split('#', 1)[0].strip()
                if '=' not in line:
                    continue
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip().strip('"').strip("'")
    except OSError as e:
        logging.warning(f"Can't read hcpy config.ini: {e}")
    return config


def dishwasher_online(filedir, device='dishwasher'):
    """True only if hc2mqtt says both the bridge and the device are online.

    Reads the retained LWT topics that hc2mqtt publishes. Anything else - either
    topic offline or missing, or the broker unreachable - counts as lost contact.
    """
    config = read_hcpy_config(filedir)
    prefix = config.get('mqtt_prefix', 'homeconnect/')
    bridge_topic = prefix + 'LWT'
    device_topic = prefix + device + '/LWT'
    cmd = ['mosquitto_sub', '-h', config.get('mqtt_host', 'localhost'),
           '-p', config.get('mqtt_port', '1883'),
           '-t', bridge_topic, '-t', device_topic, '-v', '-C', '2', '-W', '5']
    if config.get('mqtt_username'):
        cmd += ['-u', config['mqtt_username']]
    if config.get('mqtt_password'):
        cmd += ['-P', config['mqtt_password']]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError) as e:
        logging.warning(f"Can't check MQTT LWT: {e}")
        return False
    states = dict(line.split(' ', 1) for line in result.stdout.splitlines() if ' ' in line)
    logging.info(f"LWT states: {states}")
    return states.get(bridge_topic) == 'online' and states.get(device_topic) == 'online'


def lost_contact_message(filedir):
    """'? HH:MM' using when hc2mqtt last received anything from the dishwasher."""
    try:
        last_heard = datetime.fromtimestamp(os.path.getmtime(os.path.join(filedir, 'message.dat')))
    except OSError:
        return '?'
    if last_heard.date() == datetime.today().date():
        return '? ' + last_heard.strftime("%H:%M")
    return '? ' + last_heard.strftime("%a %H:%M")

try:
    logging.info("epd3in7 Demo")
    
    epd = epd3in7.EPD()
    logging.info("init and Clear")
    epd.init(0)
    # epd.Clear(0xFF, 0)
    
    font100 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 100)
    font90 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 90)
    font72 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 72)
    font64 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 64)
    font36 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 36)
    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

    interesting_ones = {'BSH.Common.Option.ProgramProgress': 0,
                        'BSH.Common.Option.RemainingProgramTime': 0,
                        'BSH.Common.Status.Program.All.Count.Started': 0,
                        'Dishcare.Dishwasher.Status.ProgramPhase': "Unknown",
                        'BSH.Common.Root.SelectedProgram': "Unknown",
                        'BSH.Common.Status.OperationState': "Unknown",
                        'BSH.Common.Option.StartInRelative': 0,
                        'deviceID': 0}

    def update_sign_from_files(filedir, loop_seconds):

       logging.info(f"Started for files in {filedir}, checking every {loop_seconds} seconds")

       # Used to tell if the message has changed...
       old_washer_mode = ''
       old_activity = ''
       old_cycle_message = ''
    
       while True:
    
            for key in interesting_ones:
                filename = filedir + '/BSH_' + "_" + key + '.dat'
                if not os.path.isfile(filename):
                    sys.exit(42)
    
                with open(filename, 'r', encoding="utf-8") as file:
                    file_contents = file.read().rstrip()
                    interesting_ones[key] = file_contents
    
            percent_done = int(interesting_ones.get('BSH.Common.Option.ProgramProgress'))
            start_count = interesting_ones.get('BSH.Common.Status.Program.All.Count.Started')
            activity = interesting_ones.get('BSH.Common.Status.OperationState') + "/" + interesting_ones.get('Dishcare.Dishwasher.Status.ProgramPhase')

            # Create useful message...
            if interesting_ones.get('BSH.Common.Status.OperationState') == 'Ready':
                activity = 'Lurking'
                interesting_ones['Dishcare.Dishwasher.Status.ProgramPhase'] = ''
            elif interesting_ones.get('BSH.Common.Status.OperationState') == 'DelayedStart':
                activity = 'Waiting - ' +  interesting_ones.get('BSH.Common.Root.SelectedProgram')
                interesting_ones['Dishcare.Dishwasher.Status.ProgramPhase'] = ''
            elif interesting_ones.get('BSH.Common.Status.OperationState') == 'Finished':
                activity = 'Lurking'
                interesting_ones['Dishcare.Dishwasher.Status.ProgramPhase'] = ''

            # if we are planning on starting in the future...
            if int(interesting_ones.get('BSH.Common.Option.StartInRelative')) > 0:
                next_time = datetime.today() + timedelta(
                    seconds=int(interesting_ones.get('BSH.Common.Option.StartInRelative')))
                washer_mode = "Start " + next_time.strftime("%H:%M")
            # if we are running right now...
            elif interesting_ones.get('BSH.Common.Status.OperationState') == 'Run':
                next_time = datetime.today() + timedelta(
                    seconds=int(interesting_ones.get('BSH.Common.Option.RemainingProgramTime')))
                washer_mode = "End  " + next_time.strftime("%H:%M")
            else:
                washer_mode = interesting_ones.get('BSH.Common.Status.OperationState')

            # If hc2mqtt has lost the dishwasher, the .dat files are frozen and the
            # times above are meaningless: show '?' and when we last heard from it.
            if not dishwasher_online(filedir):
                washer_mode = lost_contact_message(filedir)
                activity = 'No contact'
                percent_done = 0  # stale too; show just the cycle number


            # Avoid overly frequent changes to the percent done level....
            if percent_done > 90:
                # Message every change...
                cycle_message = "Cycle " + start_count + " " + str(percent_done) + "%"
            elif int(percent_done) > 10:
                # Message every 10% change...
                cycle_message = "Cycle " + start_count + " " + str(percent_done - (percent_done % 10)) + "%"
            else:
                cycle_message = "Cycle " + start_count

            # Only do an update if something has actually changed...
            if (old_washer_mode != washer_mode)  or (old_activity != activity) or (old_cycle_message != cycle_message):

              logging.info(f"{washer_mode}, {activity}, {cycle_message}")

              # Display voodoo I don't understand...
              logging.info("1.Drawing on the Horizontal image...")
              Himage = Image.new('L', (epd.height, epd.width), 0xFF)  # 0xFF: clear the frame
              draw = ImageDraw.Draw(Himage)

              # Use slightly smaller font if > 9 characters...
              if len(washer_mode) <= 9:
                draw.text((10, 0), washer_mode, font = font100, fill = 0)
              else:
                draw.text((10, 0), washer_mode, font = font90, fill = 0)

              draw.text((10, 120), activity, font = font64, fill = 0)
              draw.text((10, 220), cycle_message, font = font36, fill = 0)
              epd.display_4Gray(epd.getbuffer_4Gray(Himage))

              # Update HTML file
              f = open('boschmessages.html', 'w', encoding="utf-8")
              f.write(f'<!DOCTYPE html>\n')
              f.write(f'<html><head><title>Dishwasher Status</title><meta http-equiv="refresh" content="30"></head>\n')
              f.write(f'<body>\n')
              f.write(f'<h1>\n')
              f.write(f'{washer_mode}\n')
              f.write(f'</h1><h1>\n')
              f.write(f'{activity}\n')
              f.write(f'</h1><h1>\n')
              f.write(f'{cycle_message}\n')
              f.write(f'</h1><h1>\n')
              f.write(f'{datetime.today().strftime("%H:%M")}\n')
              f.write(f'</h1>\n')
              f.write(f'</body></html>\n')
    
              f.flush()
              f.close()

            # Used to tell if the message has changed...
            old_washer_mode = washer_mode
            old_activity = activity
            old_cycle_message = cycle_message

            logging.info(f"Sleeping for {loop_seconds} seconds...")
            time.sleep(int(loop_seconds))


    if __name__ == '__main__':
      if len(sys.argv) != 3 :
        print('usage: ./update_sign.py  path loop_seconds')
        sys.exit(1)
  
      update_sign_from_files(sys.argv[1], sys.argv[2])
  
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd3in7.epdconfig.module_exit(cleanup=True)
    exit()
