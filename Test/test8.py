from scrapers import scrape_scores, scrape_commentary_with_transform

# Example URL of the webpage containing the commentary
commentary_url = "https://africa.espn.com/football/commentary/_/gameId/674192"

# List of team names involved in the match
team_names = ['Alaves', 'Real Sociedad']
match_comments = scrape_commentary_with_transform(commentary_url, team_names)

print(match_comments)