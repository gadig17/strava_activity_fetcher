# strava_auth.py
#
# Description:
# This script handles the authentication with the Strava API v3. It reads your
# Strava credentials from environment variables, checks if the current access_token 
# has expired, and refreshes it if necessary. The new tokens are saved back to 
# the .env file and environment variables for the current session.
#
# Requirements:
#   - Python 3
#   - 'requests' library (install with: pip install requests)
#   - 'python-dotenv' library (install with: pip install python-dotenv)
#
# Setup:
# 1. Create a .env file in the same directory with the following variables:
#    CLIENT_ID=your_client_id
#    CLIENT_SECRET=your_client_secret
#    ACCESS_TOKEN=your_access_token
#    REFRESH_TOKEN=your_refresh_token
#    EXPIRES_AT=your_expires_at_timestamp
#    TOKEN_TYPE=Bearer
#    EXPIRES_IN=21600
#
# 2. To get your initial tokens, follow the Strava OAuth flow:
#    a. Go to: https://www.strava.com/settings/api
#    b. Use this URL (replace CLIENT_ID): 
#       http://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read,activity:read_all
#    c. Exchange the code for tokens using curl or a similar tool
#

import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_client_credentials():
    """Retrieve client credentials from environment variables."""
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print("Error: CLIENT_ID and CLIENT_SECRET must be set in the .env file.")
        return None, None
    
    return client_id, client_secret

def get_stored_tokens():
    """Get stored tokens from environment variables."""
    access_token = os.getenv('ACCESS_TOKEN')
    refresh_token = os.getenv('REFRESH_TOKEN')
    expires_at_str = os.getenv('EXPIRES_AT')
    
    if not access_token:
        print("Error: ACCESS_TOKEN must be set in the .env file.")
        return None
        
    if not refresh_token:
        print("Error: REFRESH_TOKEN must be set in the .env file.")
        return None
        
    if not expires_at_str:
        print("Error: EXPIRES_AT must be set in the .env file.")
        return None
    
    try:
        expires_at = int(expires_at_str)
    except ValueError:
        print("Error: EXPIRES_AT must be a valid integer timestamp.")
        return None
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_at': expires_at
    }

def update_env_file(new_access_token, new_refresh_token, new_expires_at):
    """Update the .env file with new token values."""
    try:
        # Read current .env file
        env_lines = []
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_lines = f.readlines()

        # Update or add the token values
        updated_lines = []
        tokens_to_update = {
            'ACCESS_TOKEN': new_access_token,
            'REFRESH_TOKEN': new_refresh_token,
            'EXPIRES_AT': str(new_expires_at)
        }

        # Track which tokens were updated
        updated_tokens = set()

        # Update existing lines
        for line in env_lines:
            line = line.strip()
            if line and not line.startswith('#'):
                key = line.split('=')[0]
                if key in tokens_to_update:
                    updated_lines.append(f"{key}={tokens_to_update[key]}\n")
                    updated_tokens.add(key)
                else:
                    updated_lines.append(line + '\n')
            else:
                updated_lines.append(line + '\n')

        # Add new tokens if they were not updated
        for key, value in tokens_to_update.items():
            if key not in updated_tokens:
                updated_lines.append(f"{key}={value}\n")

        # Write the updated lines back to the .env file
        with open('.env', 'w') as f:
            f.writelines(updated_lines)

        # Update the environment variables in the current session
        os.environ['ACCESS_TOKEN'] = new_access_token
        os.environ['REFRESH_TOKEN'] = new_refresh_token
        os.environ['EXPIRES_AT'] = str(new_expires_at)

        print("Tokens successfully updated in .env file.")
    except Exception as e:
        print(f"Error updating .env file: {e}")
        print("Tokens updated in current session only.")
        # Still update the environment variables in the current session
        os.environ['ACCESS_TOKEN'] = new_access_token
        os.environ['REFRESH_TOKEN'] = new_refresh_token
        os.environ['EXPIRES_AT'] = str(new_expires_at)

def get_access_token():
    """
    Main function to get a valid access token.
    It retrieves client credentials and stored tokens, checks for expiration,
    and refreshes if needed.
    
    Returns:
        str: Valid access token, or None if authentication fails
    """
    client_id, client_secret = get_client_credentials()
    if not client_id or not client_secret:
        return None

    tokens = get_stored_tokens()
    if not tokens:
        return None

    # Check if the token is expired or will expire in the next 10 minutes
    if tokens['expires_at'] < time.time() + 600:
        print("Access token expired or is about to expire. Refreshing...")

        # Prepare the data for the POST request
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': tokens['refresh_token'],
            'grant_type': 'refresh_token'
        }

        # Make the API call to refresh the token
        try:
            response = requests.post("https://www.strava.com/oauth/token", data=payload)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            new_tokens = response.json()

            # Update the .env file with new tokens
            update_env_file(
                new_tokens['access_token'], 
                new_tokens['refresh_token'], 
                new_tokens['expires_at']
            )

            print("Successfully refreshed the access token.")
            return new_tokens['access_token']

        except requests.exceptions.RequestException as e:
            print(f"Error refreshing token: {e}")
            print("Please check your .env file for correct credentials.")
            return None

    else:
        print("Access token is still valid.")
        return tokens['access_token']

def refresh_access_token():
    """
    Legacy function for backwards compatibility.
    Calls get_access_token() and displays results.
    """
    access_token = get_access_token()
    if access_token:
        print("\nAuthentication successful!")
        print(f"Current Access Token: {access_token}")
        print("\nYou can now use this token to make requests to the Strava API.")
    else:
        print("\nAuthentication failed. Please review the error messages above.")

if __name__ == "__main__":
    print("Attempting to get a valid Strava access token...")
    
    access_token = get_access_token()
    
    if access_token:
        print("\nAuthentication successful!")
        print(f"Current Access Token: {access_token}")
        print("\nYou can now use this token to make requests to the Strava API.")
    else:
        print("\nAuthentication failed. Please review the error messages above.")