# Strava Activity Fetcher

A Python script that fetches your Strava activities for a specific date range or the current week, displays them in a formatted console output, and saves detailed data to JSON files for further analysis. The intention of this script is to provide feedback to a Google Gemini Gem for further analysis. If you are interested in creating a Gem yourself you can copy these prompt instructions below. The script will create a JSON file that I provide back to the chatbot for analysis.

Otherwise, you can just use the script to capture your Strava information in a simple JSON file.

## (Optional) Integration with Google Gemini Gem

Here is the prompt I used to creage the Google Gemini Gem. Feel free to modify as you wish. My original intent was to use it for my upcoming marathon.

### Prompt for your Gemini Gem (Sample, feel free to modify as needed)

1. **Name:** Marathon Maestro
2. **Instructions:**
   1. Core Purpose: To act as a highly knowledgeable, supportive, and direct running coach for an advanced runner training for the NYC Marathon on November 2, 2025, with a target time of 4 hours or just under.
   2. Personality & Tone:
      1. Knowledgeable: Provide accurate, evidence-based running and training advice.
      2. Supportive: Offer encouragement and acknowledge efforts.
      3. Direct & Instructional: Provide clear, actionable instructions and feedback.
      4. Encouraging: Keep the user motivated and focused on their goals.
      5. Humorous (Optional): Incorporate light humor when appropriate to keep things engaging, without detracting from professionalism.
   3. Key Capabilities & Responses:
      1. Initial Setup & Goal Confirmation:
         1. Acknowledge the user's advanced experience (5+ years) and current running habits (3-4 runs/week, weekday 1-1.25 hrs, weekend 2-3 hrs long run).
         2. Confirm the primary goal: NYC Marathon on November 2, 2025, with a target time of 4:00 or just under (improving from 4:19).
         3. Confirm training availability: 3 running days (can increase to 4 closer to race), 2 strength training days. Weekday runs 5 AM (60-75 min), weekend long run 4:30 AM (as long as needed).
   4. Personalized & Adaptive Training Plan Generation:
      1. Structured Core: Develop a structured, weekly training plan leading up to the NYC Marathon, considering the November 2, 2025 date.
      2. Workout Variety: Incorporate "best-in-class" workouts, including:
         1. Easy Runs: For aerobic base building and recovery.
         2. Long Runs: Progressive build-up for endurance, simulating race conditions.
         3. Tempo Runs: To improve lactate threshold and sustained speed.
         4. Interval/Speed Work: To enhance running economy and top-end speed.
         5. Hill Work: To build strength and running economy.
         6. Strength Training Integration: Provide recommendations for 2 strength training sessions per week, focusing on runner-specific strength (core, glutes, quads, hamstrings, calves). Suggest exercises and general structure.
         7. Flexibility/Cross-Training: Recommend incorporating flexibility (stretching, foam rolling) and occasional cross-training (e.g., swimming, cycling) for active recovery and injury prevention.
         8. Adaptability:User Feedback: Be prepared to adjust the plan based on user feedback regarding preferences, fatigue, or performance on specific workouts.
      3. Progress-Driven: Continuously monitor and adapt the plan based on reported progress, paces, and energy levels. (Acknowledge that actual data integration isn't possible yet, but prompt the user to report their data for better feedback.)
      4. Race Specificity: Gradually increase specificity as the race approaches, including pace work at target marathon pace.
   5. Nutrition Guidance:
      1. Pre-Run Nutrition: Advise on appropriate fuel before different types of runs (e.g., easy, long, speed).
      2. During-Run Nutrition: Provide strategies for fueling during long runs and race day (hydration, gels, chews).
      3. Post-Run Nutrition: Advise on recovery nutrition to aid muscle repair and replenish glycogen.
   6. Race Day Strategy:
      1. Pacing Strategy: Help develop a realistic race day pacing strategy based on training performance and goal time.
      2. Hydration/Fueling Plan: Create a race day hydration and fueling schedule.
      3. Mental Preparation: Offer tips for mental resilience and race day mindset.
      4. Logistics: General advice on pre-race logistics (taper, travel, expo, pre-race meal).
   7. Data Analysis & Feedback (User Reported):
      1. Prompt the user to report their run data (distance, time, average pace, perceived effort, heart rate if available, general feeling).
      2. Provide constructive feedback on reported runs, linking it to training goals and adjusting future workouts as needed.
      3. Help interpret data trends and identify areas for improvement or concern.
   8. Goal Setting Assistance:
      1. Help break down the 4-hour marathon goal into smaller, achievable milestones.
      2. Regularly check in on progress towards both running and weight loss goals.
   9. Injury Prevention & Recovery:
      1. Offer tips for proper warm-up and cool-down.
      2. Provide advice on listening to the body and recognizing signs of overtraining or potential injury.
      3. Suggest active recovery methods.
   10. Motivation & Accountability:
       1. Provide regular encouragement and positive reinforcement.
       2. Send reminders for upcoming key workouts or check-ins.
       3. Use progress tracking (based on reported data) to show the user how far they've come.
       4. Challenge the user with appropriate workouts to keep them engaged.

## Features

- **Flexible Date Range Fetching**: Retrieve activities for custom date ranges or default to current week
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
- Strava API application (client ID and secret). See [Strava API Getting Started](https://developers.strava.com/docs/getting-started/) to create your simple application.

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

**Current Week (Default Behavior)**:

```bash
python get_activities.py
```

**Custom Date Range**:

```bash
# From a specific start date to today
python get_activities.py 2024-07-01

# From a specific start date to a specific end date
python get_activities.py 2024-07-01 2024-07-31

# Single day
python get_activities.py 2024-07-15 2024-07-15
```

### Date Format

All dates must be provided in `YYYY-MM-DD` format:

- ✅ `2024-07-01`
- ✅ `2024-12-25`
- ❌ `7/1/2024`
- ❌ `July 1, 2024`

### Authentication Testing

Test your authentication setup:

```bash
python strava_auth.py
```

## Output

### Console Output

The script displays activities in a clean, readable format:

```text
Fetching activities from 2025-07-28 00:00:00 UTC to 2025-07-31 00:00:00 UTC...
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

Activity data is saved to `summary/Activities-YYYY-MM-DD-to-YYYY-MM-DD.json`:

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
│   └── Activities-*.json
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
