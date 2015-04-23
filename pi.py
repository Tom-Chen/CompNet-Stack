from Libraries import morse, utilities, CN_Sockets, gpio
import queue, threading
import socketsbase as sb


class Pi(object):
    
    def __init__(self,verbose=True):
        self.verbose = verbose
        self.UDP_Server_Address = ('localhost', 5281)
        self.recvqueue = queue.Queue()
        self.sendqueue = queue.Queue()
        self.transmitEvent = threading.Event()
        self.sock = sb.CN_Socket(2,2)
        self.recv_thread = threading.Thread(target=self._internalRecv)
        self.send_Thread = threading.Thread(target = morse.send,args = (self.sendqueue,self.transmitEvent,17))
        self.listen_Thread = threading.Thread(target = self.listen_local)
        
        self.transmitEvent.set()
        self.sock.bind(self.UDP_Server_Address)
        self.send_Thread.start()
        self.listen_Thread.start()
        morse.Receive(self.recvqueue.put,self.transmitEvent,23)
        self.recv_thread.start()

    def input_host(self):
        host = ""
        while not utilities.checkHost(host):
            host = input("Enter host (A through C):\n").upper()
        return host
        
    def _internalRecv(self):
        while True:
            data, addr = self.sock.recvfrom(8192)
            decoded_msg = data.decode("UTF-8")
            print(decoded_msg)
            self.sendqueue.put(decoded_msg)
            
    def listen_local(self):
        self.self_map = ("B",self.input_host())
        if self.verbose: print("Local listening thread started.")
        while True:
            packet = morse.reverse_translate(self.recvqueue.get())
            if self.verbose: print("Received packet: " +  packet)
            if len(packet) >= 14: # MAC + 13 characters for the header
                routeMAC = packet[0]
                if self.validate_datalayer(routeMAC):
                    if self.validate_chksum(packet[1:10]): # is the checksum valid?
                        dest_lan = packet[2]
                        dest_host = packet[3]
                        if self.validate_udplayer(dest_lan, dest_host): # check destination host and LAN
                            # if self.verbose: print("Should send the packet up the stack") # do something else here
                            bytearray_msg = packet[1:].encode("UTF-8") # drop the mac
                            self.sock.sendto(bytearray_msg, self.UDP_Server_Address)
                        else:
                            if self.verbose: print("Packet has a different destination LAN and host. Discarding packet.")
                    else:
                        if self.verbose: print("Invalid packet checksum. Discarding packet.")
                else:
                    if self.verbose: print("Packet has a different local MAC address. Discarding packet.")
            else:
                if self.verbose: print("Incomplete packet.")
        
    def validate_chksum(self,chksum):
        return utilities.testIPv4chksum(chksum)

    def validate_datalayer(self,mac):
        return mac == self.self_map[1]
        
    def validate_udplayer(self,lan,host):
        return (lan == self.self_map[0] and host == self.self_map[1])

if __name__ == "__main__":
    Pi()