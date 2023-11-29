import sys
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
from confluent_kafka import Producer
import time
import uuid
import random
import json
import os
import signal

class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True

# load_dotenv()

KAFKA_IP: str = os.getenv("KAFKA_IP")
KAFKA_TOPIC: str = os.getenv("KAFKA_TOPIC") or "gps"
HOSTNAME: str = os.getenv("HOSTNAME")
CITY: str = os.getenv("CITY") or "Pau"

# Function to get coordinates for a given location
def get_coordinates(location_name):
    geolocator = Nominatim(user_agent="kafka_gps_tracker")
    location = geolocator.geocode(location_name)
    if location:
        # Add a small random difference to the coordinates
        latitude = location.latitude + random.uniform(-0.001, 0.001)
        longitude = location.longitude + random.uniform(-0.001, 0.001)
        return latitude, longitude
    else:
        return None

# Function to simulate sending coordinates based on arguments
def simulate_movement(machine_name, starting_city, kafka_producer):
    coordinates = get_coordinates(starting_city)

    if coordinates is None:
        print(f"Error: Unable to get coordinates for {starting_city}. Please check the city name and try again.")
        sys.exit(1)

    current_time = datetime.now()

    try:
        killer = GracefulKiller()
        while not killer.kill_now:
            print(f"Current Location: {coordinates}")
            message_uuid = str(uuid.uuid4())


            # Simulate some changes in coordinates
            latitude, longitude = coordinates
            latitude += random.uniform(-0.0005, 0.0005)
            longitude += random.uniform(-0.0005, 0.0005)

            current_time += timedelta(seconds=1)

            message = {
                "name": machine_name,
                "lng": longitude,
                "lat": latitude,
                "timestamp": int(current_time.timestamp()),
                "uuid": message_uuid
            }

            # Produce the message to the Kafka topic
            kafka_producer.produce(KAFKA_TOPIC, key=message_uuid, value=json.dumps(message))

            kafka_producer.flush()

            time.sleep(5)  # Simulate sending coordinates every  second

            # Update coordinates for the next iteration
            coordinates = (latitude, longitude)

    except Exception as e:
        print(f"Error in simulate_movement: {e}")


# Check if the correct number of command-line arguments is provided
# if len(sys.argv) != 3:
#     print("Usage: python producers.py <machine_name> <starting_city>")
#     sys.exit(1)

machine_name =  HOSTNAME
starting_city =  CITY

producer_config = {'bootstrap.servers': KAFKA_IP, 'client.id': machine_name}
kafka_producer = Producer(producer_config)

simulate_movement(machine_name, starting_city, kafka_producer)
