import asyncio
import threading
import queue
import time
import logging
from bleak import BleakClient, BleakScanner

logger = logging.getLogger("BLEComms")

class BLEComms:
    def __init__(self, device_name, service_uuid, command_char_uuid, status_char_uuid=None, ack_callback=None):
        """
        Initialize the BLE communicator in a background thread.
        """
        self.device_name = device_name
        self.service_uuid = service_uuid
        self.command_char_uuid = command_char_uuid
        self.status_char_uuid = status_char_uuid
        self.ack_callback = ack_callback
        
        self.command_queue = queue.Queue()
        self.is_connected = False
        self.client = None
        self._running = True
        
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
    def _run_loop(self):
        """Runs the asyncio event loop in a background thread."""
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._main_task())
        
    async def _main_task(self):
        """Main asynchronous task for BLE connection and command queue processing."""
        while self._running:
            if not self.is_connected:
                logger.info(f"Scanning for BLE device: {self.device_name}...")
                device = await self._discover_device()
                if device:
                    logger.info(f"Found {self.device_name} ({device.address}), connecting...")
                    try:
                        self.client = BleakClient(device, disconnected_callback=self._handle_disconnect)
                        await self.client.connect()
                        self.is_connected = True
                        logger.info(f"Successfully connected to {self.device_name}")
                        
                        # Subscribe to status notifications if provided
                        if self.status_char_uuid:
                            await self.client.start_notify(self.status_char_uuid, self._notification_handler)
                            
                    except Exception as e:
                        logger.error(f"Failed to connect to {self.device_name}: {e}")
                        await asyncio.sleep(2)
                else:
                    await asyncio.sleep(2)
            else:
                # Process outgoing commands from the queue
                try:
                    # Non-blocking get to allow loop iteration
                    command = self.command_queue.get_nowait()
                    try:
                        if self.client and self.client.is_connected:
                            await self.client.write_gatt_char(self.command_char_uuid, command.encode('utf-8'))
                            logger.debug(f"Sent BLE command: {command}")
                        else:
                            logger.warning("Tried to send command but client is disconnected. Requeuing...")
                            # Add back to the front of the queue
                            self._requeue(command)
                    except Exception as e:
                        logger.error(f"Error sending BLE command: {e}")
                        self._requeue(command)
                        self._trigger_reconnect()
                except queue.Empty:
                    await asyncio.sleep(0.05)
                    
    async def _discover_device(self):
        """Scans for the device by name or service UUID."""
        try:
            devices = await BleakScanner.discover(timeout=5.0, return_adv=True)
            for address, (d, adv) in devices.items():
                if d.name == self.device_name or adv.local_name == self.device_name:
                    return d
                if self.service_uuid.lower() in [u.lower() for u in adv.service_uuids]:
                    return d
        except Exception as e:
            logger.error(f"Error scanning for BLE devices: {e}")
        return None

    def _handle_disconnect(self, client):
        """Callback when the BLE device disconnects unexpectedly."""
        logger.warning(f"BLE disconnected from {self.device_name}!")
        self.is_connected = False
        self.client = None

    def _trigger_reconnect(self):
        self.is_connected = False
        self.client = None

    def _requeue(self, command):
        """Helper to requeue a command, effectively putting it at the front for next reconnect."""
        temp_list = [command]
        while not self.command_queue.empty():
            try:
                temp_list.append(self.command_queue.get_nowait())
            except queue.Empty:
                break
        for c in temp_list:
            self.command_queue.put(c)

    def _notification_handler(self, sender, data):
        """Handles incoming notifications/ACKs from the ESP32."""
        payload = data.decode('utf-8').strip()
        logger.info(f"BLE Notification from ESP32: {payload}")
        if self.ack_callback:
            self.ack_callback(payload)

    def send_command(self, command):
        """
        Synchronous method to enqueue a command to be sent over BLE.
        This is safe to call from Flask / other threads.
        """
        self.command_queue.put(command)

    def close(self):
        """Cleanly shutdown the BLE communicator."""
        self._running = False
        if self.client and self.client.is_connected:
            # We can't await here since it's synchronous, but we can schedule it on the loop
            asyncio.run_coroutine_threadsafe(self.client.disconnect(), self._loop)
        # Give it a moment to shutdown
        time.sleep(0.5)
