# get_activities.py
#
# Description:
# This script fetches your Strava activities for a specified date range or the current week.
# For runs, it prints a Markdown-formatted summary to the console (for easy copy-pasting
# into an AI chat) and saves detailed data to a JSON file. For workouts, it displays
# a simple summary and also saves to the JSON file.
#
# Requirements:
#   - Python 3
#   - 'requests' library (pip install requests)
#   - 'python-dotenv' library (pip install python-dotenv)
#   - The `strava_auth.py` script must be in the same directory
#   - A `.env` file with Strava API credentials must be set up
#
# Setup:
#   1. Ensure your .env file contains the required Strava API credentials
#   2. Run the strava_auth.py script first to verify authentication
#
# Usage:
#   Run from your terminal:
#   python get_activities.py                           # Current week (default behavior)
#   python get_activities.py 2024-07-01               # From July 1, 2024 to today
#   python get_activities.py 2024-07-01 2024-07-31    # From July 1 to July 31, 2024
#
# Output:
#   - Console: Markdown-formatted activity summaries
#   - File: JSON file in ./summary/ folder with all activity data
#

import json
import os
import requests
import sys
from datetime import datetime, timedelta, time

# Import the function from our authentication script
from strava_auth import get_access_token

def parse_date_argument(date_str):
    """
    Parses a date string in YYYY-MM-DD format.
    
    Args:
        date_str (str): Date string in YYYY-MM-DD format
        
    Returns:
        datetime: Parsed datetime object or None if invalid
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None

def format_pace(seconds_per_meter):
    """
    Converts pace from seconds per meter to a MM:SS/km string.
    
    Args:
        seconds_per_meter (float): Pace in seconds per meter
        
    Returns:
        str: Formatted pace string (MM:SS)
    """
    if seconds_per_meter is None or seconds_per_meter <= 0:
        return "00:00"
    
    seconds_per_km = seconds_per_meter * 1000
    minutes = int(seconds_per_km // 60)
    seconds = int(seconds_per_km % 60)
    return f"{minutes:02d}:{seconds:02d}"

def format_run_for_gemini(detailed_activity):
    """
    Formats the run data into a clean Markdown string for AI analysis.
    
    Args:
        detailed_activity (dict): Detailed activity data from Strava API
        
    Returns:
        str: Markdown-formatted activity summary
    """
    # --- Build the Summary ---
    summary_lines = ["### Activity Summary"]
    distance_km = detailed_activity.get('distance', 0) / 1000.0
    moving_time = timedelta(seconds=detailed_activity.get('moving_time', 0))
    elapsed_time = timedelta(seconds=detailed_activity.get('elapsed_time', 0))
    avg_speed = detailed_activity.get('average_speed', 0)
    pace = format_pace(1 / avg_speed) if avg_speed > 0 else "00:00"
    calories = detailed_activity.get('calories', 0)

    summary_lines.append(f"- **Distance**: {distance_km:.2f} km")
    summary_lines.append(f"- **Moving Time**: {moving_time}")
    summary_lines.append(f"- **Average Pace**: {pace} /km")
    summary_lines.append(f"- **Calories**: {int(calories)}")

    # --- Build the Splits Table ---
    splits = detailed_activity.get("splits_metric")
    if splits:
        summary_lines.append("\n### Splits Breakdown")
        summary_lines.append("| Split | Pace (/km) | Distance (km) | Time    | Avg HR | Elev Diff (m) |")
        summary_lines.append("|-------|------------|---------------|---------|--------|---------------|")
        for split in splits:
            split_num = split.get('split')
            split_pace = format_pace(1 / split.get('average_speed', 0)) if split.get('average_speed') else "00:00"
            split_dist_km = f"{split.get('distance', 0) / 1000.0:.2f}"
            split_time = str(timedelta(seconds=split.get('moving_time', 0)))
            split_hr = str(int(split.get('average_heartrate', 0))) if split.get('average_heartrate') else "N/A"
            split_elev = f"{split.get('elevation_difference', 0):.1f}"
            summary_lines.append(f"| {split_num:<5} | {split_pace:<10} | {split_dist_km:<13} | {split_time:<7} | {split_hr:<6} | {split_elev:<13} |")
    
    return "\n".join(summary_lines)

def prepare_run_data(detailed_activity):
    """
    Prepares run data for JSON storage in a format similar to console output.
    
    Args:
        detailed_activity (dict): Detailed activity data from Strava API
        
    Returns:
        dict: Structured run data for JSON storage
    """
    activity_date = datetime.fromisoformat(detailed_activity.get('start_date')).strftime('%Y-%m-%d')
    activity_id = detailed_activity.get('id')
    activity_name = detailed_activity.get('name')
    
    # Summary data
    distance_km = detailed_activity.get('distance', 0) / 1000.0
    moving_time_str = str(timedelta(seconds=detailed_activity.get('moving_time', 0)))
    elapsed_time_str = str(timedelta(seconds=detailed_activity.get('elapsed_time', 0)))
    avg_speed = detailed_activity.get('average_speed', 0)
    pace = format_pace(1 / avg_speed) if avg_speed > 0 else "00:00"
    calories = int(detailed_activity.get('calories', 0))
    
    run_data = {
        "activity_type": "Run",
        "activity_id": activity_id,
        "activity_name": activity_name,
        "date": activity_date,
        "summary": {
            "distance_km": round(distance_km, 2),
            "moving_time": moving_time_str,
            "elapsed_time": elapsed_time_str,
            "average_pace_per_km": pace,
            "calories": calories
        },
        "splits": []
    }
    
    # Splits data
    splits = detailed_activity.get("splits_metric")
    if splits:
        for split in splits:
            split_pace = format_pace(1 / split.get('average_speed', 0)) if split.get('average_speed') else "00:00"
            split_dist_km = round(split.get('distance', 0) / 1000.0, 2)
            split_time = str(timedelta(seconds=split.get('moving_time', 0)))
            split_hr = int(split.get('average_heartrate', 0)) if split.get('average_heartrate') else None
            split_elev = round(split.get('elevation_difference', 0), 1)
            
            run_data["splits"].append({
                "split_number": split.get('split'),
                "pace_per_km": split_pace,
                "distance_km": split_dist_km,
                "time": split_time,
                "avg_heart_rate": split_hr,
                "elevation_difference_m": split_elev
            })
    
    return run_data

def prepare_workout_data(activity_summary):
    """
    Prepares workout data for JSON storage.
    
    Args:
        activity_summary (dict): Activity summary data from Strava API
        
    Returns:
        dict: Structured workout data for JSON storage
    """
    activity_date = datetime.fromisoformat(activity_summary.get('start_date')).strftime('%Y-%m-%d')
    activity_id = activity_summary.get('id')
    activity_name = activity_summary.get('name')
    elapsed_time_str = str(timedelta(seconds=activity_summary.get('elapsed_time', 0)))
    
    workout_data = {
        "activity_type": "Workout",
        "activity_id": activity_id,
        "activity_name": activity_name,
        "date": activity_date,
        "summary": {
            "total_time": elapsed_time_str
        }
    }
    
    return workout_data

def save_activities_to_json(all_activities_data, start_date, end_date):
    """
    Saves all activities data to a single JSON file in the summary folder.
    
    Args:
        all_activities_data (list): List of activity data dictionaries
        start_date (datetime): Start date for the period
        end_date (datetime): End date for the period
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Create the summary folder if it doesn't exist
    summary_folder = "summary"
    os.makedirs(summary_folder, exist_ok=True)
        
    # Generate filename based on date range
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    if start_str == end_str:
        filename = f"Activities-{start_str}.json"
    else:
        filename = f"Activities-{start_str}-to-{end_str}.json"
    
    # Create full path to file in summary folder
    filepath = os.path.join(summary_folder, filename)
    
    json_data = {
        "period": f"{start_str} to {end_str}",
        "generated_at": datetime.now().isoformat(),
        "total_activities": len(all_activities_data),
        "activities": all_activities_data
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n  -> Successfully saved all activities to '{filepath}'")
        return True

    except Exception as e:
        print(f"\n  -> Error saving to JSON: {e}")
        return False

def get_activities_for_period(start_date=None, end_date=None):
    """
    Main function that fetches activities for a specified period or current week,
    prints Markdown to console, and saves all data to JSON.
    
    Args:
        start_date (datetime, optional): Start date for activity search. 
                                       Defaults to start of current week.
        end_date (datetime, optional): End date for activity search.
                                     Defaults to current date/time.
    """
    access_token = get_access_token()
    if not access_token:
        print("Could not retrieve access token. Aborting.")
        return

    # Set default date range if not provided (current week behavior)
    if start_date is None:
        today_local = datetime.now()
        start_of_week_date = today_local - timedelta(days=today_local.weekday())
        start_date = datetime.combine(start_of_week_date.date(), time.min)
    else:
        # Set to beginning of the specified start date
        start_date = datetime.combine(start_date.date(), time.min)
    
    if end_date is None:
        end_date = datetime.now()
    else:
        # Set to end of the specified end date
        end_date = datetime.combine(end_date.date(), time.max)

    after_timestamp = int(start_date.timestamp())
    before_timestamp = int(end_date.timestamp())

    print(f"Fetching activities from {start_date.strftime('%Y-%m-%d %H:%M:%S')} to {end_date.strftime('%Y-%m-%d %H:%M:%S')}...")

    list_activities_url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'before': before_timestamp, 'after': after_timestamp, 'per_page': 200}

    all_activities_data = []

    try:
        response = requests.get(list_activities_url, headers=headers, params=params)
        response.raise_for_status()
        activities = response.json()

        if not activities:
            print("\nNo activities found for the specified period.")
            return

        print(f"\nFound {len(activities)} total activities. Processing...")
        print("-" * 40)

        for activity_summary in activities:
            activity_type = activity_summary.get("type")
            activity_id = activity_summary.get("id")
            activity_name = activity_summary.get('name')
            activity_date = datetime.fromisoformat(activity_summary.get('start_date')).strftime('%Y-%m-%d')

            if activity_type == "Run":
                print(f"\n--- Processing Run: '{activity_name}' on {activity_date} ---")
                
                get_activity_url = f"https://www.strava.com/api/v3/activities/{activity_id}"
                detailed_response = requests.get(get_activity_url, headers=headers)
                detailed_activity = detailed_response.json()

                # Print Markdown formatted output for easy copy-pasting
                markdown_output = format_run_for_gemini(detailed_activity)
                print(markdown_output)

                # Prepare data for JSON
                run_data = prepare_run_data(detailed_activity)
                all_activities_data.append(run_data)
                print("-" * 40)

            elif activity_type == "Workout":
                print(f"\n--- Processing Workout: '{activity_name}' on {activity_date} ---")
                elapsed_time = str(timedelta(seconds=activity_summary.get('elapsed_time', 0)))
                print(f"  - Type: Workout")
                print(f"  - Total Time: {elapsed_time}")
                
                # Prepare data for JSON
                workout_data = prepare_workout_data(activity_summary)
                all_activities_data.append(workout_data)
                print("-" * 40)

            else:
                print(f"\n--- Skipping '{activity_name}' (Type: {activity_type}) on {activity_date} ---")
                print("-" * 40)

        # Save all activities to JSON file
        if all_activities_data:
            save_activities_to_json(all_activities_data, start_date, end_date)
        else:
            print("\nNo runs or workouts found to save.")

    except requests.exceptions.RequestException as e:
        print(f"\nAPI request failed: {e}")
        if e.response:
            print(f"Response Content: {e.response.text}")

def main():
    """
    Main entry point that handles command line arguments for date range.
    
    Usage:
        python get_activities.py                           # Current week (default)
        python get_activities.py 2024-07-01               # From July 1, 2024 to today
        python get_activities.py 2024-07-01 2024-07-31    # From July 1 to July 31, 2024
    """
    start_date = None
    end_date = None
    
    if len(sys.argv) > 1:
        # Parse start date
        start_date = parse_date_argument(sys.argv[1])
        if start_date is None:
            print(f"Error: Invalid start date '{sys.argv[1]}'. Please use YYYY-MM-DD format.")
            print("Usage:")
            print("  python get_activities.py                           # Current week")
            print("  python get_activities.py 2024-07-01               # From July 1, 2024 to today")
            print("  python get_activities.py 2024-07-01 2024-07-31    # From July 1 to July 31, 2024")
            return
    
    if len(sys.argv) > 2:
        # Parse end date
        end_date = parse_date_argument(sys.argv[2])
        if end_date is None:
            print(f"Error: Invalid end date '{sys.argv[2]}'. Please use YYYY-MM-DD format.")
            print("Usage:")
            print("  python get_activities.py                           # Current week")
            print("  python get_activities.py 2024-07-01               # From July 1, 2024 to today")
            print("  python get_activities.py 2024-07-01 2024-07-31    # From July 1 to July 31, 2024")
            return
    
    if len(sys.argv) > 3:
        print("Error: Too many arguments provided.")
        print("Usage:")
        print("  python get_activities.py                           # Current week")
        print("  python get_activities.py 2024-07-01               # From July 1, 2024 to today")
        print("  python get_activities.py 2024-07-01 2024-07-31    # From July 1 to July 31, 2024")
        return
    
    # Validate date range if both dates provided
    if start_date and end_date and start_date > end_date:
        print("Error: Start date cannot be later than end date.")
        return
    
    get_activities_for_period(start_date, end_date)

# Maintain backwards compatibility
def get_weekly_activities():
    """
    Backwards compatibility function that maintains the original weekly behavior.
    """
    get_activities_for_period()

if __name__ == "__main__":
    main()