# -*- coding: utf-8 -*-
import os, sys
import binascii

def convert_intelhex_to_bin (filename, size, filepath):

    final_file = open(filepath,"w+b")  # cria o arquivo, com permissão de leitura e escrita   
    final_file.truncate(0)  
    final_file.write(bytes([0xFF] * size))     # Write 'size' bytes with 0xFF value
    final_file.seek(0)
    
    success = 0
    
    with open(filename) as file:
        for line in file:
            if (line[0] == ':' and line[8] == '0'):
                output = line[9:-3]
                print (output)
                output = binascii.unhexlify(output)
                final_file.write(output)
            if (line[0] == ':' and line[8] == '1'):
                success = 1
    
    file.close()
    
    if success == 1:
        return final_file
    else:
        return ''
        
if __name__ == "__main__":
    print(" This is a library, not a standalone program.")