import requests

# Set the base URL of the API
base_url = 'http://192.168.1.12:5000'

# Authentication endpoint
auth_url = f'{base_url}/auth'

# Customer endpoint
customer_url = f'{base_url}/customer'

# Driver endpoint
driver_url = f'{base_url}/driver'

# Authenticate and get the access token
auth_data = {'username': 'admin', 'password': 'admin'}
response = requests.post(auth_url, json=auth_data)
access_token = response.json().get('access_token')

# Set the headers with the access token
headers = {'Authorization': f'Bearer {access_token}'}

# Test the customer endpoints
customer_data = {
    'name': 'John Doe',
    'rating': 5,
    'balance': 100,
    'location': 'New York',
    'destination': 'Los Angeles'
}

# Create a new customer
response = requests.post(customer_url, json=customer_data, headers=headers)
print(response.status_code)
print(response.json())

# Get a specific customer
customer_id = 1
response = requests.get(f'{customer_url}/{customer_id}', headers=headers)
print(response.status_code)
print(response.json())

# Update a customer
updated_customer_data = {
    'rating': 4,
    'balance': 150,
    'destination': 'San Francisco'
}
response = requests.patch(f'{customer_url}/{customer_id}', json=updated_customer_data, headers=headers)
print(response.status_code)
print(response.json())

# Delete a customer
response = requests.delete(f'{customer_url}/{customer_id}', headers=headers)
print(response.status_code)

# Test the driver endpoints
driver_data = {
    'name': 'Jane Smith',
    'rating': 4,
    'status': 'available',
    'location': 'Chicago',
    'destination': 'Houston'
}

# Create a new driver
response = requests.post(driver_url, json=driver_data, headers=headers)
print(response.status_code)
print(response.json())

# Get a specific driver
driver_id = 1
response = requests.get(f'{driver_url}/{driver_id}', headers=headers)
print(response.status_code)
print(response.json())

# Update a driver
updated_driver_data = {
    'rating': 5,
    'status': 'unavailable',
    'location': 'Miami',
    'destination': 'Orlando'
}
response = requests.patch(f'{driver_url}/{driver_id}', json=updated_driver_data, headers=headers)
print(response.status_code)
print(response.json())

# Delete a driver
response = requests.delete(f'{driver_url}/{driver_id}', headers=headers)
print(response.status_code)
