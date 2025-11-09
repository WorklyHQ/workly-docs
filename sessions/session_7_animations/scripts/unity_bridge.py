"""
Unity Bridge - IPC communication with Unity application.
Uses socket-based communication (can be upgraded to OSC later).
"""

import socket
import json
import logging
import threading
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class UnityBridge:
    """Manages communication between Python and Unity via sockets."""
    
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 5555
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        """Initialize Unity bridge.
        
        Args:
            host: Host address for socket connection
            port: Port number for socket connection
        """
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.receive_thread: Optional[threading.Thread] = None
        self.running = False
        
    def connect(self) -> bool:
        """Establish connection to Unity.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            # Start receive thread
            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            logger.info(f"Connected to Unity at {self.host}:{self.port}")
            return True
            
        except (socket.error, socket.timeout) as e:
            logger.error(f"Failed to connect to Unity: {e}")
            self.connected = False
            return False
            
    def disconnect(self):
        """Close connection to Unity."""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            
        logger.info("Disconnected from Unity")
        
    def is_connected(self) -> bool:
        """Check if connected to Unity.
        
        Returns:
            True if connected, False otherwise
        """
        return self.connected
        
    def send_command(self, command: str, data: Dict[str, Any] = None) -> bool:
        """Send a command to Unity.
        
        Args:
            command: Command name
            data: Optional command data
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.connected or not self.socket:
            logger.warning("Cannot send command: not connected to Unity")
            return False
            
        try:
            message = {
                "command": command,
                "data": data or {}
            }
            
            json_data = json.dumps(message)
            self.socket.sendall(json_data.encode('utf-8') + b'\n')
            
            logger.debug(f"Sent command to Unity: {command}")
            return True
            
        except socket.error as e:
            logger.error(f"Error sending command to Unity: {e}")
            self.connected = False
            return False
            
    def _receive_loop(self):
        """Background thread to receive messages from Unity."""
        buffer = ""
        
        while self.running and self.socket:
            try:
                data = self.socket.recv(4096)
                if not data:
                    logger.warning("Unity connection closed")
                    self.connected = False
                    break
                    
                buffer += data.decode('utf-8')
                
                # Process complete messages (delimited by newline)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self._handle_message(line)
                    
            except socket.timeout:
                continue
            except socket.error as e:
                logger.error(f"Error receiving from Unity: {e}")
                self.connected = False
                break
                
    def _handle_message(self, message: str):
        """Handle a message received from Unity.
        
        Args:
            message: JSON message string
        """
        try:
            data = json.loads(message)
            logger.debug(f"Received from Unity: {data}")
            
            # TODO: Implement message handlers based on message type
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Unity message: {e}")

    # === VRM Control Methods ===

    def load_vrm_model(self, model_path: str) -> bool:
        """Load a VRM model in Unity.
        
        Args:
            model_path: Path to the VRM model file
            
        Returns:
            True if command sent successfully, False otherwise
        """
        return self.send_command("load_model", {"path": model_path})

    def set_expression(self, expression_name: str, value: float) -> bool:
        """Set a facial expression on the VRM avatar.
        
        Args:
            expression_name: Name of the expression (e.g., "joy", "angry", "sorrow")
            value: Expression intensity from 0.0 (0%) to 1.0 (100%)
            
        Returns:
            True if command sent successfully, False otherwise
        """
        # Clamp value between 0.0 and 1.0
        value = max(0.0, min(1.0, value))
        
        return self.send_command("set_expression", {
            "name": expression_name,
            "value": value
        })

    def reset_expressions(self) -> bool:
        """Reset all facial expressions to neutral.
        
        Returns:
            True if command sent successfully, False otherwise
        """
        return self.send_command("reset_expressions", {})

    def set_transition_speed(self, speed: float) -> bool:
        """Set the transition speed for smooth expressions.
        
        Args:
            speed: Transition speed from 0.1 (slow) to 10.0 (fast)
            
        Returns:
            True if command sent successfully, False otherwise
        """
        # Clamp speed between 0.1 and 10.0
        speed = max(0.1, min(10.0, speed))
        
        return self.send_command("set_transition_speed", {
            "speed": speed
        })

