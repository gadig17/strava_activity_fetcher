# Strava Weekly Activity Fetcher

A Python script that fetches your Strava activities for the current week, displays them in a formatted console output, and saves detailed data to JSON files for further analysis.

## Features

- **Weekly Activity Fetching**: Automatically retrieves activities from Monday to today
- **Console Output**: Clean, Markdown-formatted summaries for easy copy-pasting into AI chats
- **JSON Export**: Saves all activity data to structured JSON files in a `summary/` folder
- **Activity Types Supported**:
  - Runs (with detailed splits and pace analysis)
  - Workouts (with duration tracking)
  - Other activities (skipped but logged)
- **Token Management**: Automatic refresh of expired Strava API tokens

## Prerequisites

- Python 3.6+
- A Strava account with API access
- Strava API application (client ID and secret)

## Installation

1. **Clone the repository**:

   ```bash
   git clone <your-repo-url>
   cd strava-activity-fetcher
   ```

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install required packages**:

   ```bash
   pip install requests python-dotenv
   ```

## Setup

### 1. Create Strava API Application

1. Go to [Strava API Settings](https://www.strava.com/settings/api)
2. Create a new application if you haven't already
3. Note your `Client ID` and `Client Secret`

### 2. Get Initial Tokens

1. **Get Authorization Code**:
   - Replace `YOUR_CLIENT_ID` with your actual Client ID in this URL:

   ```url
   http://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=read,activity:read_all
   ```

   - Open the URL in your browser and authorize the application
   - Copy the `code` parameter from the redirect URL

2. **Exchange Code for Tokens**:

   ```bash
   curl -X POST https://www.strava.com/oauth/token \
     -F client_id=YOUR_CLIENT_ID \
     -F client_secret=YOUR_CLIENT_SECRET \
     -F code=THE_CODE_FROM_STEP_1 \
     -F grant_type=authorization_code
   ```

### 3. Create Environment File

Create a `.env` file in the project root with the following format:

```env
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
ACCESS_TOKEN=your_access_token
REFRESH_TOKEN=your_refresh_token
EXPIRES_AT=your_expires_at_timestamp
TOKEN_TYPE=Bearer
EXPIRES_IN=21600
```

Replace the values with the data from your Strava API application and the token exchange response.

## Usage

### Basic Usage

Run the main script to fetch activities for the current week:

```bash
python get_activities.py
```

### Authentication Testing

Test your authentication setup:

```bash
python strava_auth.py
```

## Output

### Console Output

The script displays activities in a clean, readable format:

```text
Fetching activities from 2025-07-28 00:00:00 UTC to now...
Found 3 total activities. Processing...

--- Processing Run: 'Morning Run' on 2025-07-30 ---
### Activity Summary
- **Distance**: 12.98 km
- **Moving Time**: 1:11:15
- **Average Pace**: 05:29 /km
- **Calories**: 1097

### Splits Breakdown
| Split | Pace (/km) | Distance (km) | Time    | Avg HR | Elev Diff (m) |
|-------|------------|---------------|---------|--------|---------------|
| 1     | 06:04      | 1.00          | 0:06:06 | 126    | -1.3          |
...
```

### JSON Output

Activity data is saved to `summary/Weekly-Activities-YYYY-MM-DD-to-YYYY-MM-DD.json`:

```json
{
  "week_period": "2025-07-28 to 2025-08-03",
  "generated_at": "2025-08-03T...",
  "total_activities": 3,
  "activities": [
    {
      "activity_type": "Run",
      "activity_name": "Morning Run",
      "date": "2025-07-30",
      "summary": {
        "distance_km": 12.98,
        "moving_time": "1:11:15",
        "average_pace_per_km": "05:29",
        "calories": 1097
      },
      "splits": [...]
    }
  ]
}
```

## File Structure

```text
├── get_activities.py      # Main script for fetching activities
├── strava_auth.py        # Authentication and token management
├── .env                  # Environment variables (not in repo)
├── .gitignore           # Git ignore rules
├── summary/             # Output folder for JSON files
│   └── Weekly-Activities-*.json
└── README.md            # This file
```

## Error Handling

The scripts include comprehensive error handling for:

- Missing or invalid environment variables
- Network connectivity issues
- API rate limiting
- Token expiration and refresh failures
- File I/O errors

## Security Notes

- **Never commit your `.env` file** - it contains sensitive API credentials
- The `.gitignore` file is configured to exclude sensitive files
- Tokens are automatically refreshed when they expire
- All API credentials are stored as environment variables

## Troubleshooting

### Authentication Issues

1. Verify your `.env` file has all required variables
2. Check that your Strava API application is correctly configured
3. Run `python strava_auth.py` to test authentication

### API Issues

1. Ensure you have the correct scopes (`read,activity:read_all`)
2. Check for API rate limiting (Strava has request limits)
3. Verify your tokens haven't been revoked

### File Issues

1. Ensure you have write permissions in the project directory
2. Check that the `summary/` folder can be created

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Strava API Documentation](https://developers.strava.com/)
- [python-dotenv](https://github.com/theskumar/python-dotenv) for environment variable management
