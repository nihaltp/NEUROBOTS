import socket
import select

class WiFiComms:
    def __init__(self, local_port=12346):
        """
        Initialize the WiFi UDP communicator.
        
        :param local_port: The port to listen on for incoming messages from ESP.
        """
        self.local_port = local_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('0.0.0.0', self.local_port))
        self.sock.setblocking(0) # Non-blocking mode

    def receive_message(self):
        """
        Check for an incoming message.
        
        :return: A tuple of (message_string, address) or (None, None) if no message.
        """
        ready = select.select([self.sock], [], [], 0.01)
        if ready[0]:
            data, addr = self.sock.recvfrom(1024)
            return data.decode('utf-8'), addr
        return None, None

    def send_message(self, target_ip, target_port, message):
        """
        Send a message to the ESP.
        
        :param target_ip: The IP address of the ESP.
        :param target_port: The listening port of the ESP.
        :param message: The string message to send.
        """
        self.sock.sendto(message.encode('utf-8'), (target_ip, target_port))
        
    def close(self):
        """Close the socket."""
        self.sock.close()
