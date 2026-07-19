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

total_solved = 0
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

# ----------------- HACKERRANK BADGES FETCHING -----------------
hackerrank_url = "https://www.hackerrank.com/rest/hackers/suresharjjun/badges"
hackerrank_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

badge_mapping = {
    "java": {"label": "Java", "logo": "java", "color": "007396"},
    "python": {"label": "Python", "logo": "python", "color": "3776AB"},
    "sql": {"label": "SQL", "logo": "sqlite", "color": "4479A1"},
    "c": {"label": "C", "logo": "c", "color": "A8B9CC"},
    "cpp": {"label": "C++", "logo": "cplusplus", "color": "00599C"},
    "javascript": {"label": "JavaScript", "logo": "javascript", "color": "F7DF1E"},
    "algorithms": {"label": "Algorithms", "logo": "hackerrank", "color": "2EC866"},
    "data-structures": {"label": "Data Structures", "logo": "hackerrank", "color": "2EC866"},
}

hackerrank_badges_html = ""

try:
    req = urllib.request.Request(hackerrank_url, headers=hackerrank_headers)
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        models = res_data.get("models", [])
        
        badges_list = []
        for model in models:
            badge_type = model.get("badge_type", "")
            badge_name = model.get("badge_name", "")
            stars = model.get("stars", 0)
            
            # Map parameters
            mapping = badge_mapping.get(badge_type, {"label": badge_name, "logo": "hackerrank", "color": "2EC866"})
            label = mapping["label"]
            logo = mapping["logo"]
            color = mapping["color"]
            
            star_label = f"{stars}_Stars" if stars > 1 else f"{stars}_Star"
            badge_text = f"{label}-{star_label}-{color}"
            badge_url = f"https://img.shields.io/badge/{badge_text}?style=flat-square&logo={logo}&logoColor=white"
            
            badges_list.append(
                f'<a href="https://www.hackerrank.com/profile/suresharjjun" target="_blank">\n'
                f'    <img src="{badge_url}" alt="{label}" />\n'
                f'  </a>'
            )
        
        if badges_list:
            # Join with markdown spaces
            hackerrank_badges_html = "\n  &nbsp;&nbsp;&nbsp;&nbsp;\n  " + "\n  &nbsp;&nbsp;&nbsp;&nbsp;\n  ".join(badges_list)
            
    print("HackerRank badges successfully fetched.")
except Exception as e:
    print(f"Error fetching HackerRank badges: {e}")

# ----------------- UPDATE README.MD -----------------
try:
    with open("README.md", "r") as f:
        readme = f.read()
    
    # 1. Update LeetCode stats section
    leetcode_stats_text = f"<b>Contest Rating:</b> {contest_rating} &nbsp;&nbsp;&nbsp;&nbsp; <b>Max Streak:</b> {max_streak} days &nbsp;&nbsp;&nbsp;&nbsp; <b>Top Percentage:</b> {top_percentage}"
    readme = re.sub(
        r"(<!-- leetcode-stats-start -->).*?(<!-- leetcode-stats-end -->)",
        f"\\1\\n  {leetcode_stats_text}\\n  \\2",
        readme,
        flags=re.DOTALL
    )
    
    # 2. Update HackerRank badges section
    if hackerrank_badges_html:
        readme = re.sub(
            r"(<!-- hackerrank-badges-start -->).*?(<!-- hackerrank-badges-end -->)",
            f"\\1{hackerrank_badges_html}\\n  \\2",
            readme,
            flags=re.DOTALL
        )
        
    with open("README.md", "w") as f:
        f.write(readme)
        
    print("README.md successfully updated with new stats and badges.")
except Exception as e:
    print(f"Error updating README.md: {e}")
    exit(1)
