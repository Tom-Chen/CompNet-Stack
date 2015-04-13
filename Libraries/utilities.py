def checkLAN(input):
    if len(input) == 1:
        if input.isalpha():
            return True
    return False

def checkHost(input):
    if len(input) == 1:
        if input.isalpha():
            if input.upper() != "R":
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
