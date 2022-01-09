################################################################################
# cat run_1.msl | awk -F '\t' '{print $1,$26,$43,$44,$45,$46,$56}'|less
# Time SPK: Traction retard VSS1 VSS2 VSS1 ms 1 VSS2 ms 1 TC slip * time

# the info for traction control says "slip% X 0.01s"
# Retard        0.0 3.3 6.7  10.0
# slip x time   0.0 6.7 13.3 20.0
# settings were above 50.1 mph and 10% slip
# vss1 rear / driven
# vss2 front / undriven

# roll a .05 second window for the multiplier

import re

tcslip_time = (0.0, 6.7, 13.3, 20.0)
tcslip_retard = (0.0, 3.3, 6.7, 10.0)
slip_percent = .10
tc_active_above = 50
slip_window_min = .01
slip_window_max = .05
slip_window = 0.01

time = []
vss1 = []
vss2 = []
vss1dot = []
vss2dot = []
tcsliptime = []
launch_timer = []
tc_retard = []
count = 0

f = open("run_1.msl","r")
lines = f.readlines()
for line in lines:
    details = re.split(r'\t', line)
    if(len(details) > 56):
        time.append(float(details[0]))
        vss1.append(float(details[42]))
        vss2.append(float(details[43]))
        vss1dot.append(float(details[44]))
        vss2dot.append(float(details[45]))
        tcsliptime.append(float(details[55]))
        launch_timer.append(float(details[47]))
        tc_retard.append(float(details[25]))


def percentage_difference_calculator(num1, num2):
    if(num2 < tc_active_above or num2 > num1):
        return 0
    else:
        return (abs(num1 - num2)/((num1 + num2)/2) * 100)

def tc_retard_calc(current_slip_time):
    if(current_slip_time < tcslip_time[1] and current_slip_time > tcslip_time[0]):
        return current_slip_time*(tcslip_retard[1] / tcslip_time[1])
    elif(current_slip_time < tcslip_time[2] and current_slip_time > tcslip_time[1]):
        return current_slip_time*(tcslip_retard[2] / tcslip_time[2])
    elif(current_slip_time < tcslip_time[3] and current_slip_time > tcslip_time[2]):
        return current_slip_time*(tcslip_retard[3] / tcslip_time[3])
    else:
        return 0

launch_active = False

while(count < len(vss1)):

    if(launch_timer[count] < 6 and vss1[count] > 0 and vss2[count] > 0):
        my_slip = (percentage_difference_calculator(vss1[count], vss2[count])) * slip_window
        # calculat the rolling slip window
        if(my_slip > slip_percent and slip_window < slip_window_max):
            slip_window = slip_window + .01
        elif(my_slip < slip_percent and slip_window > slip_window_min):
            slip_window = slip_window - .01

        my_retard = tc_retard_calc(my_slip)

        print("time: %0.2f tc_retard/my_retard: %0.2f/%0.2f tcslip/myslip: %0.2f/%0.2f difference %0.2f/%0.2f: %0.2f window: %0.2f"
                % (time[count], tc_retard[count], my_retard, tcsliptime[count], my_slip,
                vss1[count], vss2[count],
                (percentage_difference_calculator(vss1[count], vss2[count])*slip_window), slip_window))
    count = count + 1
