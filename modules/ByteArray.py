from struct import *

class ByteArray:
    def __init__(self, bytes=b""):
        if isinstance(bytes, str): bytes = bytes.encode()
        self.bytes = bytes

    def writeByte(self, value: int):
        value = 255 if int(value) > 255 else int(value)
        self.write(pack("!b" if value < 0 else "!B", value))
        return self

    def writeShort(self, value: int):
        value = 65535 if int(value) > 65535 else int(value)
        self.write(pack("!h" if value < 0 else "!H", value))
        return self
    
    def writeInt(self, value: int):
        value = int(value)
        self.write(pack("!i" if value < 0 else "!I", value))
        return self
    
    def writeFloat(self, value: float):
        self.write(pack("!f", float(value)))
        return self
        
    def writeDouble(self, value: float):
        self.write(pack("!d", float(value)))
        return self
        
    def writeBoolean(self, value):
        return self.writeByte(int(value))

    def copy(self):
        return ByteArray(self.bytes)

    def writeUTF(self, value):
        if isinstance(value, int): value = str(value)
        if isinstance(value, str): value = value.encode()
        self.writeShort(len(value))
        self.write(value)
        return self

    def writeBytes(self, value):
        if isinstance(value, str): value = value.encode()
        self.bytes += value
        return self

    def read(self, c = 1):
        found = ""
        if self.getLength() >= c:
            found = self.bytes[:c]
            self.bytes = self.bytes[c:]
        return found

    def write(self, value):
        if isinstance(value, str): value = value.encode()
        self.bytes += value
        return self

    def readByte(self):
        value = 0
        if self.getLength() >= 1: value = unpack("!B", self.read())[0]
        return value

    def readShort(self):
        value = 0
        if self.getLength() >= 2: value = unpack("!H", self.read(2))[0]
        return value

    def readInt(self):
        value = 0
        if self.getLength() >= 4: value = unpack("!I", self.read(4))[0]
        return value

    def readFloat(self):
        value = 0.0
        if self.getLength() >= 4: value = unpack("!f", self.read(4))[0]
        return value
        
    def readDouble(self):
        value = 0.0
        if self.getLength() >= 8: value = unpack("!d", self.read(8))[0]
        return value
        
    def readUTF(self):
        value = ""
        if self.getLength() >= 2:
            value = self.read(self.readShort())
            if isinstance(value, (bytes, bytearray)): value = value.decode()
        return value

    def readBoolean(self):
        return self.readByte() > 0

    def readUTFBytes(self, size):
        value = self.bytes[:int(size)]
        self.bytes = self.bytes[int(size):]
        return value

    def getBytes(self):
        return self.bytes

    def toByteArray(self):
        return self.getBytes()

    def getLength(self):
        return len(self.bytes)

    def bytesAvailable(self):
        return self.getLength() > 0