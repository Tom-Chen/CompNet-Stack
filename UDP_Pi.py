from Libraries import morse, utilities, CN_Sockets
import queue, threading
import socketsbase as sb
UDP_Server_Address = ('localhost', 5281)

class UDP_Pi(object):
    
    def __init__(self):
##        self.local_map, input_host
##        while not self.local_map:
##            input_lan = input("Enter LAN (A or B):\n").upper() 
##            if input_lan == "A":
##                self.local_map = a_local.map
##            elif input_lan == "B":
##                self.local_map = b_local.map
##            else:
##                print("Invalid LAN.")
##        while(input_host not in self.local_map):
##            input_host = input("Enter Host (A or B):\n").upper()
##            if input_host not in self.local_map or input_host == "R":
##                print("Invalid Host")

        # self.local_map = a_local.map
        
        self.self_map = ("B","A")
        self.sock = sb.CN_Socket(2,2)
        self.sock.bind(UDP_Server_Address)
        self.recv_thread = threading.Thread(target=self._internalRecv)
        self.recv_thread.start()


        
        print ("UDP_Pi receiving client started.")
        
        self.recvqueue = queue.Queue()
        self.sendqueue = queue.Queue() # finished messages
        # packqueue = queue.Queue() # messages that need to be packaged
        self.transmitEvent = threading.Event()
        self.transmitEvent.set()
        morse.Receive(self.recvqueue.put,self.transmitEvent,23)
        self.send_Thread = threading.Thread(target = morse.send,args = (self.sendqueue,self.transmitEvent,17))
        self.listen_Thread = threading.Thread(target = self.listen_local)
        self.send_Thread.start()
        self.listen_Thread.start()

    def _internalRecv(self):
        while True:
            data, addr = self.sock.recvfrom(8192)
            decoded_msg = data.decode("UTF-8")
            print(decoded_msg)
            self.sendqueue.put(decoded_msg)
            
    def listen_local(self):
        #should this be on a constant basis or should we just call it when we have a packet?
        print("Local listening thread started.")
        while True:
            packet = morse.reverse_translate(self.recvqueue.get())
            print("Received packet: " +  packet)
            if len(packet) >= 14: # MAC + 13 characters for the header
                routeMAC = packet[0]
                if self.validate_datalayer(routeMAC):
                    if self.validate_chksum(packet[1:10]): # is the checksum valid?
                        dest_lan = packet[2]
                        dest_host = packet[3]
                        if self.validate_udplayer(dest_lan, dest_host): # check destination host and LAN
                            print(packet) # do something else here
                        else:
                            print("Packet has a different destination LAN and host. Discarding packet.")
                    else:
                        print("Invalid packet checksum. Discarding packet.")
                else:
                    print("Packet has a different local MAC address. Discarding packet.")
            else:
                print("Incomplete packet.")
        print ("UDP_Client ended")
        
    def validate_chksum(self,chksum):
        return utilities.testIPv4chksum(chksum)

    def validate_datalayer(self,mac):
        return mac == self.self_map[1]
        
    def validate_udplayer(self,lan,host):
        return (lan == self.self_map[0] and host == self.self_map[1])

    def serialize(instruction, parameters={}):
        return json.dumps(
            {"instruction": instruction,
             "params": parameters
            }).encode('utf-8')

    def deserialize(serialized):
        return json.loads(serialized.decode('utf-8'))

if __name__ == "__main__":
    UDP_Pi()
