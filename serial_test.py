# -*- coding: utf-8 -*-
import os, sys
import time
import binascii
import intelhex2bin
import serial


import zilog_ocd


def main():
    print("|---------------------------------------------|")
    print("|             ZILOG programmer                |")
    print("|---------------------------------------------|")
    print()
    try:
        arg1 = str(sys.argv[1]) # primeiro argumento
        arg2 = str(sys.argv[2]) # segundo argumento
    except:
        arg1 = ""

    if (arg1 == ""):
        print ("  -Usage: python updater.py [filename.txt]")
        print (arg1)
        print (arg2)
    else:
        try:
            ser = serial.Serial("COM3", 57600)
            ser.timeout = 1
            success = 1;
            print("Sucesso")
            print("Porta:    " + ser.port)
            print("Baudrate: " + str(ser.baudrate))
        except:
            success = 0;
            print("Falha na Abertura de " + ser.port)
       
        if success == 1:
            command = zilog_ocd.ocd_read_revision()
            ser.write(command)
            input = ser.read(4);
            #input = binascii.hexlify(input)
            print(input)
            
            ser.write(command)
            input = ser.read(4);
            input = binascii.hexlify(input)
            print(input)
        
        """
        while (finish == 0):
            pos = file.tell()   # Returns the file's current position
            line = file.readline()  # Reads one entire line from the file
            output = line[9:-2]
            print(pos)
            print(output)
            output = binascii.unhexlify(output)
            final_file.write(output)
            
            finish = 1
        
        file.close()
        final_file.close()
        """
        
        """
        try:
            ser = serial.Serial("COM1", 9600)
            ser.timeout = 1
            success = 1;
            print("Sucesso")
            print("Porta:    " + ser.port)
            print("Baudrate: " + str(ser.baudrate))
        except:
            success = 0;
            print("Falha na Abertura de " + ser.port)
        
        if (success == 1):
            finish = 0;
            ack = 0
            while (finish == 0):
                pos = file.tell()
                line = file.readline()
                output = binascii.unhexlify(line[:-2])
                ser.write(output)
                if (ack == 0):
                    time.sleep(.5)
                    ser.baudrate = 115200
                print(output)
                leitura = ser.readline()
                print(leitura)
                
                if (leitura == b'ms\x01\x07PEA0402H\r\n'):
                    print("Vamo que vamo!")
                    ack = 1
                # elif (leitura[:4] == bytes([109, 115, 1, 8])):
                    # print("ACK bloco")
                # elif (leitura[:4] == bytes([109, 115, 1, 8])):
                    # finish = 1
                else:
                    file.seek(pos)
        """
                    
if __name__ == "__main__":
    main()    