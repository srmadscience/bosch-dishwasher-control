


import sys
import time
from datetime import datetime, timedelta
import os.path


def update_sign_from_files(filedir, loop_seconds):
   interesting_ones = {'BSH.Common.Option.ProgramProgress':0,
                        'BSH.Common.Option.RemainingProgramTime':0,
                        'BSH.Common.Status.Program.All.Count.Started':0,
                        'Dishcare.Dishwasher.Status.ProgramPhase':"Unknown",
                        'BSH.Common.Root.SelectedProgram':"Unknown",
                        'BSH.Common.Status.OperationState':"Unknown",
                        'BSH.Common.Option.StartInRelative':0,
                        'deviceID':0}

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

        percent_done = interesting_ones.get('BSH.Common.Option.ProgramProgress')
        start_count = interesting_ones.get('BSH.Common.Status.Program.All.Count.Started')
        activity = interesting_ones.get('BSH.Common.Status.OperationState') + "/" + interesting_ones.get('Dishcare.Dishwasher.Status.ProgramPhase')

        next_time = datetime.today() + timedelta(
            seconds=int(interesting_ones.get('BSH.Common.Option.RemainingProgramTime')))

        if interesting_ones.get('BSH.Common.Status.OperationState') == 'Ready':
            activity = 'Lurking'
            next_time = datetime.today()
            interesting_ones['Dishcare.Dishwasher.Status.ProgramPhase'] = ''
        elif interesting_ones.get('BSH.Common.Status.OperationState') == 'DelayedStart':
            activity = 'Waiting - ' +  interesting_ones.get('BSH.Common.Root.SelectedProgram')
            next_time = datetime.today()
            interesting_ones['Dishcare.Dishwasher.Status.ProgramPhase'] = ''


        pct = ""

        if int(interesting_ones.get('BSH.Common.Option.StartInRelative')) > 0:
            next_time = datetime.today() + timedelta(
                seconds=int(interesting_ones.get('BSH.Common.Option.StartInRelative')))
            washer_mode = "Start " + next_time.strftime("%H:%M")
        elif interesting_ones.get('BSH.Common.Status.OperationState') == 'Run':
            next_time = datetime.today() + timedelta(
                seconds=int(interesting_ones.get('BSH.Common.Option.RemainingProgramTime')))
            washer_mode = "End  " + next_time.strftime("%H:%M")
        else:
            washer_mode = interesting_ones.get('BSH.Common.Status.OperationState')
            next_time = datetime.today()

        if int(percent_done) > 0:
            cycle_message = "Cycle " + start_count + " " + percent_done + "%"
        else:
            cycle_message = "Cycle " + start_count



        if (old_washer_mode != washer_mode)  or (old_activity != activity) or (old_cycle_message != cycle_message):
          print(washer_mode)
          print(activity)
          print(cycle_message)
          print(datetime.today().strftime("%H:%M"))

          f = open('boschmessages.html', 'w', encoding="utf-8")



          f.write(f'<!DOCTYPE html>\n')
          f.write(f'<html><heed><title>Dishwasher Status</title</head>\n')
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

        old_washer_mode = washer_mode
        old_activity = activity
        old_cycle_message = cycle_message

        time.sleep(int(loop_seconds))




if __name__ == '__main__':
  if len(sys.argv) != 3 :
    print('usage: ./update_sign.py  path loop_seconds')
    sys.exit(1)
  
  update_sign_from_files(sys.argv[1], sys.argv[2])
  