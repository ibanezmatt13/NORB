#!/usr/bin/python
 
import os
import serial
import crcmod
import time
import time as time_
 

trigger = False

 
# byte array for a UBX command to set flight mode
setNav = bytearray.fromhex("B5 62 06 24 24 00 FF FF 06 03 00 00 00 00 10 27 00 00 05 00 FA 00 FA 00 64 00 2C 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 16 DC")
# byte array for UBX command to disable automatic NMEA response from GPS
setNMEA_off = bytearray.fromhex("B5 62 06 00 14 00 01 00 00 00 D0 08 00 00 80 25 00 00 07 00 01 00 00 00 00 00 A0 A9")
 
# function to disable all NMEA sentences
def disable_sentences():
    
    GPS = serial.Serial('/dev/ttyAMA0', 9600, timeout=1) # open serial to write to GPS
 
    # Disabling all NMEA sentences 
    GPS.write("$PUBX,40,GLL,0,0,0,0*5C\r\n")
    GPS.write("$PUBX,40,GSA,0,0,0,0*4E\r\n")
    GPS.write("$PUBX,40,RMC,0,0,0,0*47\r\n")
    GPS.write("$PUBX,40,GSV,0,0,0,0*59\r\n")
    GPS.write("$PUBX,40,VTG,0,0,0,0*5E\r\n")
    GPS.write("$PUBX,40,GGA,0,0,0,0*5A\r\n")
    
    GPS.close() # close serial
    
 

    
    
#create function equivalent to arduino millis();
def millis():
    return int(round(time_.time() * 1000))
 
 

 
    
 
     
# fucntion to send commands to the GPS 
def sendUBX(MSG, length):
    
    print "Sending UBX Command: "
    ubxcmds = ""
    for i in range(0, length):
        GPS.write(chr(MSG[i])) #write each byte of ubx cmd to serial port
        ubxcmds = ubxcmds + str(MSG[i]) + " " # build up sent message debug output string
    GPS.write("\r\n") #send newline to ublox
    print ubxcmds #print debug message
    print "UBX Command Sent..."
 
 
 
 
crc16f = crcmod.predefined.mkCrcFun('crc-ccitt-false') # function for CRC-CCITT checksum
disable_sentences()
counter = 0 # this counter will increment as our sentence_id
 
 
 
# function to send both telemetry and packets
def send(data):
    NTX2 = serial.Serial('/dev/ttyAMA0', 300, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_TWO) # opening serial at 300 baud for radio transmission with 8 character bits, no parity and two stop bits
    NTX2.write(data) # write final datastring to the serial port
    print data
    NTX2.close()
    
 
# function to read the gps and process the data it returns for transmission
def read_gps():
    satellites = 0
    lats = 0
    northsouth = 0
    lngs = 0
    westeast = 0
    altitude = 0
    time = 0
    latitude = 0
    longitude = 0
    
    global counter
    gps = serial.Serial('/dev/ttyAMA0', 9600, timeout=1) # open serial for GPS
    gps.write("$PUBX,00*33\n") # reuest a PUBX sentence
    NMEA_sentence = gps.readline() # read GPS
    
    print "GPS sentence has been read"
    if NMEA_sentence.startswith("$PUBX"): # while we don't have a sentence
        #gps.write("$PUBX,00*33\n")
        #NMEA_sentence = gps.readline() # re-read ready for re-looping
        #print "Still Bad Sentence"
     
        gps.close() # close serial
 
        print NMEA_sentence
 
        data = NMEA_sentence.split(",") # split sentence into individual fields
 
    
        
        if data[18] == "0": # if it does start with a valid sentence but with no fix
            print "No Lock"
            pass
    
        else: # if it does start with a valid sentence and has a fix
    
        # parsing required telemetry fields
            satellites = data[18]
            lats = data[3]
            northsouth = data[4]
            lngs = data[5]
            westeast = data[6]
            altitude = int(float(data[7]))
       
         
            time = data[2]
        
        
 
            time = float(time) # ensuring that python knows time is a float
            string = "%06i" % time # creating a string out of time (this format ensures 0 is included at start if any)
            hours = string[0:2]
            minutes = string[2:4]
            seconds = string[4:6]
            time = str(str(hours) + ':' + str(minutes) + ':' + str(seconds)) # the final time string in form 'hh:mm:ss'
        
            latitude = convert(lats, northsouth)
            longitude = convert(lngs, westeast)
    
    callsign = "NORB_Test"
        
    if altitude >= 29900:
        trigger = True
    else:
        trigger = False
        
    string = str(callsign + ',' + time + ',' + str(counter) + ',' + str(latitude) + ',' + str(longitude) + ',' + satellites + ',' + str(trigger) + ',' + str(altitude)) # the data string
    csum = str(hex(crc16f(string))).upper()[2:] # running the CRC-CCITT checksum
    csum = csum.zfill(4) # creating the checksum data
    datastring = str("$$" + string + "*" + csum + "\n") # appending the datastring as per the UKHAS communication protocol
    counter += 1 # increment the sentence ID for next transmission
    print "now sending the following:", datastring
    send(datastring) # send the datastring to the send function to send to the NTX2
           

 
# function to convert latitude and longitude into a different format 
def convert(position_data, orientation):
        decs = "" 
        decs2 = "" 
        for i in range(0, position_data.index('.') - 2): 
            decs = decs + position_data[i]
        for i in range(position_data.index('.') - 2, len(position_data) - 1):
            decs2 = decs2 + position_data[i]
        position = float(decs) + float(str((float(decs2)/60))[:8])
        
        if orientation == ("S") or orientation == ("W"): 
            position = 0 - position 
 
        return position
 
 
 
 
 
 
 
 
while True:
    
    GPS = serial.Serial('/dev/ttyAMA0', 9600, timeout=1) # open serial
    print "serial opened"
    GPS.flush() # wait for bytes to be physically read from the GPS
    sendUBX(setNav, len(setNav)) # send command to enable flightmode
    print "sendUBX_ACK function complete"
    sendUBX(setNMEA_off, len(setNMEA_off)) # turn NMEA sentences off
    GPS.flush()
    GPS.close() # close the serial
    print "serial port closed"
    
    read_gps() # run the read_gps function to get the data and parse it with status of flightmode
