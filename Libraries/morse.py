# import gpio
import Libraries.utilities as utilities, Libraries.gpio as gpio
import time, queue

To_Morse = {
  "A":".-", "B":"-...", "C":"-.-.", "D":"-..", "E":".", "F":"..-.", "G":"--.",
  "H":"....", "I":"..", "J":".---", "K":"-.-", "L":".-..", "M":"--", "N":"-.",
  "O":"---", "P":".--.", "Q":"--.-", "R":".-.", "S":"...", "T":"-", "U":"..-",
  "V":"...-", "W":".--", "X":"-..-", "Y":"-.--", "Z":"--..", "1":".----",
  "2":"..---", "3":"...--", "4":"....-", "5":".....", "6":"-....", "7":"--...",
  "8":"---..", "9":"----.", "0":"-----"
}

From_Morse = {v: k for k, v in To_Morse.items()}

def translate_message(message):
    tuplePack = []
    for c in message.upper():
        if(c == ' '):
            tuplePack.pop()
            tuplePack.append((0,7))
        else:
            charic = To_Morse[c]
            for ch in charic:
                if(ch == '-'):
                    tuplePack.append((1,3))
                else:
                    tuplePack.append((1,1))
                tuplePack.append((0,1))
            tuplePack.pop()
            tuplePack.append((0,3))
    tuplePack.pop()
    return tuplePack

def reverse_translate(tuples,verbose=False):
    message = ""
    letter = ""
    for t in tuples:
        if(t[0] == 0): # off pulse signalling an end
            if(t[1] >= 5): # space
                if letter != '':
                    reallet = From_Morse[letter]
                    message = message + reallet + " "
                else:
                    message += " "
                letter = ""
            elif(t[1] >= 2): # letter end
                reallet = From_Morse[letter]
                message = message + reallet
                letter = ""
        else:
            if(t[1] >= 2): # dash
                letter = letter + "-"
            else: # dot
                letter = letter + "."
    reallet = From_Morse[letter]
    if verbose: print(reallet)
    message = message + reallet
    return message

def package_message(sourceLAN, sourceMac, destLAN, destMac, nextProtocol,sourcePort,destPort,payload):
    return sourceLAN + sourceMac + destLAN + destMac + nextProtocol + \
    (utilities.createIPv4chksum(sourceLAN, sourceMac, destLAN, destMac, nextProtocol)) + str(sourcePort) + str(destPort) + payload
    

def send(messageQueue,transmitEvent,pin=17,verbose=True):
    gpio.prepare_pin_out(pin)
    if verbose:
        print("Sending thread started.")
    while True:
        if verbose: print("Waiting for a message...")
        message = messageQueue.get()

        source_lan = message[0]
        dest_lan = message[2]
        dest_host = message[3]

        if source_lan == dest_lan: # since we only have the data layer mac when sending locally we only add it here
            mac = translate_message(dest_host)
        else: # if you don't know what to do send it to the router
            mac = translate_message("R")
        
        if verbose: print("Waiting until bus is clear...")
        transmitEvent.wait()
        if verbose: print("Bus is clear.")
        gpio.blink((1,10),pin) # start prosign
        gpio.blink((0,1),pin)
        for tup in mac: # smush the local destination mac onto the front
            gpio.blink(tup,pin)
        gpio.blink((0,3),pin)
        tups = translate_message(message)
        for tup in tups:
            gpio.blink(tup,pin)
        gpio.blink((0,1),pin)
        gpio.blink((1,30),pin) # end prosign
        gpio.blink((0,1),pin)
        if verbose: print("Message sent.")

class Receive(object):

    def __init__(self,queuePut,transmitEvent,pin=23,verbose=True):
        gpio.prepare_pin_in(pin)
        self.output = [] #set of output tuples
        self.verbose = verbose
        self.prev_time = time.time()
        self.now_time = time.time()
        self.state = gpio.read_pin(pin)
        self.receiving = False
        self.transmitEvent = transmitEvent
        self.queuePut = queuePut
        gpio.add_event_detect(pin,self.edgeFound)
        if self.verbose: print("GPIO event added.")

    def edgeFound(self,pin=23):
        self.now_time = time.time()
        delta = self.now_time - self.prev_time
        pulse = (self.state,delta*100) # convert to 100hz
        self.prev_time = self.now_time
        self.state = gpio.read_pin(pin)
        
        if pulse[0] and pulse[1] > 10:
            if pulse[1] < 20:
                self.receiving = True
                self.transmitEvent.clear()
                self.output = []
                if self.verbose: print("Start sign received.")
            else:
                self.receiving = False
                self.transmitEvent.set()
                self.queuePut(self.output)
                if self.verbose: print("End sign received")
            return
            
        if self.receiving:
            self.output.append(pulse)
    
# if __name__ == "__main__":
    # with Safeguards():
        # gpio.prepare_pin()
        # send_message("4 ACES")