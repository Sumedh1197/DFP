'''
Function returns the os_name of the current operating system 
'''
import platform

def returnOS():
    os_name = platform.system()
    return os_name
