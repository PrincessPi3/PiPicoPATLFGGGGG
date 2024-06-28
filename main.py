import network
import socket
import machine
import utime
import _thread
import math
#import os


# gpio pin to read power analysis off of (int)
# reads 16bit (0-65535) between 0.0v and 3.3v
# (16 bit is phony, real read is 12 bit)
power_analysis_pin = 28

# output gpio pin generating clock pulse
clock_pulse_pin = 20

# Wi-Fi credentials
ssid = 'your-wifi-name-here'
password = 'yuour-wifi-password-here'

# == Clock Pulse Genertor == #
# starts a pwm
# usage do_pwm(int gpio_pin, float duty_cycle, int hertz frequency, int samples_per_clock_pulse)
def do_pwm(outpin = 20, duty_cycle = 0.5, frequency = 2000):
  print('Starting Clock Pulse PWM')
  output_pin = machine.Pin(outpin)
  pwm_pin = machine.PWM(output_pin)
  pwm_pin.freq(frequency)
  
  pwm_duty = math.floor(duty_cycle*65535)
  percent_duty = duty_cycle*100
  pwm_pin.duty_u16(pwm_duty)
  print(f"Clock Pulses Running\n\tGPIO Pin: {outpin}\n\tDuty Cycle: {percent_duty}%\n\tFrequency: {frequency}Hz")

# us of sleep calculate4d by floor(1000000 / (frequency_in_Hz * samples_per_pulse))
def us_samples(frequency, samples_per_pulse):
     return math.floor(1000000/(frequency*samples_per_pulse))

# == Read Value off of device == #
# uses ADC,  16bit output is phony, is actualloy 12bit.
# us of sleep calculate4d by floor(1000000 / (frequency_in_Hz * samples_per_pulse))
def do_adc(adcpin=28, duty_cycle = 0.5, frequency = 2000, samples_per_pulse = 100):
    print('Starting voltage reading ADC')
    semaphore_thread_adc = _thread.allocate_lock()
    analog_value = machine.ADC(adcpin)
    us_sample = us_samples(frequency, samples_per_pulse)
    while True:
        semaphore_thread_adc.acquire()
        reading = analog_value.read_u16()     
        print(reading)
        utime.sleep_us(us_sample)
        semaphore_thread_adc.release()

# == HTTP Stuff == #
# HTML template for the webpage
header = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SillyFilly Pi Pico Power Analysis Tool (LFFGGGGG)</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="preload" href="http://10.0.0.80/ComicCode-Regular.woff2" as="font" type="font/woff2" crossorigin>
            <style>
            body {{
                font-family: 'Comic Code';
                font-weight: normal;
                font-style: normal;
            }}

            form, div {{
                width: 80%;
                margin: auto;
            }}

            h1 {{
                font-size: 1.15em;'
            }}

            form input[type='number'] {{
                width: 3.6em;
            }}
            </style>
        </head>
        <body>
"""

footer = f"""
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

def running_webpage(outpin = 20, adcpin = 28, duty_cycle = 0.5, frequency = 2000, samples_per_pulse = 100):
    dutyy = duty_cycle*100
    us_sample = us_samples(frequency, samples_per_pulse)
    template = f"""
            {header}
            <div id="sillyrunninfg">
            <h1>SillyFilly Pi Pico Power Analysis Tool (LFFGGGGG)</h1>
            <h2>WE RUNNING NOWWWWW LFGGGGGGGGGGGGG</h2>
            <p>
                Clock Pulse Pin: <b>{outpin}</b><br>
                Power Analysis Pin: <b>{adcpin}</b><br><br>

                Frequency: <b>{frequency}Hz</b> (Duty Cycle: <b>{dutyy}%</b>)<br>
                Samples Per Pulse: <b>{samples_per_pulse}</b><br>
                Delay Between Samples: <b>{us_sample}us</b><br><br>
                <b>LFGGGGGGGG FRONG</b>
            </p>
            </div>
            {footer}
    """
    return str(template)

print("Board Started or Reset\n===========\n\n")

# Connect to WLAN
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
    
# Wait for Wi-Fi connection
connection_timeout = 10
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
    
# I like to have the LED on :3
led = machine.Pin('LED', machine.Pin.OUT)
led.value(1)

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
            print(f"power_analysis_pin: {power_analysis_pin}\nduty_cycle_in: {duty_cycle_in}\nfreq_in: {freq_in}\nsamples_per_pulse_in:{samples_per_pulse_in}")
            
            # run the clock pulse (PWM) task 
            do_pwm(clock_pulse_pin, duty_cycle_in, freq_in)

            # fork the voltage measuring ADC reading to the second core
            _thread.start_new_thread(do_adc, (power_analysis_pin, duty_cycle_in, freq_in, samples_per_pulse_in))
            
            response = running_webpage()

        else: 
            response = default_webpage()  

        # Send the HTTP response and close the conn
        conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        conn.send(response)
        conn.close()

    except OSError as e:
        conn.close()
        print('Connection closed')