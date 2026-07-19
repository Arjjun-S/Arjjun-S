import urllib.request
import json
import re

# ----------------- LEETCODE STATS FETCHING -----------------
leetcode_query = """
query userProfileCalendar($username: String!) {
  matchedUser(username: $username) {
    userCalendar {
      streak
      submissionCalendar
    }
  }
  userContestRanking(username: $username) {
    rating
    topPercentage
  }
}
"""

leetcode_url = "https://leetcode.com/graphql/"
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

streak = 0
max_streak = 0
contest_rating = "N/A"
top_percentage = "N/A"

try:
    payload = {
        "query": leetcode_query,
        "variables": {"username": "ArjjunS"}
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(leetcode_url, data=data_bytes, headers=headers, method="POST")
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        data = res_data.get("data", {})
        
        matched_user = data.get("matchedUser")
        if matched_user:
            user_calendar = matched_user.get("userCalendar", {})
            current_streak = user_calendar.get("streak", 0)
            
            # Calculate max streak from submissionCalendar
            sub_cal_str = user_calendar.get("submissionCalendar", "{}")
            sub_cal = json.loads(sub_cal_str)
            timestamps = sorted([int(k) for k in sub_cal.keys()])
            
            computed_max = 0
            curr = 0
            prev_day = None
            for t in timestamps:
                day = t // 86400
                if prev_day is None:
                    curr = 1
                else:
                    if day - prev_day == 1:
                        curr += 1
                    elif day - prev_day > 1:
                        curr = 1
                if curr > computed_max:
                    computed_max = curr
                prev_day = day
            
            max_streak = max(computed_max, current_streak)
        
        contest_ranking = data.get("userContestRanking")
        if contest_ranking:
            if contest_ranking.get("rating") is not None:
                contest_rating = str(round(contest_ranking.get("rating")))
            if contest_ranking.get("topPercentage") is not None:
                top_percentage = f"{contest_ranking.get('topPercentage')}%"
                
    print("LeetCode stats successfully fetched.")
except Exception as e:
    print(f"Error fetching LeetCode stats: {e}")

# ----------------- UPDATE README.MD -----------------
try:
    with open("README.md", "r") as f:
        readme = f.read()
    
    # Update LeetCode stats section
    leetcode_stats_text = f"<b>Contest Rating:</b> {contest_rating} &nbsp;&nbsp;&nbsp;&nbsp; <b>Max Streak:</b> {max_streak} days &nbsp;&nbsp;&nbsp;&nbsp; <b>Top Percentage:</b> {top_percentage}"
    readme = re.sub(
        r"(<!-- leetcode-stats-start -->).*?(<!-- leetcode-stats-end -->)",
        f"\\1\\n  {leetcode_stats_text}\\n  \\2",
        readme,
        flags=re.DOTALL
    )
        
    with open("README.md", "w") as f:
        f.write(readme)
        
    print("README.md successfully updated with new stats.")
except Exception as e:
    print(f"Error updating README.md: {e}")
    exit(1)
