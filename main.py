import network
import socket
import machine
from machine import Timer
import utime
import _thread
import math

# gpio pin to read power analysis off of (int)
# reads 16bit (0-65535) between 0.0v and 3.3v
# (16 bit is phony, real read is 12 bit)
power_analysis_pin = 28

# output gpio pin generating clock pulse
clock_pulse_pin = 20

# this pin gets power and toggles off and on every X PWM cycles
# it powers the board you're targeting
power_on_pin = 2

# how many seconds to power the board before reset
seconds_awake = 3

# Wi-Fi credentials
ssid = 'your-wifi-name-here'
password = 'your-wifi-password-here'

# == Clock Pulse Genertor == #
# starts a pwm
# usage do_pwm(int gpio_pin, float duty_cycle, int hertz frequency, int samples_per_clock_pulse)
def do_pwm(outpin, duty_cycle, frequency):
    global pwm_pin
    output_pin = machine.Pin(outpin)
    
    # configure pwm
    pwm_pin = machine.PWM(output_pin)
    pwm_pin.freq(frequency) # frequency in Hz
    pwm_duty = math.floor(duty_cycle*65535) # duty cycle is a uint 16bit 

    # run da pwm
    pwm_pin.duty_u16(pwm_duty)

# us of sleep calculate4d by ceil(1000000 / (frequency_in_Hz * samples_per_pulse))
# 1000000 is one million, 1,000,000 or 10^6
def us_samples(frequency, samples_per_pulse):
    return math.ceil(1000000/(frequency*samples_per_pulse))

# == Read Value off of device == #
# uses ADC,  16bit output is phony, is actualloy 12bit.
kill = False # for the thread killing hack
def do_adc(adcpin, frequency, samples_per_pulse):
    analog_value = machine.ADC(adcpin)
    us_sample = us_samples(frequency, samples_per_pulse)

    global kill
    while True:
        reading = analog_value.read_u16() # do the actual reading, actual precision is 12bit
        print(reading,',',sep='')
        utime.sleep_us(us_sample)

        # just keep checking if kill is set to True by reset_init()
        # if it is True, reset kill to False, kill the thread, and break for good measure
        if kill is True:
            kill = False
            _thread.exit()
            break

# HTML template for the webpage
header = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>SillyFilly Pi Pico Power Analysis Tool (LFFGGGGG)</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <!-- todo: actually host this font file somewhere lmfao -->
            <link rel="preload" href="http://10.0.0.80/ComicCode-Regular.woff2" as="font" type="font/woff2" crossorigin>
            <style>
            body {
                font-family: 'Comic Code', 'Comic Sans MS', Monospace;
                font-weight: normal;
                font-style: normal;
            }

            form, div {
                width: 80%;
                margin: auto;
            }

            h1 {
                font-size: 1.15em;'
            }

            form input[type='number'] {
                width: 3.6em;
            }
            </style>
        </head>
        <body>
"""

footer = """
        </body>
        </html>
"""

def default_webpage():
    template = f"""
            {header}
            <form action="/action">
            <h1>SillyFilly Pi Pico Power Analysis Tool (LFFGGGGG)</h1>
            <b>Config:</b><br>
                Duty Cycle<br><input id="duty_cycle" name="duty_cycle" type="range" min="0" max="1" step="0.01" value="0.5">  <output id="duty_cycle_output">50%</output><br><br>
                Frequency (Hz)<br><input type="number" size="5" name="freq" value="2000"><br><br>
                Samples Per Clock Pulse:<br> <input type="number" size="5" id="samples_per_pulse" name="samples_per_pulse" value="5"><br><br>
                <input type="submit" value="Go, Baby, Go!">
            </form>
            <script>
                const value = document.querySelector("#duty_cycle_output");
                const input = document.querySelector("#duty_cycle");

                input.addEventListener("input", (event) => {{
                value.textContent = (event.target.value*100)+"%";
                }});
            </script>
            {footer}
        """
    return str(template)

def running_webpage(outpin, adcpin, duty_cycle, frequency, samples_per_pulse, loop_time):
    dutyy = duty_cycle*100
    us_sample = us_samples(frequency, samples_per_pulse)
    template = f"""
            {header}
            <div id="sillyrunninfg">
            <h1>SillyFilly Pi Pico Power Analysis Tool (LFFGGGGG)</h1>
            <h2>WE RUNNING NOWWWWW LFGGGGGGGGGGGGG</h2>
            <p>
                Clock Pulse Pin: <b>{outpin}</b><br>
                Power Analysis Pin: <b>{adcpin}</b><br>
                Power On Pin:{power_on_pin} <b></b><br><br><br>

                Frequency: <b>{frequency}Hz</b> (Duty Cycle: <b>{dutyy}%</b><br>
                Samples Per Pulse: <b>{samples_per_pulse}</b><br>
                Delay Between Samples: <b>{us_sample}us</b><br><br>
                Loop length: <b>{loop_time}</b><br><br><br>
                <b>LFGGGGGGGG FRONG</b>
            </p>
            </div>
            {footer}
    """
    return str(template)

print("Board Started or Reset\n===========\n\n")

toggle_power = machine.Pin(power_on_pin, machine.Pin.OUT)
toggle_power.value(0)

# I like to have the LED on :3
led = machine.Pin('LED', machine.Pin.OUT)
led.value(1)

# do da thingggggssssss for da loooop
def reset_init(t):
    global kill
    kill = True # kill da adc thread
    toggle_power.value(0) # kill power on pin
    print("==Looping==")
    pwm_pin.deinit() # stop pwm
    utime.sleep(1)
    toggle_power.value(1) # re-enable power on pin
    do_pwm(clock_pulse_pin, duty_cycle_in, freq_in) # restart pwm

    # restart da threaddyyyyy
    _thread.start_new_thread(do_adc, (power_analysis_pin, freq_in, samples_per_pulse_in))

# Connect to WLAN
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
    
# Wait for Wi-Fi connection
connection_timeout = 9
while connection_timeout > 0:
    if wlan.status() >= 3:
        break
    connection_timeout -= 1
    print('Waiting for Wi-Fi connection...')
    utime.sleep(1)
    
# Check if connection is successful
if wlan.status() != 3:
    raise RuntimeError('Failed to establish a network connection')
else:
    print('Connection successful!')
    network_info = wlan.ifconfig()
    print(f"\n\nOpen web browser and navigate to http://{network_info[0]}\n\n")

# Set up socket and start listening
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen()

while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(1024)
        request = str(request)

        try:
            fullreq = request.split()
            request = fullreq[1]
        except IndexError:
            pass
        
        # Process the action page!
        if request.startswith('/action?', 0):
            # parse the request path to extract da GET vars
            req_string = request.split('?')[1]
            req_vars = req_string.split('&')
            for f in req_vars:
                req_split = f.split('=')
                # Type strict whitelist for safety and compatibility
                if req_split[0] == 'duty_cycle':
                    duty_cycle_in = float(req_split[1])
                elif req_split[0] == 'freq':
                    freq_in = int(req_split[1])
                elif req_split[0] == 'samples_per_pulse':
                    samples_per_pulse_in =  int(req_split[1])

            loop_time = (seconds_awake-1)*1000 # the -1 is because reset_init() adds a 1 second delay
            dutyyy = duty_cycle_in*100
            us_sample = us_samples(freq_in, samples_per_pulse_in)

            print(f"Clock pulse pin: {clock_pulse_pin}\n\nPower analysis pin: {power_analysis_pin}\n\nPower on pin: {power_on_pin}\n\nDuty cycle: {duty_cycle_in}%\n\nFrequency: {freq_in}Hz\n\nSamples per clock pulse: {samples_per_pulse_in}\n\nTime between samples: {us_sample}us\n\nLoop length: {loop_time}ms\n\n")

            # run the clock pulse (PWM) task 
            do_pwm(clock_pulse_pin, duty_cycle_in, freq_in)

            # fork the voltage measuring ADC reading to the second core
            _thread.start_new_thread(do_adc, (power_analysis_pin,  freq_in, samples_per_pulse_in))

            Timer(mode=Timer.PERIODIC, period=loop_time, callback=reset_init)

            # outpin, adcpin, duty_cycle, frequency, samples_per_pulse, loop_time
            response = running_webpage(clock_pulse_pin, power_analysis_pin, dutyyy, freq_in, samples_per_pulse_in, loop_time)

        else: 
            response = default_webpage()  

        # Send the HTTP response and close the conn
        conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        conn.send(response)
        conn.close()

    except OSError as e:
        conn.close()
        print('Connection closed')