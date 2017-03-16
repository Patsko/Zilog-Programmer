# -*- coding: utf-8 -*-
import os, sys
import binascii


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

if __name__ == "__main__":
    print(" This is a library, not a standalone program.")  