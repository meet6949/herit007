import requests
import os
from datetime import datetime, timedelta
import json

# Configuration
USERNAME = "herit007"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OUTPUT_FILE = "dist/space-contribution-graph.svg"

# Colors
SPACE_BG = "#0d1117"
STAR_COLOR = "#ffffff"
ROCKET_COLOR = "#7c3aed"
PROJECTILE_COLOR = "#22c55e"
GRID_COLOR = "#161b22"

def fetch_contributions():
    """Fetch contribution data from GitHub GraphQL API"""
    query = """
    query($userName:String!) {
      user(login: $userName){
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    
    headers = {"Authorization": f"bearer {GITHUB_TOKEN}"}
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"userName": USERNAME}},
        headers=headers
    )
    
    data = response.json()
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    
    # Flatten to get all days
    contributions = []
    for week in weeks:
        for day in week["contributionDays"]:
            contributions.append({
                "date": day["date"],
                "count": day["contributionCount"]
            })
    
    return contributions

def generate_svg(contributions):
    """Generate space-themed SVG with rocket and projectiles"""
    
    # SVG dimensions
    width = 800
    height = 200
    cell_size = 11
    cell_gap = 3
    
    # Calculate grid dimensions (52 weeks × 7 days)
    weeks = 52
    days = 7
    
    # Start SVG
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <style>
        @keyframes rocket {{
            0% {{ transform: translateX(800px); }}
            100% {{ transform: translateX(-100px); }}
        }}
        
        @keyframes shoot {{
            0% {{ opacity: 0; transform: translateY(0); }}
            20% {{ opacity: 1; }}
            100% {{ opacity: 1; transform: translateY(var(--target-y)); }}
        }}
        
        .rocket {{
            animation: rocket 8s linear infinite;
        }}
        
        .projectile {{
            animation: shoot 0.5s ease-out forwards;
            animation-delay: var(--delay);
        }}
        
        .star {{
            animation: twinkle 3s ease-in-out infinite;
            animation-delay: var(--twinkle-delay);
        }}
        
        @keyframes twinkle {{
            0%, 100% {{ opacity: 0.3; }}
            50% {{ opacity: 1; }}
        }}
    </style>
    
    <!-- Space background -->
    <rect width="{width}" height="{height}" fill="{SPACE_BG}"/>
    
    <!-- Stars -->
'''
    
    # Add random stars
    import random
    random.seed(42)
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height - 50)
        size = random.uniform(0.5, 2)
        delay = random.uniform(0, 3)
        svg += f'    <circle cx="{x}" cy="{y}" r="{size}" fill="{STAR_COLOR}" class="star" style="--twinkle-delay: {delay}s;"/>\n'
    
    # Add contribution grid
    svg += '\n    <!-- Contribution Grid -->\n'
    
    grid_start_x = 50
    grid_start_y = 20
    
    # Recent year of contributions (last 365 days)
    recent_contributions = contributions[-365:] if len(contributions) > 365 else contributions
    
    day_index = 0
    for week in range(weeks):
        for day in range(days):
            if day_index >= len(recent_contributions):
                break
            
            contrib = recent_contributions[day_index]
            count = contrib["count"]
            
            x = grid_start_x + (week * (cell_size + cell_gap))
            y = grid_start_y + (day * (cell_size + cell_gap))
            
            # Color based on contribution count
            if count == 0:
                color = GRID_COLOR
            elif count < 5:
                color = "#0e4429"
            elif count < 10:
                color = "#006d32"
            elif count < 15:
                color = "#26a641"
            else:
                color = "#39d353"
            
            svg += f'    <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{color}" rx="2"/>\n'
            
            # Add projectile if there's a contribution
            if count > 0:
                rocket_y = height - 30
                target_y = y - rocket_y
                delay = (week * 0.15) + (day * 0.02)
                
                svg += f'    <circle cx="{x + cell_size/2}" cy="{rocket_y}" r="2" fill="{PROJECTILE_COLOR}" class="projectile" style="--target-y: {target_y}px; --delay: {delay}s;"/>\n'
            
            day_index += 1
        
        if day_index >= len(recent_contributions):
            break
    
    # Add rocket at bottom
    rocket_y = height - 30
    svg += f'''
    <!-- Rocket -->
    <g class="rocket">
        <path d="M 0 {rocket_y} L 20 {rocket_y - 15} L 20 {rocket_y + 15} Z" fill="{ROCKET_COLOR}"/>
        <circle cx="22" cy="{rocket_y}" r="6" fill="{ROCKET_COLOR}"/>
        <path d="M 0 {rocket_y - 5} L -10 {rocket_y - 15} L 0 {rocket_y - 10} Z" fill="#ef4444"/>
        <path d="M 0 {rocket_y + 5} L -10 {rocket_y + 15} L 0 {rocket_y + 10} Z" fill="#ef4444"/>
        <circle cx="-5" cy="{rocket_y}" r="3" fill="#fbbf24" opacity="0.7"/>
    </g>
    
</svg>'''
    
    return svg

def main():
    print("Fetching contribution data...")
    contributions = fetch_contributions()
    
    print(f"Found {len(contributions)} contribution days")
    print("Generating SVG...")
    
    svg_content = generate_svg(contributions)
    
    # Create dist directory if it doesn't exist
    os.makedirs("dist", exist_ok=True)
    
    # Write SVG file
    with open(OUTPUT_FILE, "w") as f:
        f.write(svg_content)
    
    print(f"✅ Space contribution graph generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
