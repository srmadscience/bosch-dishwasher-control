


import sys
import time
from datetime import datetime, timedelta


def update_sign_from_files(filedir, loop_seconds):
   interesting_ones = {'BSH.Common.Option.ProgramProgress':0,
                        'BSH.Common.Option.RemainingProgramTime':0,
                        'BSH.Common.Status.Program.All.Count.Started':0,
                        'Dishcare.Dishwasher.Status.ProgramPhase':"Unknown",
                        'BSH.Common.Root.SelectedProgram':"Unknown",
                        'BSH.Common.Status.OperationState':"Unknown",
                        'BSH.Common.Option.StartInRelative':0,
                        'deviceID':0}


   current_state = 'Unknown'
   start_count = 0
   percent_done = 0
   next_time = 0
   while True:
        for key in interesting_ones:
            with open(filedir + '/BSH_' + "_" + key + '.dat', 'r', encoding="utf-8") as file:
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
            activity = 'Waiting'
            next_time = datetime.today()
            interesting_ones['Dishcare.Dishwasher.Status.ProgramPhase'] = ''
        pct = ""

        if int(interesting_ones.get('BSH.Common.Option.StartInRelative')) > 0:
            next_time = datetime.today() + timedelta(
                seconds=int(interesting_ones.get('BSH.Common.Option.StartInRelative')))
            washer_mode = "Start " + next_time.strftime("%H:%M")
        elif int(interesting_ones.get('BSH.Common.Option.RemainingProgramTime')) > 0:
            next_time = datetime.today() + timedelta(
                seconds=int(interesting_ones.get('BSH.Common.Option.RemainingProgramTime')))
            washer_mode = "End  " + next_time.strftime("%H:%M")

        else:
            next_time = datetime.today()
            washer_mode = "Lurk  "

        print(washer_mode)
        print(activity)
        if int(percent_done) >0 :
            print("Cycle " + start_count + " " + percent_done + "%")
        else:
            print("Cycle " + start_count )

        print(" ")

        time.sleep(int(loop_seconds))




if __name__ == '__main__':
  if len(sys.argv) != 3 :
    print('usage: ./update_sign.py  path loop_seconds')
    sys.exit(1)
  
  update_sign_from_files(sys.argv[1], sys.argv[2])
  