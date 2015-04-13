from Libraries import morse, utilities, CN_Sockets
from Constants import a_local, b_local
import queue, threading
import socketsbase as sb
UDP_Server_Address = ('localhost', 5281)

class UDP_Pi(object):
    
    def __init__(self):
        self.self_map = (input_lan, input_host)
        self.local_map, input_host
        self.sock = sb.CN_Socket(2,2)
        self.sock.bind(UDP_Server_Address)
        self.recv_thread = threading.Thread(target=self._internalRecv)
        self.recv_thread.start()

        while not self.local_map:
            input_lan = input("Enter LAN (A or B):\n").upper() 
            if input_lan == "A":
                self.local_map = a_local.map
            elif input_lan == "B":
                self.local_map = b_local.map
            else:
                print("Invalid LAN.")
        while(input_host not in self.local_map):
            input_host = input("Enter Host (A or B):\n").upper()
            if input_host not in self.local_map or input_host == "R":
                print("Invalid Host")
        
        print ("UDP_Pi receiving client started.")
        
        recvqueue = queue.Queue()
        sendqueue = queue.Queue() # finished messages
        # packqueue = queue.Queue() # messages that need to be packaged
        transmitEvent = threading.Event()
        transmitEvent.set()
        morse.receive(recvqueue.put,transmitEvent,23)
        self.send_Thread = threading.Thread(target = morse.send,args = (sendqueue,transmitEvent,17))
        self.listen_Thread = threading.Thread(target = listen_local)
        self.send_Thread.start()
        self.listen_Thread = start()

    def _internalRecv(self):
        while True:
            data, addr = self.sock.recvfrom(8192)
            data = deserialize(data)
            print(data)
            

    # def send_local(self):
        # print("Sending thread started.")
        # while True:
            # print("Waiting for a message...")
            # [message,dest_ip,dest_port] = packqueue.get()
            
            
    def listen_local(self):
        #should this be on a constant basis or should we just call it when we have a packet?
        print("Local listening thread started.")
        while True:
            packet = morse.reverse_translate(recvqueue.get())
            if len(packet) >= 14: # MAC + 13 characters for the header
                routeMAC = packet[0]
                if validate_datalayer(routeMAC):
                    if validate_chksum(packet[1:10]): # is the checksum valid?
                        dest_lan = packet[2]
                        dest_host = packet[3]
                        if validate_udplayer(dest_lan, dest_host): # check destination host and LAN
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