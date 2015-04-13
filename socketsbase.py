"""
socketsbase.py
--------------
A base class to establish the standardized
sockets interface for all CNSP15 teams.
All publically defined methods are to be
implemented by the teams.
"""

# ----- IMPORTS ------ #
from abc import ABCMeta, abstractmethod
import socket


# ----- AVAILABLE CONSTANTS ----- #
# Network Protocol
AF_INET = 'E';       # IP

# Transport Layer Protocols
SOCK_DGRAM = 'A';   # UDP
SOCK_STREAM = 'B';  # TCP

# Default IP Fields
_DEF_IP = ['192', '168', '0', '0']


# ----- SOCKETS BASE CLASS ----- #
class socketbase:
    __metaclass__ = ABCMeta

    def __init__ (self, network_protocol=AF_INET, transport_protocol=SOCK_DGRAM):
        self.network_protocol = network_protocol
        self.transport_protocol = transport_protocol
        self.timeout = 0;
    
    def __enter__ (self):
        return self
        
    def __exit__ (self, argException, argString, argTraceback):
        # If your stack requires you to exit it gracefully, you
        # may want to override this method
        return False # Don't suppress exceptions, True suppresses

    @abstractmethod
    def bind (self, ip, port=80):
        raise NotImplementedError('bind() method is not yet implmented!')

    @abstractmethod
    def recvfrom (self, bufsize):
         raise NotImplementedError('recvfrom() method is not yet implmented!')

    @abstractmethod
    def sendto (self, message, address):
         raise NotImplementedError('sendto() method is not yet implmented!')

    def settimeout (self, timeout):
        if (timeout < 0): raise ValueError('timeout must be nonnegative!')
        self.timeout = timeout

    def gettimeout (self):
        return self.timeout


# ----- SOCKETS BASE UTILITY FUNCTIONS ----- #
def _morse2ipv4 (morse_ip):
    """
    Translates a morse IP address (eg. 'R0') to an ipv4 address according to
    the class agreement on ipv4 - morse mapping. The ipv4 address has its
    last two fields filled in by the ascii code corresponding to the respective
    characters of the ip address (eg. 'R' -> 82, '0' -> 48).
    ex. input = 'R0', output = '192.168.82.48'
    """

    ipv4 = _DEF_IP
    ipv4[2] = str(ord(morse_ip[0])) # Map Morse IP field to third ipv4 field
    ipv4[3] = str(ord(morse_ip[1])) # Map Morse MAC field to fourth ipv4 field
    return '.'.join(ipv4)


def _ipv42morse (ipv4):
    """
    Translates an IPV4 address (eg. '192.168.82.48') to a morse address according to
    the class agreement on ipv4 - morse mapping. The morse address is two chars long
    with the characters corresponding to the ascii characters mapped to the numeric
    ascii codes in the last two fields of the IPV4 address (eg. 82 -> 'R', 48 -> '0').
    ex. input = '192.168.82.48', output = 'R0'
    also handles ports
    """

    ipv4 = ipv4[0].replace(':','.').split('.')
    # print(ipv4)
    return [chr(int(ipv4[2])), chr(int(ipv4[3])), ipv4[4]]


# ----- SOCKETS CTRL-C EXTENSION ----- #
class CN_Socket(socket.socket):
    """
    CN_Socket subclasses standard Python 3 socket class 
    to add support for keyboard interrupt (ctl-C)
    
    Written by Alex Morrow, borrowed here
    """
    
    def __exit__(self, argException, argString, argTraceback):

        if argException is KeyboardInterrupt:
            print (argString)
            self.close()   # return socket resources on ctl-c keyboard interrupt
            return True
        
        else:  # invoke normal socket context manager __exit__
            super().__exit__(argException, argString, argTraceback)


# ----- TESTING CODE ----- #
if __name__ == "__main__":
    print("-- Morse to IP Test --" )

    test_morse_ip = 'R0'
    ipv4 = _morse2ipv4(test_morse_ip)

    print("Morse IP is '" + test_morse_ip + "'")
    print("The corresponding ipv4 address is: " + ipv4)
    print("And the retranslation to morse is: " + _ipv42morse(ipv4))