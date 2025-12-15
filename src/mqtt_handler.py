"""
MQTT handler for RFID card reader communication (FastAPI version)
Handles authentication and access control via MQTT messages
"""
from typing import Optional
import paho.mqtt.client as mqtt
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.data.models.user import User
from src.data.models.carddata import Card
from src.data.models.timecard import Timecard
from src.data.models.logdata import Log
from src.config import settings


# Constants
DEFAULT_CODE = "00000000"
ACCESS_DENIED_CODE = "0"
ACCESS_ALLOWED_CODE = "1"


def code_convert(kod: str) -> str:
    """
    Convert hexadecimal code to decimal string
    
    Args:
        kod: Hexadecimal code
        
    Returns:
        Decimal code as zero-padded string
    """
    pom = int(kod, base=16)
    kod_str = str(pom).zfill(10)
    return kod_str


def find_topic_substring(topic: str, hledat: str) -> bool:
    """
    Check if substring exists in topic
    
    Args:
        topic: Topic string to search in
        hledat: Substring to search for
        
    Returns:
        True if found, False otherwise
    """
    pom = topic.find(hledat)
    return pom >= 0


class MQTTHandler:
    """MQTT handler for card reader communication"""
    
    def __init__(self, db_session: Session):
        """
        Initialize MQTT handler
        
        Args:
            db_session: Database session
        """
        self.db = db_session
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
    
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback when connected to MQTT broker
        
        Args:
            client: MQTT client
            userdata: User data
            flags: Connection flags
            rc: Return code
        """
        print(f"Connected to MQTT broker with result code {rc}")
        # Subscribe to all topics (can be restricted to specific patterns)
        client.subscribe('#', qos=0)
    
    def on_message(self, client, userdata, msg):
        """
        Callback when MQTT message is received
        
        Args:
            client: MQTT client
            userdata: User data
            msg: MQTT message
        """
        print(f"{msg.topic}: {str(msg.payload)}")
        self.door_test(msg)
    
    def door_test(self, msg):
        """
        Process door access request
        
        Args:
            msg: MQTT message containing card number and reader ID
        """
        # Find timecard/reader by identifier
        id_ctecka = self.db.query(Timecard).filter_by(
            identreader=str(msg.topic).zfill(10)
        ).first()
        
        msgtopic = msg.topic
        
        if id_ctecka is not None:
            # Extract chip number from message payload
            try:
                testchip = int(msg.payload)
            except (ValueError, TypeError):
                print(f"Invalid chip number in payload: {msg.payload}")
                return
            
            # Find user by chip number
            user_chip = User.find_by_chip(testchip)
            
            if not user_chip:
                # Log unknown card (commit separately to avoid blocking)
                try:
                    log = Log(
                        time=datetime.now(),
                        text=f"Neznama karta {code_convert(str(msg.payload))} {str(msg.payload).zfill(10)}"
                    )
                    self.db.add(log)
                    self.db.commit()
                except Exception as e:
                    print(f"Error logging unknown card: {e}")
                    self.db.rollback()
            else:
                print("Kontrola vstupu")
                
                # Check access permissions
                pomveta = User.access_by_group(testchip, msgtopic)
                
                # Create card access log entry
                card = Card(
                    card_number=user_chip.card_number,
                    time=datetime.now(),
                    id_card_reader=id_ctecka.id,
                    id_user=user_chip.id,
                    access=pomveta
                )
                
                # Publish MQTT response and log in one transaction
                try:
                    if pomveta:
                        # Grant access
                        self.client.publish(id_ctecka.pushopen, payload=ACCESS_ALLOWED_CODE)
                        print(f"{id_ctecka.pushopen} - ACCESS ALLOWED")
                    else:
                        # Deny access
                        self.client.publish(id_ctecka.pushopen, payload=ACCESS_DENIED_CODE)
                        print(f"{id_ctecka.pushopen} - ACCESS DENIED")
                    
                    # Log card access
                    self.db.add(card)
                    self.db.commit()
                except Exception as e:
                    print(f"Error processing access: {e}")
                    self.db.rollback()
    
    def connect(self, host: str = None, port: int = None, keepalive: int = 60):
        """
        Connect to MQTT broker
        
        Args:
            host: MQTT broker host
            port: MQTT broker port
            keepalive: Keepalive interval in seconds
        """
        broker_host = host or settings.MQTT_BROKER
        broker_port = port or settings.MQTT_PORT
        
        self.client.connect(broker_host, broker_port, keepalive)
    
    def start(self):
        """Start MQTT client loop"""
        self.client.loop_forever()
    
    def stop(self):
        """Stop MQTT client"""
        self.client.disconnect()


def start_mqtt_listener():
    """
    Start MQTT listener for card readers
    This function should be run in a separate thread/process
    """
    # Create database session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        handler = MQTTHandler(db)
        handler.connect()
        print(f"Starting MQTT listener on {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
        handler.start()
    finally:
        db.close()


if __name__ == "__main__":
    start_mqtt_listener()
