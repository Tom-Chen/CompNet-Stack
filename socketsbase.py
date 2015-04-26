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
from Libraries import utilities
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
    ipv4 = utilities._morse2ipv4(test_morse_ip)

    print("Morse IP is '" + test_morse_ip + "'")
    print("The corresponding ipv4 address is: " + ipv4)
    print("And the retranslation to morse is: ", utilities._ipv42morse((ipv4,99)))