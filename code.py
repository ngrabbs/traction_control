import time
import analogio
import digitalio
import board

sample_speed = .01
tcslip_time = (0.0, 6.7, 13.3, 20.0)
tcslip_retard = (0.0, 3.3, 6.7, 10.0)
slip_percent = .10
tc_active_above = 50
slip_window_min = .01
slip_window_max = .05
slip_window = 0.01
magic_number = 200
my_slip = 0
my_retard = 0

button = digitalio.DigitalInOut(board.A2)
button.switch_to_input(pull=digitalio.Pull.UP)

def percentage_calculator(num1, num2):
    if(num2 < tc_active_above or num2 > num1):
        return 0
    else:
        return (abs(num1 - num2)/((num1 + num2)/2) * 100)

def tc_retard_calc(current_slip_time):
    if(current_slip_time > slip_percent and current_slip_time < tcslip_time[1] and current_slip_time > tcslip_time[0]):
        print("level one retard " + str(tcslip_retard[1]) + " " + str(tcslip_time[1]))
        return current_slip_time*(tcslip_retard[1] / tcslip_time[1])
    elif(current_slip_time > slip_percent and current_slip_time < tcslip_time[2] and current_slip_time > tcslip_time[1]):
        print("level two retard " + str(tcslip_retard[2]) + " " + str(tcslip_time[2]))
        return current_slip_time*(tcslip_retard[2] / tcslip_time[2])
    elif(current_slip_time > slip_percent and current_slip_time < tcslip_time[3] and current_slip_time > tcslip_time[2]):
        print("level three retard " + str(tcslip_retard[3]) + " " + str(tcslip_time[3]))
        return current_slip_time*(tcslip_retard[3] / tcslip_time[3])
    else:
        return 0

while True:
    if button.value:
        slip_window = .01
    if not button.value:
        offset = magic_number / 65532
        vss1 = analogio.AnalogIn(board.A0)
        vss2 = analogio.AnalogIn(board.A1)
        vss1_mph = vss1.value * offset
        vss2_mph = vss2.value * offset

        if(vss1_mph > 0 and vss2_mph > 0):
            my_slip = ((percentage_calculator(vss1_mph, vss2_mph)) * slip_window)
            # calculate the rolling slip window
            if(my_slip > slip_percent and slip_window < slip_window_max):
                slip_window = slip_window + .01
            elif(my_slip < slip_percent and slip_window > slip_window_min):
                slip_window = slip_window - .01

            if(my_slip > slip_percent):
                my_retard = tc_retard_calc(my_slip*100)
            else:
                my_retard = 0

            if(my_retard > 0):
                print("vss1:[%0.2f] vss2:[%0.2f] slip:[%0.2f] retard:[%0.2f] window:[%0.2f]" %
                    (vss1_mph, vss2_mph, my_slip,  my_retard, slip_window))

#        print("(%0.2f,%0.2f,%0.2f,%0.2f)" %
#            (vss1_mph, vss2_mph, my_slip,  my_retard))

        vss1.deinit()
        vss2.deinit()
        time.sleep(sample_speed)