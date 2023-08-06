import requests
import airport_list
from datetime import datetime, timezone


class DrivingFlying:
    def __init__(self, origin, date_from, date_to, return_from, return_to):
        self.origin = airport_list.popular_airports[origin]
        self.date_from = date_from
        self.date_to = date_to
        self.return_from = return_from
        self.return_to = return_to

    def record_flights(self):
        # postintoSpreadSheets
        api_key = 'API_KEY'
        url = 'https://api.sheety.co/10ff97581bc4b0585d95d7cb79113422/lowestAirplanePriceTracker/sheet1'

        print(requests.get(url).status_code)

        for items in airport_list.popular_airports:
            if items == self.origin:
                continue
            destination = airport_list.popular_airports[items]
            # sort flights based on price
            flight_price = sorted(self.get_flight_price(origin=self.origin, destination=destination),
                                  key=lambda a: a[2])
            if not flight_price:
                continue
            # M (driving_distance) / mpg  X  $ (average_price_of_gas) = gas_cost
            d = self.get_driving_duration(self.origin, destination)[1]
            if isinstance(d, int) or isinstance(d, float):
                driving_distance = d
            else:
                driving_distance = ''.join(filter(lambda x: x.isdigit(), d))
            driving_cost = round(float(driving_distance) / 25.4 * 3.83, 2)

            body = {
                "sheet1": {
                    "origin": f"{self.origin}({self.get_iata_code(self.origin)})",
                    "destination": f"{destination}({self.get_iata_code(destination)})",
                    "leavingDate": f"{flight_price[0][0]}",
                    "returnDate": f"{flight_price[0][1]}",
                    "airplanePrice($)": f"{flight_price[0][2]}",
                    "flightDuration(hrs)": f"{flight_price[0][3]}",
                    "drivingCost($)": f"{driving_cost}",
                    "drivingDuration(hrs)": f"{round(self.get_driving_duration(self.origin, destination)[0], 1)}"
                }
            }
            requests.post(url=url, json=body)

    def get_driving_duration(self, origin, destination):
        if destination == 'Manchester Airport':
            destination = 'Manchester-Boston Regional Airport'
        apikey = 'API_KEY'
        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&units=imperial&key={apikey}"
        r = requests.get(url=url).json()
        estimate = r['rows'][0]['elements'][0]
        if 'duration' in estimate:
            return estimate['duration']['value'] / 3600, estimate['distance']['text']

        return 0, 0

    def get_iata_code(self, airport_name):
        url = f'https://api.api-ninjas.com/v1/airports?name={airport_name}'
        api_key = 'API_KEY'
        headers = {
            'X-Api-Key': api_key
        }

        r = requests.get(url, headers=headers)
        return r.json()[0]['iata']

    def get_flight_price(self, origin, destination):
        fly_from, fly_to = self.get_iata_code(origin), self.get_iata_code(destination)
        apikey = 'API_KEY'
        url = 'https://api.tequila.kiwi.com/v2/search'
        price_list = []
        headers = {
            'apikey': apikey,
        }
        params = {
            'fly_from': f'{fly_from}',
            'fly_to': f'{fly_to}',
            'date_from': self.date_from,
            'date_to': self.date_to,
            'return_from': self.return_from,
            'return_to': self.return_to
        }

        r = requests.get(url, headers=headers, params=params).json()
        bag_cost = 0

        for items in r['data']:
            # "2021-04-02T10:00:00.000Z"
            leaving_date = datetime.fromisoformat(items['utc_departure'][:-1]).astimezone(timezone.utc)
            return_date = datetime.fromisoformat(items['utc_arrival'][:-1]).astimezone(timezone.utc)
            date_time_diff = return_date - leaving_date

            if '1' in items['bags_price']:
                bag_cost = items['bags_price']['1']

            total_cost = items['price'] + bag_cost
            price_list.append(
                (
                    leaving_date.date(), return_date.date(), round(total_cost, 2),
                    round(date_time_diff.seconds / 3600, 1)))

        return price_list
