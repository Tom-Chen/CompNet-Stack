from Libraries import utilities, CN_Sockets
from Constants import a_local, b_local
import queue, threading
import socketsbase as sb
UDP_Server_Address = ('localhost', 5281)

class UDP_Pi_Receiver(object):
    
    def __init__(self):
        self.local_map = a_local.map
        self.input_host = "A"
        self.input_lan = "A"
        self.sock = sb.CN_Socket(2,2)
        self.sock.bind(UDP_Server_Address)
        self.recv_thread = threading.Thread(target=self._internalRecv)
        self.recv_thread.start()
        self.self_map = (self.input_lan, self.input_host)
        
        print ("UDP_Pi receiving client started.")
        
        recvqueue = queue.Queue()
        sendqueue = queue.Queue()
        transmitEvent = threading.Event()
        # morse.receive(recvqueue.put,transmitEvent,23)
        # self.send_Thread = threading.Thread(target = morse.send,args = (sendqueue,transmitEvent,17))
        # listen_local()

    def _internalRecv(self):
        while True:
            data, addr = self.sock.recvfrom(8192)
            data = deserialize(data)
            console.log(data)

    def listen_local(self):
        #should this be on a constant basis or should we just call it when we have a packet?
        while True:
            packet = morse.reverse_translate(recvqueue.get())
            # experimental handling logic
            if len(packet) >= 12: # 10 characters for the header, one space, and then content
                if validate_chksum(packet[0:10]): # is the checksum valid?
                    routeMAC = packet[0]
                    dest_lan = packet[2]
                    dest_host = packet[3]
                    if validate_datalayer(routeMAC): # check the mac
                        if validate_udplayer(dest_lan, dest_host): # check destination host and LAN
                            print(packet)
                        else:
                            print("Packet has a different destination lan and host.")
                    else:
                        print("Packet has a different local MAC address.")
                else:
                    print("Invalid packet checksum.")
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
    UDP_Pi_Receiver()