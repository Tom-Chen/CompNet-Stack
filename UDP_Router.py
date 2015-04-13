from Libraries import morse, CN_Sockets, utilities
from Constants import a_local, b_local, routers
import queue, threading, ast
from UDP_Pi_Receiver import UDP_Pi_Receiver 

class UDP_Router(UDP_Pi):

    def __init__(self): # Router for Network A
        self.self_map = (input_lan, "R")
        self.local_map
        while not self.local_map:
            input_lan = input("Enter LAN (A or B):\n").upper() 
            if input_lan == "A":
                self.local_map = a_local.map
            elif input_lan == "B":
                self.local_map = b_local.map
            else:
                print("Invalid LAN.")
 
        socket, AF_INET, SOCK_DGRAM, timeout = CN_Sockets.socket, CN_Sockets.AF_INET, CN_Sockets.SOCK_DGRAM, CN_Sockets.timeout
        with socket(AF_INET, SOCK_DGRAM) as sock:
            sock.bind(Local_Map["R"])
            sock.settimeout(2.0)
            
            print ("UDP router started.")
            
            recvqueue = Queue.Queue()
            sendqueue = Queue.Queue()
            transmitEvent = threading.Event()
            transmitEvent.set()
            morse.receive(recvqueue.put,transmitEvent,23)
            self.send_Thread = threading.Thread(target = morse.send,args = (sendqueue,transmitEvent,17))
            self.routing_Thread = threading.Thread(target = route_packets)
            self.listen_Thread = threading.Thread(target = listen_local)
            self.send_Thread.start()
            self.routing_Thread.start()
            self.listen_Thread.start()

            def listen_local(self):
                print("Local listening thread started.")
                while True:
                    translated_packet = morse.reverse_translate(recvqueue.get())
                    # experimental handling logic
                    if len(translated_packet) >= 14: # MAC + 13 characters for header
                        routeMAC = translated_packet[0]
                        if validate_datalayer(routeMAC): 
                            if validate_chksum(translated_packet[1:10]): # is the IP layer checksum valid?
                                dest_lan = translated_packet[2]
                                dest_host = translated_packet[3]
                                # check the mac (router version)
                                    if dest_lan == self.self_map[0] and dest_host != "R": # match LAN but not MAC
                                        new_packet = dest_host+translated_packet[1:3]+translated_packet[4:] # change target MAC
                                        sendqueue.put(new_packet) # route directly to correct host
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
                        
            
            def route_packets(self):
                print("Packet routing thread started.")
                while True:
                    try:
                        bytearray_msg, source_address = sock.recvfrom(1024)
                        source_IP, source_port = source_address
                        print ("\nMessage received from ip address {}, port {}:".format(source_IP,source_port))
                        morse_tuples = ast.literal_eval(bytearray_msg.decode("UTF-8"))
                        translated_packet = morse.reverse_translate(morse_tuples)
                        if len(translated_packet) >= 13: # 13 characters for the header 
                            if utilities.testIPv4chksum(translated_packet[0:9]):
                                dest_lan = translated_packet[2]
                                dest_host = translated_packet[3]
                                print ("Destination LAN: {}, Destination Host: {}".format(dest_lan,dest_host))
                                
                                if dest_lan == input_lan and dest_host != "R": # is it on our LAN? also make sure we don't loop packets forever
                                    if dest_host in Local_Map: # just send it directly
                                        sendqueue.put(dest_host+translate_packet) # add the MAC since we're sending over LAN
                                    else:
                                        print("Host name not found on this LAN. Discarding packet.") # On our LAN, but not in the local map
                                elif dest_host != "R": # make sure we don't loop packets forever
                                    if dest_lan in routers.map:
                                        sock.sendto(bytearray_msg, routers.map[dest_lan]) # punt it off to the right router
                                    else:
                                        print("Received packet with unknown destination LAN. Discarding packet.")
                            else:
                                print("Incorrect packet checksum. Discarding packet.")
                                translated_packet = ""
                                bytearray_msg = ""
                          else:
                              print("Incomplete packet. Discarding packet.")
                    except timeout:
                        # print (".",end="",flush=True)  # if process times out, just print a "dot" and continue waiting.  The effect is to have the server print  a line of dots
                                                       # # so that you can see if it's still working.
                        continue  # go wait again

if __name__ == "__main__":
    UDP_router()