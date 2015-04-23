import CN_Sockets, sys

class HangmanClient(object):
    
    def __init__(self):
        self.server_addr = ('localhost',99)
        self.client_addr = ('localhost',98)
        self.sock = CN_Sockets.socket(2,2)
        self.sock.settimeout(20.0)
        self.sock.bind(self.client_addr)
        
        while True:
            try:
                str_message = input("Enter guess:\n").upper()
                if not str_message:
                    continue
                bytearray_message = bytearray(str_message,encoding="UTF-8")
                self.sock.sendto(bytearray_message, self.server_addr)
                
                print("Waiting for a response...")
                bytearray_reply, source_address = self.sock.recvfrom(8192)
                reply = (bytearray_reply.decode("UTF-8"))
                
                if reply[0:15] == "Congratulations":
                    print(reply)
                    self.sock.close()
                    sys.exit()
                elif  reply[0:9] == "Game over":
                    print(reply)
                    self.sock.close()
                    sys.exit()
                else:
                    print(reply)
            except CN_Sockets.timeout:
                print("Server timed out.")
          
                    
if __name__ == "__main__":
    HangmanClient()




    
                
                
                
            



            
        
