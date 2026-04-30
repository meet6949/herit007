import requests
import os
from datetime import datetime
import random

# Configuration
USERNAME = "herit007"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OUTPUT_FILE = "dist/space-contribution-graph.svg"

# Colors
SPACE_BG = "#0d1117"
STAR_COLOR = "#ffffff"
ROCKET_COLOR = "#7c3aed"
PROJECTILE_COLOR = "#22c55e"

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
    
    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"userName": USERNAME}},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
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
    except Exception as e:
        print(f"Error fetching contributions: {e}")
        return []

def get_color_for_count(count):
    """Return color based on contribution count"""
    if count == 0:
        return "#161b22"
    elif count < 3:
        return "#0e4429"
    elif count < 6:
        return "#006d32"
    elif count < 9:
        return "#26a641"
    else:
        return "#39d353"

def generate_svg(contributions):
    """Generate space-themed SVG with rocket shooting at contributions"""
    
    # SVG dimensions
    width = 900
    height = 220
    cell_size = 10
    cell_gap = 3
    
    # Grid settings
    grid_start_x = 60
    grid_start_y = 30
    rocket_y = height - 40
    
    # Start SVG with animations
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="rocketGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#7c3aed;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#a855f7;stop-opacity:1" />
        </linearGradient>
        
        <linearGradient id="flameGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#fbbf24;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#f97316;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#ef4444;stop-opacity:1" />
        </linearGradient>
    </defs>
    
    <style>
        @keyframes rocket-move {{
            0% {{ transform: translateX(0px); }}
            100% {{ transform: translateX({width - 100}px); }}
        }}
        
        @keyframes shoot {{
            0% {{ 
                opacity: 0; 
                cy: {rocket_y - 10};
            }}
            10% {{ 
                opacity: 1; 
                cy: {rocket_y - 10};
            }}
            100% {{ 
                opacity: 1; 
                cy: var(--target-y);
            }}
        }}
        
        @keyframes flame-flicker {{
            0%, 100% {{ opacity: 0.8; transform: scaleX(1); }}
            50% {{ opacity: 1; transform: scaleX(1.3); }}
        }}
        
        @keyframes star-twinkle {{
            0%, 100% {{ opacity: 0.3; }}
            50% {{ opacity: 1; }}
        }}
        
        @keyframes projectile-glow {{
            0%, 100% {{ filter: brightness(1); }}
            50% {{ filter: brightness(1.5); }}
        }}
        
        .rocket-group {{
            animation: rocket-move 12s linear infinite;
        }}
        
        .flame {{
            animation: flame-flicker 0.2s ease-in-out infinite;
        }}
        
        .star {{
            animation: star-twinkle 3s ease-in-out infinite;
        }}
        
        .projectile {{
            animation: shoot 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards,
                       projectile-glow 0.3s ease-in-out infinite;
        }}
    </style>
    
    <!-- Space Background -->
    <rect width="{width}" height="{height}" fill="{SPACE_BG}"/>
    
    <!-- Background Stars -->
'''
    
    # Generate random stars
    random.seed(42)
    for _ in range(80):
        x = random.randint(0, width)
        y = random.randint(0, height - 60)
        size = random.uniform(0.5, 2.5)
        delay = random.uniform(0, 3)
        svg += f'    <circle cx="{x}" cy="{y}" r="{size}" fill="{STAR_COLOR}" class="star" style="animation-delay: {delay}s;"/>\n'
    
    # Contribution Grid
    svg += '\n    <!-- Contribution Grid -->\n    <g id="contribution-grid">\n'
    
    # Get last 53 weeks (full year view)
    recent_contributions = contributions[-371:] if len(contributions) > 371 else contributions
    
    day_index = 0
    projectile_index = 0
    
    for week in range(53):
        for day in range(7):
            if day_index >= len(recent_contributions):
                break
            
            contrib = recent_contributions[day_index]
            count = contrib["count"]
            
            x = grid_start_x + (week * (cell_size + cell_gap))
            y = grid_start_y + (day * (cell_size + cell_gap))
            
            color = get_color_for_count(count)
            
            # Draw contribution cell
            svg += f'        <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{color}" rx="2"/>\n'
            
            # Add projectile for non-zero contributions
            if count > 0:
                # Calculate timing based on position
                delay = (week * 0.12) + (day * 0.015)
                target_y = y + (cell_size / 2)
                
                svg += f'        <circle class="projectile" cx="{x + cell_size/2}" r="3" fill="{PROJECTILE_COLOR}" style="--target-y: {target_y}px; animation-delay: {delay}s;"/>\n'
                projectile_index += 1
            
            day_index += 1
        
        if day_index >= len(recent_contributions):
            break
    
    svg += '    </g>\n\n'
    
    # Rocket
    svg += f'''    <!-- Rocket -->
    <g class="rocket-group">
        <!-- Rocket Body -->
        <path d="M 30 {rocket_y} L 55 {rocket_y - 12} L 65 {rocket_y - 12} L 65 {rocket_y + 12} L 55 {rocket_y + 12} Z" 
              fill="url(#rocketGradient)" stroke="#a855f7" stroke-width="1"/>
        
        <!-- Rocket Nose -->
        <path d="M 65 {rocket_y - 12} L 80 {rocket_y} L 65 {rocket_y + 12} Z" 
              fill="#c084fc"/>
        
        <!-- Window -->
        <circle cx="58" cy="{rocket_y}" r="5" fill="#1e293b" opacity="0.7"/>
        <circle cx="58" cy="{rocket_y}" r="3" fill="#60a5fa" opacity="0.5"/>
        
        <!-- Wing Top -->
        <path d="M 35 {rocket_y - 12} L 35 {rocket_y - 22} L 50 {rocket_y - 12} Z" 
              fill="#6366f1"/>
        
        <!-- Wing Bottom -->
        <path d="M 35 {rocket_y + 12} L 35 {rocket_y + 22} L 50 {rocket_y + 12} Z" 
              fill="#6366f1"/>
        
        <!-- Flames -->
        <g class="flame">
            <ellipse cx="22" cy="{rocket_y}" rx="15" ry="6" fill="url(#flameGradient)" opacity="0.9"/>
            <ellipse cx="18" cy="{rocket_y}" rx="12" ry="5" fill="#fbbf24" opacity="0.7"/>
        </g>
        
        <!-- Flame Particles -->
        <circle cx="10" cy="{rocket_y - 3}" r="2" fill="#fbbf24" opacity="0.6" class="flame"/>
        <circle cx="8" cy="{rocket_y + 3}" r="2" fill="#f97316" opacity="0.6" class="flame"/>
        <circle cx="12" cy="{rocket_y}" r="1.5" fill="#ef4444" opacity="0.8" class="flame"/>
    </g>
    
    <!-- Title Text -->
    <text x="{width/2}" y="{height - 8}" text-anchor="middle" fill="#8b949e" font-family="'Segoe UI', Arial, sans-serif" font-size="12">
        🚀 Contribution Journey • {len([c for c in recent_contributions if c['count'] > 0])} active days
    </text>
    
</svg>'''
    
    return svg

def main():
    print("🚀 Starting space contribution graph generator...")
    print(f"👤 Username: {USERNAME}")
    
    # Fetch contributions
    print("📊 Fetching contribution data from GitHub...")
    contributions = fetch_contributions()
    
    if not contributions:
        print("❌ No contributions found or error occurred")
        return
    
    total_contributions = sum(c['count'] for c in contributions)
    print(f"✅ Found {len(contributions)} days with {total_contributions} total contributions")
    
    # Generate SVG
    print("🎨 Generating SVG...")
    svg_content = generate_svg(contributions)
    
    # Create output directory
    os.makedirs("dist", exist_ok=True)
    
    # Write SVG file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"✅ Space contribution graph generated successfully!")
    print(f"📁 Output: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
