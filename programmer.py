# -*- coding: utf-8 -*-
import os, sys
import time
import binascii
import serial

import intelhex2bin
import zilog_ocd


# Gets a 8-bit bytes object, reflects its bits and returns it 
def reflect_byte(byte):
    reflected_byte = 0
    
    aux = byte & 0x01
    aux = aux << 7
    reflected_byte += aux    
    aux = byte & 0x02
    aux = aux << 5
    reflected_byte += aux     
    aux = byte & 0x04
    aux = aux << 3
    reflected_byte += aux 
    aux = byte & 0x08
    aux = aux << 1
    reflected_byte += aux
    aux = byte & 0x10
    aux = aux >> 1
    reflected_byte += aux
    aux = byte & 0x20
    aux = aux >> 3
    reflected_byte += aux    
    aux = byte & 0x40
    aux = aux >> 5
    reflected_byte += aux
    aux = byte & 0x80
    aux = aux >> 7
    reflected_byte += aux
    
    reflected_byte = reflected_byte.to_bytes(1, byteorder='little')
    
    return reflected_byte
    
# Gets an 16-bit bytes object, reflects its bits and returns it 
def reflected_word(word):
    
    result = bytes(0)
    word_pieces = list(word)    # Converts word to a list
    result += reflect_byte(word_pieces[1])
    result += reflect_byte(word_pieces[0])
    
    return result
    
# Gets a bytes object and inverts its bits  
def invert_word(word):
    word = int.from_bytes(word, byteorder='little')
    word = ~word
    word = word.to_bytes(2, byteorder='little', signed=True)
    
    return word
    
# Calculates CRC from a binary file and returns it as an int value
def calculate_bin_crc(file):
    file.seek(0)
            
    file_data = file.read()
    file_data_reflected = bytes(0)
    for byte in file_data:
        reflected_byte = reflect_byte(byte)                            
        file_data_reflected += reflected_byte                
    crc_value = binascii.crc_hqx(file_data_reflected, 0xFFFF)
    crc_value = crc_value.to_bytes(2, byteorder='little')
    crc_value = reflected_word(crc_value)
    crc_value = invert_word(crc_value)
    crc_value = int.from_bytes(crc_value, byteorder='little')
    
    return (crc_value)
    

def main():
    print("|---------------------------------------------|")
    print("|             ZILOG programmer                |")
    print("|---------------------------------------------|")
    print()
    try:
        arg1 = str(sys.argv[1]) # First argument - hex file
        arg2 = str(sys.argv[2]) # Second argument - COM port
        arg3 = str(sys.argv[3]) # Third argument - MCU type
    except:
        arg1 = ""

    if (arg1 == ""):
        print ("  -Usage: python programmer.py [fw_file.hex] [serial port] [MCU]")
        print (arg1)
        print (arg2)
        print (arg3)
        
    else:
        abs_path = os.getcwd()    # Gets 
        abs_path = os.path.join(abs_path, "data")        
        os.makedirs(abs_path, exist_ok=True)        # Creates an "data" subfolder, if it doesn't exists
        abs_path_binary_file = os.path.join(abs_path, "fw_to_write.bin")    
        abs_path_mcu_data_file = os.path.join(abs_path, "mcu_data.bin") 
        
        mcu_data_file = open(abs_path_mcu_data_file,"w+b")  # Creates the file in binary mode, with read and write permissions  
        
        # Checks MCU type and configures variables
        success = 1
        if ('Z8F24' in arg3):
            fw_size = 24576
            clock = 11059200
        elif ('Z8F08' in arg3):
            fw_size = 8192
            clock = 5529600
        elif ('Z8F04' in arg3):
            fw_size = 4096
            clock = 5529600
        else:
            success = 0
            print("MCU was not defined! ")                          
             
        success = 0
        print ("Analysing file '"+ arg1 +"'")
        output_file = intelhex2bin.convert_intelhex_to_bin(arg1, fw_size, abs_path_binary_file)       
        if output_file != '':
            print ("Conversion finished succesfully")
            success = 1
        else:
            print ("Conversion unsuccesful")
             
        try:
            ser = serial.Serial(arg2, 28800)            
            ser.timeout = 3
            ser.reset_input_buffer()
            success = 1;
            print("Sucesso")
            print("Porta:    " + ser.port)
            print("Baudrate: " + str(ser.baudrate))
        except:
            success = 0;
            print("Falha na Abertura de " + ser.port)


        # Enter debug
        if success == 1:
            # Enter debug by sending break and resetting MCU
            ser.break_condition = True;
            user = input('Please reset MCU and press any key')
            ser.break_condition = False;
            ser.reset_input_buffer()
            success = 1
            '''
            # Enter debug by setting register
            command = zilog_ocd.ocd_enter_debug()
            ser.write(command)
            serial_data = ser.read(3)     # Dummy read
            '''
            
        # Read OCD Revision
        if success == 1:        
            command = zilog_ocd.ocd_read_revision()
            ser.write(command)
            serial_data = ser.read(4)
            serial_data = binascii.hexlify(serial_data)
            if b'800001' in serial_data:
                print('OCD revision: OK')
                success = 1
            else:
                print('OCD revision: Error')
                print(serial_data)
                success = 0
        
        # Checks if is in Debug mode
        if success == 1:
            command = zilog_ocd.ocd_read_debug()
            ser.write(command)
            serial_data = ser.read(3)
            value = serial_data[2]        # Pega o terceiro byte da sequ�ncia, que cont�m o valor do registrador           
            if value & 0x80 == 0x80:  # Verifica se bit correspondente ao modo debug est� setado
                print('Debug mode: OK')
                success = 1
            else:
                print('Debug mode: Error')
                print(binascii.hexlify(serial_data))
                success = 0      

        # Write Flash Programming Frequency register
        if success == 1:
            command = zilog_ocd.ocd_write_flash_freq_reg(clock)
            ser.write(command)
            serial_data = ser.read(7)     # Dummy read
            print('Flash Programming Frequency: OK')
            success = 1
                              
        # Flash unlock
        if success == 1:
            command = zilog_ocd.ocd_unlock_flash_1()
            ser.write(command)
            serial_data = ser.read(6)     # Dummy read
            command = zilog_ocd.ocd_unlock_flash_2()
            ser.write(command)
            serial_data = ser.read(6)     # Dummy read
            command = zilog_ocd.ocd_read_flash_stat()
            ser.write(command)
            serial_data = ser.read(6)
            value = serial_data[5]        # The sixth byte contains the value of the register         
            if value & 0x3F == 0x03:    # Check if flash is unlocked
                print('Flash unlock: OK')
                success = 1
            else:
                print('Flash unlock Error')
                print(binascii.hexlify(serial_data))
                success = 0
        
        # Flash mass erase
        if success == 1:
            command = zilog_ocd.ocd_mass_erase_flash()
            ser.write(command)
            serial_data = ser.read(6)     # Dummy read
            success = 0
            while (success == 0):
                command = zilog_ocd.ocd_read_flash_stat()
                ser.write(command)
                serial_data = ser.read(6)
                value = serial_data[5]        # The sixth byte contains the value of the register         
                if value & 0x38 == 0x00:    # Check if mass erase operation has finished
                    print('Flash mass erase: OK')
                    success = 1
                else:
                    print('Verifying Flash status...')
                    time.sleep(0.5)
             
        # Flash unlock
        if success == 1:
            command = zilog_ocd.ocd_unlock_flash_1()
            ser.write(command)
            serial_data = ser.read(6)     # Dummy read
            command = zilog_ocd.ocd_unlock_flash_2()
            ser.write(command)
            serial_data = ser.read(6)     # Dummy read
            command = zilog_ocd.ocd_read_flash_stat()
            ser.write(command)
            serial_data = ser.read(6)
            value = serial_data[5]        # The sixth byte contains the value of the register         
            if value & 0x3F == 0x03:    # Check if flash is unlocked
                print('Flash unlock: OK')
                success = 1
            else:
                print('Flash unlock Error')
                print(binascii.hexlify(serial_data))
                success = 0

        # Flash programming
        if success == 1:
            print("Programming Flash...")
            command = zilog_ocd.ocd_write_flash(output_file, 0, fw_size)
            ser.write(command)  
            time.sleep(2)         
            ser.reset_input_buffer()
            print('Flash programming: OK')
            success = 1
     
        # Checks CRC
        if success == 1:
            print('Checking CRC...')
            command = zilog_ocd.ocd_read_crc()
            ser.write(command)
            serial_data = ser.read(2)
            crc_read = ser.read(2)
            crc_read = int.from_bytes(crc_read, byteorder='big')    # CRC is sent by the MCU as big endian  
            crc_file = calculate_bin_crc(output_file)
            print('CRC from MCU: ' + str(crc_read))          
            print('CRC from file: ' + str(crc_file))
            if (crc_read == crc_file):
                print ('Flash successfully programmed!!')
                success = 1
            else:
                print ('Operation unsuccessful...')
     
        # Flash verify
        if success == 0:   # Only reads Flash memory if CRC is invalid  
            addr = 0
            bytes_to_read = 2   # Data from program memory has to be read only 2 bytes at once. 
            print("Verifying Flash...")
            while addr < fw_size:
                command = zilog_ocd.ocd_read_flash(addr, bytes_to_read)
                ser.write(command)
                ser.read(6)
                serial_data = ser.read(bytes_to_read)
                mcu_data_file.write(serial_data)
                addr += bytes_to_read
                
            # Checks if sent data is the same as read data
            output_file.seek(0)
            output_file_data = output_file.read()  
            mcu_data_file.seek(0)
            mcu_data_file_data = mcu_data_file.read()     
            if output_file_data == mcu_data_file_data:     
                success = 1  
                print('Success!')
            else:
                print('Error')
        
                    
if __name__ == "__main__":
    main()    