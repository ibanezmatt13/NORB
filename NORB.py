#!/usr/bin/python

import os
import serial
import crcmod
import time
import time as time_
 
gps_set_success = False # boolean for the status of flightmode
time_set = False 
 
# byte array for a UBX command to set flight mode
setNav = bytearray.fromhex("B5 62 06 24 24 00 FF FF 06 03 00 00 00 00 10 27 00 00 05 00 FA 00 FA 00 64 00 2C 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 16 DC")
setNMEA_off = bytearray.fromhex("B5 62 06 00 14 00 01 00 00 00 D0 08 00 00 80 25 00 00 07 00 01 00 00 00 00 00 A0 A9")
 
def disable_sentences():
    
    GPS = serial.Serial('/dev/ttyAMA0', 9600, timeout=1) # open serial to write to GPS
 
    # Disabling all NMEA sentences except $GPGGA
    GPS.write("$PUBX,40,GLL,0,0,0,0*5C\r\n")
    GPS.write("$PUBX,40,GSA,0,0,0,0*4E\r\n")
    GPS.write("$PUBX,40,RMC,0,0,0,0*47\r\n")
    GPS.write("$PUBX,40,GSV,0,0,0,0*59\r\n")
    GPS.write("$PUBX,40,VTG,0,0,0,0*5E\r\n")
    GPS.write("$PUBX,40,GGA,0,0,0,0*5A\r\n")
    
    GPS.close()
    
 

    
    
#create function equivalent to arduino millis();
def millis():
    return int(round(time_.time() * 1000))
 
 
#calcuate expected UBX ACK packet and parse UBX response from GPS
def getUBX_ACK(MSG):
    
    b = 0
    ackByteID = 0
    ackPacket = [0 for x in range(10)]
    startTime = millis()
 
 
    print "Reading ACK response: "
        
    #construct the expected ACK packet
    ackPacket[0] = int('0xB5', 16) #header
    ackPacket[1] = int('0x62', 16) #header
    ackPacket[2] = int('0x05', 16) #class
    ackPacket[3] = int('0x01', 16) #id
    ackPacket[4] = int('0x02', 16) #length
    ackPacket[5] = int('0x00', 16)
    ackPacket[6] = MSG[2] #ACK class
    ackPacket[7] = MSG[3] #ACK id
    ackPacket[8] = 0 #CK_A
    ackPacket[9] = 0 #CK_B
 
 
    #calculate the checksums
    for i in range(2,8):
        ackPacket[8] = ackPacket[8] + ackPacket[i]
        ackPacket[9] = ackPacket[9] + ackPacket[8]
 
 
    #print expected packet
    print "Expected ACK Response: "
    for byt in ackPacket:
        print byt
                
    print "Waiting for UBX ACK reply:"
    while 1:
        #test for success
        if ackByteID > 9 :
            #all packets are in order
            print "ACK has been acknowledged successfully!"
            return True
 
 
        #timeout if no valid response in 3 secs
        if millis() - startTime > 3000:
            print "The ACK has completely failed"
            return False
        #make sure data is availible to read
        if GPS.inWaiting() > 0:
            print "serial buffer contains data"
            b = GPS.read(1)
            print "following byte has been read from buffer:", ord(b)
                   
                  
            #check that bytes arrive in the sequence as per expected ACK packet
            if ord(b) == ackPacket[ackByteID]:
                print "this particular byte matches our expected response"
                ackByteID += 1
                #print ord(b)
            else:
                ackByteID = 0 #reset and look again, invalid order
                print "the byte doesn't match what was expected. Back to the start"
            print "current ackByteID:", ackByteID
        
 
    

     
 
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
counter = 0

 
 
# function to send both telemetry and packets
def send(data):
    NTX2 = serial.Serial('/dev/ttyAMA0', 300, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_TWO) # opening serial at 300 baud for radio transmission with 8 character bits, no parity and two stop bits
    NTX2.write(data) # write final datastring to the serial port
    print data
    NTX2.close()
 
def set_date_time(time):
   
    data = list(time)
    
    
      
    
    hours = time[0] + time[1]
    minutes = time[2] + time[3]
    
    parsed_datetime = hours + minutes
    os.system('sudo date --set ' + str(parsed_datetime))
    time_set = True
    
 
# function to read the gps and process the data it returns for transmission
def read_gps(flightmode_status):
    global counter
    import time # for some reason, importing time at the start is futile
    gps = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
    gps.write("$PUBX,00*33\n")
    NMEA_sentence = gps.readline() # read GPS








    print "GPS sentence has been read"
    while not NMEA_sentence.startswith("$PUBX"): # while we don't have a sentence
        gps.write("$PUBX,00*33\n")
        NMEA_sentence = gps.readline() # re-read ready for re-looping
        print "Still Bad Sentence"
        time.sleep(1) # wait for no reason what so ever :)
     
    gps.close()
 
    print NMEA_sentence
 
    
    data = NMEA_sentence.split(",") # split sentence into individual fields
 
    
        
    if data[18] == "0": # if it does start with a valid sentence but with no fix
        print "No Lock"
        pass
    
    else: # if it does start with a valid sentence and has a fix
    

      
            
    
        satellites = data[18]
        lats = data[3]
        northsouth = data[4]
        lngs = data[5]
        westeast = data[6]
        altitude = data[7]
       
        callsign = "NORB_Test" 
        time = data[2]
        
        if counter < 1 and time != 0:
            set_date_time(time)

        time = float(time) # ensuring that python knows time is a float
        string = "%06i" % time # creating a string out of time (this format ensures 0 is included at start if any)
        hours = string[0:2]
        minutes = string[2:4]
        seconds = string[4:6]
        time = str(str(hours) + ':' + str(minutes) + ':' + str(seconds)) # the final time string in form 'hh:mm:ss'
        
        latitude = convert(lats, northsouth)
        longitude = convert(lngs, westeast)
        
        string = str(callsign + ',' + time + ',' + str(counter) + ',' + str(latitude) + ',' + str(longitude) + ',' + str(flightmode_status) + ',' + satellites + ',' + altitude) # the data string
        csum = str(hex(crc16f(string))).upper()[2:] # running the CRC-CCITT checksum
        csum = csum.zfill(4) # creating the checksum data
        datastring = str("$$" + string + "*" + csum + "\n") # appending the datastring as per the UKHAS communication protocol
        counter += 1 # increment the sentence ID for next transmission
        print "now sending the following:", datastring
        send(datastring)
        
 
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
    gps_set_success = False    
    
        
    GPS = serial.Serial('/dev/ttyAMA0', 9600, timeout=3)
    print "serial opened"
    GPS.flush()
    sendUBX(setNav, len(setNav))
    print "sendUBX_ACK function complete"
    gps_set_success = getUBX_ACK(setNav)
    print "here is the current flightmode status:", gps_set_success
    sendUBX(setNMEA_off, len(setNMEA_off))
    GPS.close()
    print "serial port closed"
    read_gps(gps_set_success)
   
      
   
  

