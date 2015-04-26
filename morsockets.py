'''
morsockets.py
------------
A set of classes to implement basic socket functionality
for the CN-Internet.
The morsocketclient is a socket clone for use by applications.
It should operate as normal sockets would, such that the
application cannot distinguish it from sockets, except for
the import command. Additionally, many applications, each
using morsocketclient, should be able to run simultaneously.
Underlying the morsocketclient is a seperate, singleton process
running the morsocketserver on top of the morse stack (layers 1-4).
morsocketclient and morsocketserver manage cross-process communication
via the normal sockets library.
'''


# ----- IMPORTS ------ #
import socketsbase as sb
import queue
import threading
from interfaces import StackLayer
from Libraries import morse, utilities

# Move constants to this namespace
AF_INET = sb.AF_INET
SOCK_DGRAM = sb.SOCK_DGRAM
SOCK_STREAM = sb.SOCK_STREAM

# Internal Constants
_MORSOCK_SERVER_ADDR = ('localhost', 5280)  # Default address of the morstack server
UDP_Server_Address = ('localhost', 5281)
_PORT_CAP = 100  # Number of morse ports to make available

class socket(sb.socketbase):
    """
    Serves as a sockets-conforming interface for use by the
    application layer. Implements bind, recvfrom, and sendto
    as expected of a normal socket, but forwards method calls
    to the morse-stack via RPC.
    """

    def __init__(self, network_protocol=AF_INET, transport_protocol=SOCK_DGRAM):
        self.msg_queue = queue.Queue()
        self.CMD_MAP = {
            "exception" : self._raiseException,
            "message" : self._enqueueMessage
        }
        
        super().__init__(network_protocol, transport_protocol) 
        
        self.sock = sb.CN_Socket(2, 2)
        self.running = threading.Event()
        self.running.set()
        self.recv_thread = threading.Thread(target=self._internalRecv,args = (self.running, ))
        self.recv_thread.daemon = True
        self.recv_thread.start()
        
        # Register this process with the morsockserver
        self._sendCmd("register")
        
    def _internalRecv(self,running_event):
        while running_event.isSet():
            data, addr = self.sock.recvfrom(8192)
            data = utilities.deserialize(data)
            data['params']['addr'] = addr
            self.CMD_MAP[data["instruction"]](**data["params"])
            
    def _sendCmd(self, instruction, params={}):
        serialized = utilities.serialize(instruction, params)
        self.sock.sendto(serialized, _MORSOCK_SERVER_ADDR)
            
    def _enqueueMessage(self, message, dest_addr, addr):
        self.msg_queue.put((message[13:], addr))
        
    def _raiseException(self, desc):
        raise Exception(desc)
        
    def bind(self, addr):
        self._sendCmd("bind", {"request_addr": addr})
        
    def close(self):
        self._sendCmd("close")
        self.sock.close()
        print("Socket closing.")
        self.running.clear()
        return
        
    def sendto(self, message, dest_address):
        #print(message, dest_address)
        self._sendCmd("sendto", {
                "message": utilities.forcedecode(message),
                "dest_addr": dest_address
            })

    def recvfrom (self, bufsize):
        if self.timeout > 0:
            try:
                return self.msg_queue.get(True, self.timeout)
            except queue.Empty:
                raise TimeoutException("Socket recvfrom operation timed out.")
        else:
            return self.msg_queue.get(True,None)
            
    def __exit__ (self, argException, argString, argTraceback):
        self.close()
        self.sock.close()
        super().__exit__(argException, argString, argTraceback)
        
    
class TimeoutException(Exception):
    def __init__(self,arg):
        #print(arg)
        pass
        
class socketserver(StackLayer):
    
    def __init__(self, addr=_MORSOCK_SERVER_ADDR, verbose=True):
        self.verbose = verbose
        self.port_map = {}
        self.port_counter = 0
        self.local_lan = input("Enter LAN (A through D):\n").upper() 
        self.local_host = input("Enter Host (A through C or R):\n")
        print("Running...")
        self.CMD_MAP = {
            "sendto" : self.passDirection,
            "bind" : self.bind,
            "register" : self.register,
            "close" : self.close
        }
        
        with sb.CN_Socket(2, 2) as self.sock:
            self.sock.bind(addr)          
            while True:
                data, addr = self.sock.recvfrom(8192)
                cmd_obj = utilities.deserialize(data)
                #if self.verbose: print("Packet received from", addr)
                cmd_obj['params']['addr'] = addr
                if self.verbose: print("Received the command {} from {}".format(data, addr))
                self.CMD_MAP[cmd_obj['instruction']](**cmd_obj['params'])
                
        self.sock.close()

    def passDirection(self, message, addr, dest_addr):
        if(addr[1] == 5281):
            self.passUp(message, addr, dest_addr)
        else:
            self.passDown(message, addr, dest_addr)

    def passUp(self, message, addr, dest_addr):
        dest_port = int(dest_addr[1])
        if dest_port not in self.port_map.values():
            print("Destination port not found.")
            exception = "Port not found"
        else:
            reverseMap = {v: k for k, v in self.port_map.items()}
            morse_port = reverseMap[dest_port]
            self.sock.sendto(utilities.serialize("message", {
                "message": message,
                "dest_addr": ('localhost', morse_port)
            }), ('localhost', reverseMap[dest_port]))
            if self.verbose: print("Packet {} sent to localhost {}".format(message,morse_port))
        
    def passDown(self, message, addr, dest_addr):
        dest_addr = utilities._ipv42morse(dest_addr)
        if self.verbose: print("Destination Address: ", dest_addr)
        source_port = str(self.port_map[addr[1]])
        if len(source_port) == 1:
            source_port = "0" + source_port
        packed = morse.package_message(self.local_lan, self.local_host, dest_addr[0], dest_addr[1], "1", source_port, dest_addr[2], message)
        if self.verbose: print("Packet: " + packed)
        packed = bytearray(packed,encoding="UTF-8")
        self.sock.sendto(packed, UDP_Server_Address)
    
    def bind(self, request_addr, addr):
        
        if request_addr in self.port_map.values():
            print("Port in use.")
            exception = "Port in use"
        elif request_addr[1] > _PORT_CAP:
            print("Port number out of range. Ports numbers must be >0 and <{}".format(_PORT_CAP))
            exception = "Port number out of range. Ports numbers must be >0 and <{}".format(_PORT_CAP)
        else:
            del self.port_map[addr[1]]  # Clear old port reservation
            self.port_map[addr[1]] = request_addr[1]  # Reserve new port
            if self.verbose: print("Process on OS port {} bound to morse port {}".format(addr[1], request_addr[1]))
            return
        
        self.sendException(exception, addr)
            
    
    def register(self, addr):
        """
        Assign a morse port to a process when it starts up. The ports
        are assigned from 0 to _PORT_CAP and will find an available port
        if available. If a port is not available, it will return a serialized
        exception to the morstackclient.
        """
        
        for i in range(self.port_counter, self.port_counter + _PORT_CAP):
            port = i % _PORT_CAP
            
            # If an available port if found, adjust the port_counter for
            # future searches, and register the process to the port
            if port not in self.port_map:
                self.port_counter = port + 1
                self.port_map[addr[1]] = port
                #if self.verbose:
                print("New process registered on OS port {} bound to morse port {}".format(addr[1], port))
                return
        
        # If no ports are available, forward an exception to the requesting client
        self.sendException("No ports available", addr)
        
    def close(self, addr):
        del self.port_map[addr[1]]  # Close port reservation
    
    def sendException(self, desc, addr):
        self.sock.sendto(utilities.serialize("exception", {"desc": desc}), addr)

    
    
# ----- TESTING CODE ----- #
if __name__ == "__main__":
    socketserver()