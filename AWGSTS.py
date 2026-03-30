import pyvisa
import time

usr_amp = int(input("desired amplitude: "))
usr_freq = int(input("desired frequency: "))
usr_wave = input("desired wave (SIN, SQU, TRI)")

rm = pyvisa.ResourceManager()
try:
    awg = rm.open_resource("TCPIP0::192.168.1.50::inst0::INSTR")
except ConnectionError:
    print("did not connect to device ")

cmd = ":SOUR:FUNC " + usr_wave
awg.write(awg, cmd)

awg.write(awg, ":SOUR:FREQ " + str(usr_freq))
awg.write(awg, ":SOUR:VOLT:AMPL " + str(usr_amp))

awg.write(awg, ":OUTP ON")
time.sleep(5)
awg.write(":OUTP OFF")
