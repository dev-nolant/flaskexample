import subprocess
import os
from github import Github

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Run fin_playerSeasonTotalScraper.py
result1 = subprocess.run(["python", "fin_playerSeasonTotalScraper.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Check if fin_playerSeasonTotalScraper.py succeeded
if result1.returncode == 0:
    print("fin_playerSeasonTotalScraper.py completed successfully.")
    
    # Run scrapegamelog.py
    result2 = subprocess.run(["python", "scrapegamelog.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result2.returncode == 0:
        print("scrapegamelog.py completed successfully.")
        
        # Upload combined_players_data.json to GitHub
        github_token = os.getenv("GITHUB_TOKEN")
        github_repo = os.getenv("GITHUB_REPO")
        github_filepath = "combined_players_data.json"
        
        if github_token and github_repo:
        
            g = Github(github_token)
            repo = g.get_repo(github_repo)
            with open(github_filepath, "r") as file:
                content = file.read()
            repo.create_file(github_filepath, "Updated combined player data", content, branch="main")
            print("Uploaded combined_players_data.json to GitHub.")
        else:
            print("GitHub token or repo information not provided in .env")
    else:
        print("Error: scrapegamelog.py failed.")
        print(result2.stderr)
else:
    print("Error: fin_playerSeasonTotalScraper.py failed.")
    print(result1.stderr)
