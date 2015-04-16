
import RPC # RPC adds ability to interrupt "while True" loop with ctl-C
    

            
class UDP_TX(object):
    """ Computer Networks Lab 4: Introduction to Sockets.  UDP Transmit example.
This code only transmits a udp message to a known IP_address ("127.0.0.1") and port_number (5280)
The UDP_RX module recieves and prints messages it is sent.
In this example, the UDP_TX process is the client, because the port number of the server (5280) is known to it.
The server, runing UDP_RX, determines the client's port number from each message it receives.
"""
    
    
    def __init__(self,Server_Address=("192.168.66.65",2048)):

        socket, AF_INET, SOCK_DGRAM = RPC.socket, RPC.AF_INET, RPC.SOCK_DGRAM
        # socket = RPC.socket, which is socket.socket with a slignt modification to allow you to use ctl-c to terminate a test safely
        # RPC.AF_INET is the constant 2, indicating that the address is in IPv4 format
        # RPC.SOCK_DGRAM is the constant 2, indicating that the programmer intends to use the Universal Datagram Protocol of the Transport Layer

        with socket(AF_INET,SOCK_DGRAM) as sock:  # open the socket
          
            
            print ("UDP_TX client started for UDP_Server at IP address {} on port {}".format(
                Server_Address[0],Server_Address[1])
                   )

    
            while True:
                
                str_message = input("Enter message to send to server:\n")

                if not str_message: # an return with no characters terminates the loop
                    break
                
                bytearray_message = bytearray(str_message,encoding="UTF-8") # note that sockets can only send 8-bit bytes.
                                                                            # Since Python 3 uses the Unicode character set,
                                                                            # we have to specify this to convert the message typed in by the user
                                                                            # (str_message) to 8-bit ascii 

                bytes_sent = sock.sendto(bytearray_message, Server_Address) # this is the command to send the bytes in bytearray to the server at "Server_Address"
                
                print ("{} bytes sent".format(bytes_sent)) #sock_sendto returns number of bytes send.

        print ("UDP_Client ended")

    


if __name__ == "__main__":
    UDP_TX()
               
    
                
                
                
            



            
        
