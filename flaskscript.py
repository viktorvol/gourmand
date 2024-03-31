from flask import Flask, request, jsonify
import requests
import random

app = Flask(__name__)

@app.route('/find_restaurant', methods=['GET'])
def find_restaurant():
    api_key = 'AIzaSyBgIWAq02krq0d1zbWgxdP_8U4Y1_63QvY'  # Replace with your API key
    location = request.args.get('location')

    keyword = request.args.get('keyword', 'restaurant')
    min_rating = float(request.args.get('min_rating', 4.0))
    radius = int(request.args.get('radius', 10000))
    num_results = int(request.args.get('num_results', 20))

    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'key': api_key,
        'location': location,
        'radius': radius,
        'keyword': keyword,
        'type': 'restaurant'
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'results' in data:
        eligible_restaurants = [restaurant for restaurant in data['results'] if restaurant.get('rating', 0.0) >= min_rating]
        if eligible_restaurants:
            if len(eligible_restaurants) <= num_results:
                chosen_restaurant = random.choice(eligible_restaurants)
            else:
                chosen_restaurant = random.sample(eligible_restaurants, num_results)
            
            restaurant_id = chosen_restaurant['place_id']
            restaurant_details = get_restaurant_details(api_key, restaurant_id)
            
            # Include coordinates of the restaurant
            restaurant_details['coordinates'] = chosen_restaurant['geometry']['location']
            
            return jsonify(restaurant_details)
        else:
            return jsonify({'message': 'No eligible restaurants found.'}), 404
    else:
        return jsonify({'message': 'Error in fetching data.'}), 500

def get_restaurant_details(api_key, place_id):
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    params = {
        'key': api_key,
        'place_id': place_id,
        'fields': 'name,rating,types,vicinity,price_level,user_ratings_total,opening_hours,geometry,website'
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'result' in data:
        return data['result']
    else:
        return None

if __name__ == '__main__':
    app.run()
