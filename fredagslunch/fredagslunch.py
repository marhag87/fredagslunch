from pathlib import Path
import googlemaps
from datetime import datetime
from pyyamlconfig import load_config

config = load_config(f'{Path.home()}/.config/fredagslunch.yaml')
data = config.get('data')
destination = config.get('destination')

people_with_cars = []
for person in data:
    if person.get('car'):
        people_with_cars.append(person)


gmaps = googlemaps.Client(key=config.get('key'))


shortest_distance = None
shortest_order = []

for person_with_car in people_with_cars:
    waypoints = set([x.get('location') for x in data])
    directions_result = gmaps.directions(
        person_with_car.get('location'),
        destination,
        mode="driving",
        departure_time=datetime.now(),
        waypoints=waypoints,
        optimize_waypoints=True,
    )

    distance = 0
    order = []
    for leg in directions_result[0].get('legs'):
        start_address = leg.get('start_address')
        if start_address not in order:
            order.append(start_address)
        end_address = leg.get('end_address')
        if end_address not in order:
            order.append(end_address)

        distance = distance + leg.get('distance').get('value')

    if shortest_distance is None or distance < shortest_distance:
        shortest_distance = distance
        shortest_order = order


print(f'Optimal route: {shortest_distance}m')
for address in shortest_order:
    print(f'  {address}')
    for person in data:
        if person.get('location') in address:
            print(f'    {person.get("name")}')
        if destination in address:
            print('    Destination')
            break
