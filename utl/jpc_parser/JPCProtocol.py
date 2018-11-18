from uuid import getnode as get_mac
import json
import crc16


class JPCProtocol:
    # opcodes
    HELLO = 0
    CLOSE = 1
    HEARTBEAT = 2
    ERROR = 3
    SEND = 4
    TELL = 5

    # error codes
    ERROR_UNKNOWN = 0
    ERROR_TIMED_OUT = 1

    # misc
    HEARTBEAT_INTERVAL = 3
    HEARTBEAT_TIMEOUT = 5
    STANDARD_PORT = 27272

    # byte stuffing
    FRAME_BYTE = 0x7E
    ESCAPE_BYTE = 0x7D
    XOR_BYTE = 0x20

    def __init__(self, opcode, payload=None):
        self.opcode = opcode
        self.payload = payload

    def to_json(self):
        js = {
            'opcode':      self.opcode,
            'payload':     self.payload
        }

        if self.opcode == JPCProtocol.SEND:
            js['payload'] = self.payload
        elif self.opcode == JPCProtocol.HELLO:
            js['payload'] = get_mac()
        elif self.opcode == JPCProtocol.HEARTBEAT:
            js['payload'] = get_mac()

        return json.dumps(js)

    def encode(self):
        data = self.to_json().encode()
        data += JPCProtocol.calculate_crc(data)
        raw_data = bytes([])
        end = bytes([JPCProtocol.FRAME_BYTE])
        for byte in data:
            if byte == JPCProtocol.FRAME_BYTE or byte == JPCProtocol.ESCAPE_BYTE:
                raw_data += bytes([JPCProtocol.ESCAPE_BYTE])
                raw_data += bytes([byte ^ JPCProtocol.XOR_BYTE])
            else:
                raw_data += bytes([byte])

        return end + raw_data + end

    def decode(raw_data):
        data_array = []
        data = b''
        i = 0
        while i < len(raw_data):
            byte = raw_data[i]
            if byte == JPCProtocol.FRAME_BYTE:
                if data != b'':
                    crc = JPCProtocol.calculate_crc(data[:-2])
                    if crc == data[-2:]:
                        data_array.append(json.loads(data[:-2].decode()))
                    data = b''
            elif byte == JPCProtocol.ESCAPE_BYTE:
                i += 1
                byte = raw_data[i]
                data += bytes([byte ^ JPCProtocol.XOR_BYTE])
            else:
                data += bytes([byte])
            i += 1
        return data_array

    def send(self, sock):
        raw_data = self.encode()
        sock.send(raw_data)

    def calculate_crc(data):
        return crc16.crc16xmodem(data).to_bytes(length=2, byteorder='little')
