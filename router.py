from Libraries import morse, utilities, CN_Sockets, gpio
from Constants import routers
import queue, threading
import socketsbase as sb
from pi import Pi

class Router(Pi):

    def __init__(self):

        Pi.__init__(self)
    
        self.self_map = ("B", "R")
        self.intersock = CN_Sockets.socket(2,2)
        self.intersock.bind(("192.168.128.108",2048)) # changed to pi IP address and port 2048
        self.routing_Thread = threading.Thread(target = self.route_packets)
        self.routing_Thread.start()
        self.sock.close() # router doesn't run internal morse server

    def listen_local(self):
        if self.verbose: print("Local listening thread (router edition) started.")
        while True:
            translated_packet = morse.reverse_translate(self.recvqueue.get())
            if self.verbose: print("Received local packet: " + translated_packet)
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
                            bytearray_msg = translated_packet[1:].encode("UTF-8") # drop the MAC
                            self.intersock.sendto(bytearray_msg,routers.map[dest_lan])
                        else:
                            if self.verbose: print("Router as final destination host or invalid LAN. Discarding packet.")
                    else:
                        if self.verbose: print("Invalid packet checksum. Discarding packet.")
                else:
                    if self.verbose: print("Packet has a different local MAC address. Discarding packet.")

            else:
                print("Incomplete packet.")
                
    
    def route_packets(self):
        print("Packet routing thread started.")
        while True:
            bytearray_msg, source_address = self.intersock.recvfrom(8192)
            source_IP, source_port = source_address
            translated_packet = bytearray_msg.decode("UTF-8")
            if self.verbose:
                print ("\nMessage received from ip address {}, port {}:".format(source_IP,source_port))
                print("Received internet packet: " + translated_packet)
            if len(translated_packet) >= 13: # 13 characters for the header 
                if utilities.testIPv4chksum(translated_packet[0:9]):
                    dest_lan = translated_packet[2]
                    dest_host = translated_packet[3]
                    if self.verbose: print ("Destination LAN: {}, Destination Host: {}".format(dest_lan,dest_host))
                    
                    if dest_lan == self.self_map[0] and dest_host != "R": # is it on our LAN? also make sure we don't loop packets forever
                        if dest_host in self.local_map: # just send it directly
                            sendqueue.put(dest_host+translate_packet) # add the MAC since we're sending over LAN
                        else:
                            if self.verbose: print("Host name not found on this LAN. Discarding packet.") # On our LAN, but not in the local map
                    elif dest_host != "R": # make sure we don't loop packets forever
                        if dest_lan in routers.map:
                            if self.verbose: print("Routing packet.")
                            self.intersock.sendto(bytearray_msg, routers.map[dest_lan]) # punt it off to the right router
                        else:
                            if self.verbose: print("Received packet with unknown destination LAN. Discarding packet.")
                    else:
                        if self.verbose: print("Packet sent with router as destination host. Discarding packet.")
                else:
                    if self.verbose: print("Incorrect packet checksum. Discarding packet.")
            else:
                  if self.verbose: print("Incomplete packet. Discarding packet.")

if __name__ == "__main__":
    Router()
