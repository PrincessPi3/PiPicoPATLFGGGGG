# SillyFilly Pi Pico W Power Analysis Tool
# LFGGGGGGGGGGG
# FRONG
A tool for simplifying power analysis attacks against other gadgets. 
Built on the Raspberry Pi Pico W, it runs a PWM channel to do manual clock control on the nugget you're hacking, and then reads an ADC channel to measure voltage used at each clock cycle.

## Installataion
Make sure you have Micropython installed on your Pico W.
Open up your Pico W in your favorite IDE (Thonny and VS Code are commonly used) and upload main.py.
If you're having trouble, see the official [Raspberry Pi Pico W Getting Started Page](https://projects.raspberrypi.org/en/projects/get-started-pico-w)

## Usage
1) Optional: edit the `power_analysis_pin` and `clock_pulse_pin` variables as you see fit
2) Edit the `ssid` and `password` variables with your wifi name (ssid) and the password
3) Set up the Pico W with pins on a breadboard, connect your power_analysis_pin and clock_pulse pin to the nugget (See Theory and Method)
3) Plug the Pico W to USB of your computer
4) Open the serial terminal of the Pico W
5) Reset the Pico W
6) When the Pico W connects, it will display a message like `Open web browser and navigate to http://x.x.x.x` Open a web browser on the same network and navigate to that address
7) Configure the options on the page to your liking (see below under Options)


## Options
### main.py
`power_analysis_pin`  
     This is the pin that is reading the power usage from the device  
     Defaults to GPIO 28  
  
`clock_pulse_pin`  
     This pin provides the clock signal that you will be using to manually take control of the nuggets clock  
     Defaults to GPIO 20  
  
`ssid`  
     This is your wifi network name. Only bgn supported (2.4GHz)  
     Dont forget the 's around the name  
  
`password`  
     Your wifi password  
     Dont forget the 's around the password  
  
### On the Webpage
`Duty Cycle`  
     The Percentage of the time that the clock is on vs off  
     50% is by far the most common, it makes a normal square wave and is the default output
    for most oscilators that you will be replacing  
  
`Frequency`  
     Frequency in Hertz (Hz)  
     How many times per second you want your nuggets clock to pulse  
     Dont make this too high  
  
`Samples Per Manual Clock Pulse`  
     This is how many times per clock pulse to sample the nuggets power usage  
     Dont make this too high  
  
## Hardware Needed
1) Raspberry Pi Pico W or Raspberry Pi Pico WH
2) Pins
3) Breadboard
4) Small capacitior (470uF is fine or anywhere within that range)
5) Wires 
6) Optional: spikey probes

## Theory
Power analysis attacks are very simple in concept.  
The idea is monitoring the amount of power a device uses very carefully to get some data leaked.  
Two things are most important during these attacks:  
1) Getting the most accurate, raw read of the power usage at a high sample rate
2) Controlling the clock of the device to slow down the processor enough to get the readings
  
To accomplish #1, we will get our power reading probe as close to the action of the processor as possible, while als adding a capacitor ground, which will pull any remaining juice out of the system.  

For #2, we need to remove the builtin crystal oscilator and replace that connection with our clock pulse probe.  
  
For this example, I will describe a firmware decryption power analysis attack.  
  
Scenario:  You have and ESP32-S3 based device with flash and bootloader encryption set up on it. You Can remove the RF sheield and get a raw dump of the flash chip with a SOP8 test clip and a programmer, but the data is encrypted.