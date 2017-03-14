# -*- coding: utf-8 -*-
import os, sys
import binascii
        
def ocd_read_revision ():
    # Read Revision 00h
    command = binascii.unhexlify("8000FFFF")
    return command
    
def ocd_enter_debug ():
    # Write OCD Control Register 04h
    command = binascii.unhexlify("800480")
    return command
    
def ocd_read_debug ():
    # Read OCD Control Register 05h
    command = binascii.unhexlify("8005FF")
    return command    
    
def ocd_read_status ():
    # Read OCD Status Register 02h
    command = binascii.unhexlify("8002FF")
    return command    
        
def ocd_write_flash_freq_reg(freq = 11059200):
    # Write Register 08h 
    # FFREQ - 0x0FFA
    regvalue = freq // 1000;    # Integer division of freq by 1000
    command = binascii.unhexlify("80080FFA02")
    command += regvalue.to_bytes(2, 'big')    
    return command
    
def ocd_unlock_flash_1():
    # Write Register 08h 
    # FCTL - 0x0FF8
    command = binascii.unhexlify("80080FF80173")
    return command
    
def ocd_unlock_flash_2():
    # Write Register 08h 
    # FCTL - 0x0FF8
    command = binascii.unhexlify("80080FF8018C")
    return command    
 
def ocd_mass_erase_flash():
    # Write Register 08h 
    command = binascii.unhexlify("80080FF80163")
    return command
    
def ocd_read_flash_stat():
    # Read Register 09h 
    # FSTAT - 0x0FF8
    command = binascii.unhexlify("80090FF801FF")
    return command
    
def ocd_write_flash(file, init_address = 0, size = 24576):
    # Write Program Memory 0Ah   
        
    file.seek(0)
    file_data = file.read()
    
    command = binascii.unhexlify("800A")   
    command += init_address.to_bytes(2, 'big')
    command += size.to_bytes(2, 'big')
    command += file_data   
    
    return command
    
    
def ocd_read_flash(init_address = 0, size = 4096):
    # Read Program Memory 0Bh   
           
    command = binascii.unhexlify("800B")   
    command += init_address.to_bytes(2, 'big')
    command += size.to_bytes(2, 'big')   
    command += bytes([0xFF] * size)     # Append 'size' bytes with 0xFF value 
    
    return command    
    
def ocd_read_crc():
    # Read Program Memory CRC 0Eh 
    command = binascii.unhexlify("800E") 
    
    return command
    
if __name__ == "__main__":
    print(" This is a library, not a standalone program.")
    