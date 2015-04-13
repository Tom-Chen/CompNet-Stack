from Libraries import morse, utilities, CN_Sockets
from Constants import a_local, b_local, routers
import queue, threading
from UDP_Pi import UDP_Pi 

class UDP_Router(UDP_Pi):

    def __init__(self): # Router for Network A

#        self.self_map = (input_lan, "R")
#        self.local_map
#        while not self.local_map:
#            input_lan = input("Enter LAN (A or B):\n").upper() 
#            if input_lan == "A":
#                self.local_map = a_local.map
#           elif input_lan == "B":
#                self.local_map = b_local.map
#            else:
#                print("Invalid LAN.")

        self.self_map = ("A", "R")
        self.local_map = a_local.map
 
        socket, AF_INET, SOCK_DGRAM, timeout = CN_Sockets.socket, CN_Sockets.AF_INET, CN_Sockets.SOCK_DGRAM, CN_Sockets.timeout
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(self.local_map["R"]) # changed to pi IP address and port 2048
        
        print ("UDP router started.")
        
        self.recvqueue = queue.Queue()
        self.sendqueue = queue.Queue()
        self.transmitEvent = threading.Event()
        self.transmitEvent.set()
        morse.Receive(self.recvqueue.put,self.transmitEvent,23)
        self.send_Thread = threading.Thread(target = morse.send,args = (self.sendqueue,self.transmitEvent,17))
        self.routing_Thread = threading.Thread(target = self.route_packets,args=(self.sock,))
        self.listen_Thread = threading.Thread(target = self.listen_local,args=(self.sock,))
        self.send_Thread.start()
        self.routing_Thread.start()
        self.listen_Thread.start()

    def listen_local(self,sock):
        print("Local listening thread started.")
        while True:
            translated_packet = morse.reverse_translate(self.recvqueue.get())
            # experimental handling logic
            if len(translated_packet) >= 14: # MAC + 13 characters for header
                routeMAC = translated_packet[0]
                if self.validate_datalayer(routeMAC): 
                    if self.validate_chksum(translated_packet[1:10]): # is the IP layer checksum valid?
                        dest_lan = translated_packet[2]
                        dest_host = translated_packet[3]
                        # check the mac (router version)
                        if (dest_lan == self.self_map[0] and dest_host != "R"): # match lan but not mac
                            new_packet = dest_host+translated_packet[1:3]+translated_packet[4:] # change target MAC
                            self.sendqueue.put(new_packet) # route directly to correct host
                        elif dest_lan != self.self_map[0] and dest_lan in routers.map: # different LAN
                            bytearray_msg = translated_packet[1:].encode("UTF-8") # drop the MAC since we're sending it over ethernet
                            sock.sendto(bytearray_msg,routers.map[dest_lan])
                        else:
                            print("Router as final destination host or invalid LAN. Discarding packet.")
                    else:
                        print("Invalid packet checksum. Discarding packet.")
                else:
                    print("Packet has a different local MAC address. Discarding packet.")

            else:
                print("Incomplete packet.")
                
    
    def route_packets(self,sock):
        print("Packet routing thread started.")
        while True:
            bytearray_msg, source_address = sock.recvfrom(1024)
            source_IP, source_port = source_address
            print ("\nMessage received from ip address {}, port {}:".format(source_IP,source_port))
##            print (bytearray_msg.decode("UTF-8"))
##            morse_tuples = ast.literal_eval(bytearray_msg.decode("UTF-8"))
##            translated_packet = morse.reverse_translate(morse_tuples)
            translated_packet = bytearray_msg.decode("UTF-8")
            if len(translated_packet) >= 13: # 13 characters for the header 
                if utilities.testIPv4chksum(translated_packet[0:9]):
                    dest_lan = translated_packet[2]
                    dest_host = translated_packet[3]
                    print ("Destination LAN: {}, Destination Host: {}".format(dest_lan,dest_host))
                    
                    if dest_lan == self.self_map[0] and dest_host != "R": # is it on our LAN? also make sure we don't loop packets forever
                        if dest_host in self.local_map: # just send it directly
                            sendqueue.put(dest_host+translate_packet) # add the MAC since we're sending over LAN
                        else:
                            print("Host name not found on this LAN. Discarding packet.") # On our LAN, but not in the local map
                    elif dest_host != "R": # make sure we don't loop packets forever
                        if dest_lan in routers.map:
                            print("Routing packet.")
                            sock.sendto(bytearray_msg, routers.map[dest_lan]) # punt it off to the right router
                        else:
                            print("Received packet with unknown destination LAN. Discarding packet.")
                    else:
                        print("Packet sent with router as destination host. Discarding packet.")
                else:
                    print("Incorrect packet checksum. Discarding packet.")
            else:
                  print("Incomplete packet. Discarding packet.")

if __name__ == "__main__":
    UDP_Router()
