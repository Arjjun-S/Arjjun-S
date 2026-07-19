import urllib.request
import json
import re

query = """
query userProfileAndContest($username: String!) {
  matchedUser(username: $username) {
    submitStats {
      acSubmissionNum {
        difficulty
        count
      }
    }
    userCalendar {
      streak
    }
  }
  userContestRanking(username: $username) {
    rating
  }
}
"""

url = "https://leetcode.com/graphql/"
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

payload = {
    "query": query,
    "variables": {"username": "ArjjunS"}
}
data_bytes = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

try:
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        data = res_data.get("data", {})
        
        # Parse stats
        matched_user = data.get("matchedUser")
        total_solved = 0
        streak = 0
        if matched_user:
            ac_submissions = matched_user.get("submitStats", {}).get("acSubmissionNum", [])
            for sub in ac_submissions:
                if sub.get("difficulty") == "All":
                    total_solved = sub.get("count", 0)
            user_calendar = matched_user.get("userCalendar")
            if user_calendar:
                streak = user_calendar.get("streak", 0)
        
        contest_ranking = data.get("userContestRanking")
        contest_rating = "N/A"
        if contest_ranking and contest_ranking.get("rating") is not None:
            contest_rating = str(round(contest_ranking.get("rating")))
        
        # Read README.md
        with open("README.md", "r") as f:
            readme = f.read()
            
        # Create updated stats text
        new_stats = f"**Total Solved:** {total_solved} &nbsp;&nbsp;&nbsp;&nbsp; **Contest Rating:** {contest_rating} &nbsp;&nbsp;&nbsp;&nbsp; **Current Streak:** {streak} days"
        
        # Replace between placeholder comments
        pattern = r"(<!-- leetcode-stats-start -->).*?(<!-- leetcode-stats-end -->)"
        replacement = f"\\1\\n  {new_stats}\\n  \\2"
        updated_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)
        
        with open("README.md", "w") as f:
            f.write(updated_readme)
            
        print("Successfully updated LeetCode statistics in README.md")
except Exception as e:
    print(f"Error fetching/updating LeetCode stats: {e}")
    exit(1)
