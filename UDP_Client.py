from Libraries import morse, CN_Sockets, utilities
from Constants import a_local, b_local
import ast

class UDP_Client(object):
    
    def __init__(self):
        input_lan = input("Enter LAN (A or B):\n").upper()
        input_host = input("Enter Host (A or B):\n").upper()
        Self_Map = (input_lan, input_host)
        Local_Map, input_host
        while(!Local_Map):
            input_lan = input("Enter LAN (A or B):\n").upper() 
            if input_lan == "A":
                Local_Map = a_local.map
            elif input_lan == "B":
                Local_Map = b_local.map
            else:
                print("Invalid LAN.")
        while(input_host not in Local_Map):
            input_host = input("Enter Host (A, B, or R for router):\n").upper()
            if input_host not in Local_Map:
                print("Invalid Host")
            
        socket, AF_INET, SOCK_DGRAM, timeout = CN_Sockets.socket, CN_Sockets.AF_INET, CN_Sockets.SOCK_DGRAM, CN_Sockets.timeout
        
        with socket(AF_INET,SOCK_DGRAM) as sock:  # open the socket
            sock.bind(Local_Map[input_host])
            sock.settimeout(2.0)
            
            print ("UDP_Pi client started.")
            
            while True:
                try:
                    print("Open to messages...")
                    bytearray_msg, source_address = sock.recvfrom(1024)
                    source_IP, source_port = source_address
                    
                    print ("\nMessage received from ip address {}, port {}:".format(source_IP,source_port))
                    str_received = morse.reverse_translate(ast.literal_eval(bytearray_msg.decode("UTF-8")))
                    print (str_received)
                    if utilities.testIPv4chksum(str_received[0:9]):
                        print("Packet checksum verified.")
                    else:
                        print("Wrong packet checksum. Contents may be incorrect.")
                    
                except timeout:
                    print("Timed out, press enter to open message receiving")
                    dest_lan = input("Enter destination LAN:\n").upper()
                    if not (utilities.checkLetter(dest_lan)):
                        print("Invalid LAN")
                        continue
                    dest_host = input("Enter destination Host:\n").upper()
                    if not (utilities.checkLetter(dest_host)):
                        print("Invalid Host")
                        continue
                    if dest_host.upper() == "R":
                        print("Please do not send directly to router")
                        continue
                    str_message = input("Enter message to send:\n").upper()
                    str_message = str(morse.package_message(input_lan, input_host, dest_lan, dest_host, "1", str_message))
                    # print(str_message)
                    if not str_message: # an return with no characters terminates the loop
                        print("No message.")
                        continue
                    
                    bytearray_message = bytearray(str_message,encoding="UTF-8")

                    if dest_lan == input_lan: # is it on our LAN?
                        if dest_host in Local_Map: # just send it directly
                            sock.sendto(bytearray_message, Local_Map[dest_host])
                        else:
                            print("Host name not found on this LAN") # On our LAN, but not in the local map
                    else:
                        print("This packet needs to be routed")
                        sock.sendto(bytearray_message, Local_Map["R"])

        print ("UDP_Client ended")

    


if __name__ == "__main__":
    UDP_Client()
