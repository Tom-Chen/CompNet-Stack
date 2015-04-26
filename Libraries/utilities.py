import json

_DEF_IP = ['192', '168', '0', '0']

# ----- SOCKETS BASE UTILITY FUNCTIONS ----- #
def _morse2ipv4 (morse_ip):
    """
    Translates a morse IP address (eg. 'R0') to an ipv4 address according to
    the class agreement on ipv4 - morse mapping. The ipv4 address has its
    last two fields filled in by the ascii code corresponding to the respective
    characters of the ip address (eg. 'R' -> 82, '0' -> 48).
    ex. input = 'R0', output = '192.168.82.48'
    """

    ipv4 = _DEF_IP
    ipv4[2] = str(ord(morse_ip[0])) # Map Morse IP field to third ipv4 field
    ipv4[3] = str(ord(morse_ip[1])) # Map Morse MAC field to fourth ipv4 field
    return '.'.join(ipv4)


def _ipv42morse (addr):
    """
    Translates an IPV4 address (eg. '192.168.82.48') to a morse address according to
    the class agreement on ipv4 - morse mapping. The morse address is two chars long
    with the characters corresponding to the ascii characters mapped to the numeric
    ascii codes in the last two fields of the IPV4 address (eg. 82 -> 'R', 48 -> '0').
    ex. input = '192.168.82.48', output = 'R0'
    also handles ports
    """
    port = addr[1]
    ipv4 = addr[0].split(".")
    return [chr(int(ipv4[2])), chr(int(ipv4[3])), port]
    
def forcedecode (encoded):
    try:
        return encoded.decode('utf-8')
    except (TypeError, AttributeError):
        return encoded

def checkLAN(input):
    if len(input) == 1:
        if input.isalpha():
            return True
    return False

def checkHost(input):
    if len(input) == 1:
        if input.isalpha():
            if input != "R":
                return True
    return False
    
def createIPv4chksum(sourceLAN, sourceMac, destLAN, destMac, nextProtocol):
    header = bytearray(sourceLAN + sourceMac + destLAN + destMac + str(nextProtocol),encoding="UTF-8")
    decsum = 0
    for item in header:
        decsum += int(item)
    # print(bin(decsum))
    binsumflip = bin(decsum)[2:]
    binsumflip = "0" * (16-len(binsumflip)) + binsumflip
    # print(binsumflip)
    binsum = ""
    for char in binsumflip:
        if char == "0":
            binsum+= "1"
        else:
            binsum+= "0"
    return(hex(int(binsum,2))[2:].upper())
    
def testIPv4chksum(header):
    header = bytearray(header,encoding="UTF-8")
    decsum = 0
    for item in header[0:5]: #non checksum parts
        decsum += int(item)
    decsum += int(header[5:],16) # checksum has to be converted from hex instead of ascii
    binsumflip = bin(decsum)[2:]
    binsum = ""
    for char in binsumflip:
        if char == "0":
            binsum+= "1"
        else:
            binsum+= "0"
    if(int(binsum)) == 0:
        return True
    else:
        return False

def serialize(instruction, parameters={}):
    return json.dumps(
        {"instruction": instruction,
         "params": parameters
        }).encode('utf-8')
        

def deserialize(serialized):
    return json.loads(serialized.decode('utf-8'))