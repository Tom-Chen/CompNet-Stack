import morsockets as CN_Sockets, sys
from Libraries import utilities

class HangmanClient(object):
    
    def __init__(self):
        svr_ip = input("What's the server's IP?")
        svr_port = input("What's the server's port?")
        clt_ip = input("What's my IP?")
        clt_port = input("What's my port?")
        self.server_addr = (svr_ip,int(svr_port))
        self.client_addr = (clt_ip,int(clt_port))
        with CN_Sockets.socket(2,2) as self.sock:
            self.sock.settimeout(20.0)
            self.sock.bind(self.client_addr)
            
            while True:
                try:
                    str_message = input("Enter guess:\n").upper()
                    if not str_message or not str_message.isalpha():
                        continue
                    bytearray_message = bytearray(str_message,encoding="UTF-8")
                    self.sock.sendto(bytearray_message, self.server_addr)
                    
                    print("Waiting for a response...")
                    bytearray_reply, source_address = self.sock.recvfrom(8192)
                    reply = (utilities.forcedecode(bytearray_reply)).replace("7","_")
                    
                    if reply[0:15] == "CONGRATULATIONS" or reply[0:9] == "GAME OVER":
                        print(reply)
                        self.sock.close()
                        sys.exit()
                    else:
                        print(reply)
                except CN_Sockets.TimeoutException:
                    print("Server timed out.")
          
                    
if __name__ == "__main__":
    HangmanClient()




    
                
                
                
            



            
        
