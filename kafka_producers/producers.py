import sys
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
from confluent_kafka import Producer
import time
import random

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

    while True:
        print(f"Current Location: {coordinates}")

        # Simulate some changes in coordinates
        latitude, longitude = coordinates
        latitude += random.uniform(-0.0005, 0.0005)
        longitude += random.uniform(-0.0005, 0.0005)

        current_time += timedelta(seconds=1)

        message = {
            'machine_name': machine_name,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': current_time.isoformat()
        }

        # Produce the message to the Kafka topic
        kafka_producer.produce('Machines_positions', key=machine_name, value=str(message))

        kafka_producer.flush()
        time.sleep(5)  # Simulate sending coordinates every  second

        # Update coordinates for the next iteration
        coordinates = (latitude, longitude)

# Check if the correct number of command-line arguments is provided
if len(sys.argv) != 3:
    print("Usage: python script.py <machine_name> <starting_city>")
    sys.exit(1)

machine_name = sys.argv[1]
starting_city = sys.argv[2]

producer_config = {'bootstrap.servers': '172.17.10.24:9094', 'client.id': machine_name}
kafka_producer = Producer(producer_config)

simulate_movement(machine_name, starting_city, kafka_producer)