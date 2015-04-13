from Libraries import morse, utilities
from Constants import a_local, b_local

class UDP_Pi_Send(object):
    
    def __init__(self):
        input_lan = input("Enter LAN (A or B):\n").upper()
        input_host = input("Enter Host (A or B):\n").upper()
        self.self_map = (input_lan, input_host)
        
        if input_lan == "A":
            self.local_map = a_local.map
        elif input_lan == "B":
            self.local_map = b_local.map
        else:
            print("Invalid LAN.")
            return
        if input_host not in self.local_map:
            print("Invalid Host")
            return
            
        print ("UDP_Pi sending client started.")
        
        while True:
            dest_lan = input("Enter destination LAN:\n")
            if not (utilities.checkLAN(dest_lan)):
                print("Invalid LAN")
                continue
            dest_host = input("Enter destination Host:\n")
            if not (utilities.checkHost(dest_host)):
                print("Invalid Host")
                continue
            str_message = input("Enter message to send:\n")
            
            source_port, dest_port = "00", "99"
            morse_network_header = morse.package_network_header(input_lan, input_host, dest_lan, dest_host, "1")
            morse_udp_message = morse.package_udp_message(source_port, dest_port, str_message)
            
            if dest_lan != self.self_map[0]:
                message = morse.package_message("R", input_lan, input_host, dest_lan, dest_host, "1", source_port, dest_port, str_message) # send to router
            else:
                message = morse.package_message(dest_host, input_lan, input_host, dest_lan, dest_host, "1", source_port, dest_port, str_message) # send direct to destination host
            sendqueue.put(message)

        print ("UDP_Client ended")

    


if __name__ == "__main__":
    UDP_Pi_Send()
