import requests
import os
import random

# Configuration
USERNAME = "herit007"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OUTPUT_FILE = "dist/space-contribution-graph.svg"

# Colors
SPACE_BG = "#0d1117"
STAR_COLOR = "#ffffff"
SPACESHIP_COLOR = "#7c3aed"
LASER_COLOR = "#22c55e"
LASER_GLOW = "#4ade80"

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
    """Generate space-themed SVG with spaceship firing at contributions"""
    
    # SVG dimensions
    width = 920
    height = 240
    cell_size = 10
    cell_gap = 3
    
    # Grid settings
    grid_start_x = 60
    grid_start_y = 30
    spaceship_y = height - 50
    
    # Get last 53 weeks
    recent_contributions = contributions[-371:] if len(contributions) > 371 else contributions
    
    # Collect contribution positions
    contrib_positions = []
    day_index = 0
    
    for week in range(53):
        for day in range(7):
            if day_index >= len(recent_contributions):
                break
            
            contrib = recent_contributions[day_index]
            if contrib["count"] > 0:
                x = grid_start_x + (week * (cell_size + cell_gap))
                y = grid_start_y + (day * (cell_size + cell_gap))
                contrib_positions.append({
                    "x": x + cell_size/2,
                    "y": y + cell_size/2,
                    "week": week,
                    "day": day,
                    "count": contrib["count"],
                    "color": get_color_for_count(contrib["count"])
                })
            
            day_index += 1
        
        if day_index >= len(recent_contributions):
            break
    
    total_contributions = len(contrib_positions)
    
    # Calculate animation timings
    cycle_duration = max(total_contributions * 0.15, 8)  # Total cycle time
    spaceship_duration = cycle_duration
    
    # Start SVG
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <!-- Gradients -->
        <linearGradient id="spaceshipGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#7c3aed;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#a855f7;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#c084fc;stop-opacity:1" />
        </linearGradient>
        
        <radialGradient id="engineGlow">
            <stop offset="0%" style="stop-color:#fbbf24;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#f97316;stop-opacity:0.8" />
            <stop offset="100%" style="stop-color:#ef4444;stop-opacity:0" />
        </radialGradient>
        
        <radialGradient id="laserGlow">
            <stop offset="0%" style="stop-color:{LASER_GLOW};stop-opacity:1" />
            <stop offset="100%" style="stop-color:{LASER_COLOR};stop-opacity:0.3" />
        </radialGradient>
        
        <!-- Filters -->
        <filter id="glow">
            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    </defs>
    
    <style>
        /* Spaceship oscillating movement (right to left, left to right) */
        @keyframes spaceship-move {{
            0% {{ transform: translateX(0px); }}
            50% {{ transform: translateX({width - 150}px); }}
            100% {{ transform: translateX(0px); }}
        }}
        
        /* Engine flame animation */
        @keyframes flame-flicker {{
            0%, 100% {{ opacity: 0.7; transform: scaleX(1) scaleY(1); }}
            25% {{ opacity: 1; transform: scaleX(1.4) scaleY(0.9); }}
            50% {{ opacity: 0.8; transform: scaleX(1.1) scaleY(1.1); }}
            75% {{ opacity: 0.9; transform: scaleX(1.3) scaleY(0.95); }}
        }}
        
        /* Stars twinkling */
        @keyframes star-twinkle {{
            0%, 100% {{ opacity: 0.2; }}
            50% {{ opacity: 1; }}
        }}
        
        /* Laser shot animation - travels to target then stays */
        @keyframes laser-shoot {{
            0% {{ 
                opacity: 0;
                transform: translate(0, 0) scale(0);
            }}
            5% {{ 
                opacity: 1;
                transform: translate(0, 0) scale(1);
            }}
            100% {{ 
                opacity: 1;
                transform: translate(var(--target-x), var(--target-y)) scale(1);
            }}
        }}
        
        /* Contribution cell reveal animation */
        @keyframes cell-reveal {{
            0% {{ 
                opacity: 0;
                transform: scale(0);
            }}
            100% {{ 
                opacity: 1;
                transform: scale(1);
            }}
        }}
        
        /* Glow pulse for hit cells */
        @keyframes glow-pulse {{
            0%, 100% {{ filter: brightness(1); }}
            50% {{ filter: brightness(1.4); }}
        }}
        
        .spaceship-group {{
            animation: spaceship-move {spaceship_duration}s linear infinite;
        }}
        
        .flame {{
            animation: flame-flicker 0.15s ease-in-out infinite;
        }}
        
        .star {{
            animation: star-twinkle 3s ease-in-out infinite;
        }}
        
        .laser {{
            animation: laser-shoot 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
            filter: url(#glow);
        }}
        
        .contrib-cell {{
            animation: cell-reveal 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) forwards,
                       glow-pulse 1s ease-in-out 2;
        }}
    </style>
    
    <!-- Space Background -->
    <rect width="{width}" height="{height}" fill="{SPACE_BG}"/>
    
    <!-- Background Stars -->
'''
    
    # Generate random stars
    random.seed(42)
    for _ in range(100):
        x = random.randint(0, width)
        y = random.randint(0, height - 70)
        size = random.uniform(0.5, 2.5)
        delay = random.uniform(0, 3)
        svg += f'    <circle cx="{x}" cy="{y}" r="{size}" fill="{STAR_COLOR}" class="star" style="animation-delay: {delay}s;"/>\n'
    
    # Contribution Grid Background (empty cells)
    svg += '\n    <!-- Contribution Grid Background -->\n    <g id="grid-background">\n'
    
    day_index = 0
    for week in range(53):
        for day in range(7):
            if day_index >= len(recent_contributions):
                break
            
            x = grid_start_x + (week * (cell_size + cell_gap))
            y = grid_start_y + (day * (cell_size + cell_gap))
            
            # Always show empty cell background
            svg += f'        <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="#161b22" rx="2"/>\n'
            
            day_index += 1
        
        if day_index >= len(recent_contributions):
            break
    
    svg += '    </g>\n\n'
    
    # Contribution cells that will be revealed
    svg += '    <!-- Contribution Cells (Revealed by Lasers) -->\n    <g id="contribution-cells">\n'
    
    for idx, pos in enumerate(contrib_positions):
        x = pos["x"] - cell_size/2
        y = pos["y"] - cell_size/2
        delay = idx * 0.15  # Stagger the reveals
        
        svg += f'        <rect class="contrib-cell" x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{pos["color"]}" rx="2" style="animation-delay: {delay + 0.4}s;"/>\n'
    
    svg += '    </g>\n\n'
    
    # Laser shots
    svg += '    <!-- Laser Shots -->\n    <g id="lasers">\n'
    
    for idx, pos in enumerate(contrib_positions):
        delay = idx * 0.15
        target_x = pos["x"] - 40  # Offset from spaceship gun position
        target_y = pos["y"] - spaceship_y
        
        # Laser beam
        svg += f'''        <g class="laser" style="animation-delay: {delay}s; --target-x: {target_x}px; --target-y: {target_y}px;">
            <circle cx="40" cy="{spaceship_y}" r="3" fill="{LASER_COLOR}"/>
            <circle cx="40" cy="{spaceship_y}" r="6" fill="url(#laserGlow)" opacity="0.6"/>
        </g>\n'''
    
    svg += '    </g>\n\n'
    
    # Spaceship
    svg += f'''    <!-- Spaceship -->
    <g class="spaceship-group">
        <!-- Main Body -->
        <ellipse cx="45" cy="{spaceship_y}" rx="25" ry="15" fill="url(#spaceshipGradient)" stroke="#a855f7" stroke-width="1.5"/>
        
        <!-- Cockpit -->
        <ellipse cx="55" cy="{spaceship_y}" rx="12" ry="8" fill="#1e293b" opacity="0.8"/>
        <ellipse cx="55" cy="{spaceship_y}" rx="8" ry="5" fill="#60a5fa" opacity="0.5"/>
        <circle cx="58" cy="{spaceship_y - 2}" r="2" fill="#93c5fd" opacity="0.7"/>
        
        <!-- Wings -->
        <path d="M 30 {spaceship_y - 8} L 20 {spaceship_y - 18} L 35 {spaceship_y - 10} Z" fill="#6366f1" opacity="0.9"/>
        <path d="M 30 {spaceship_y + 8} L 20 {spaceship_y + 18} L 35 {spaceship_y + 10} Z" fill="#6366f1" opacity="0.9"/>
        
        <!-- Engine Exhausts -->
        <g class="flame">
            <ellipse cx="15" cy="{spaceship_y - 5}" rx="12" ry="4" fill="url(#engineGlow)" opacity="0.9"/>
            <ellipse cx="12" cy="{spaceship_y - 5}" rx="8" ry="3" fill="#fbbf24" opacity="0.8"/>
        </g>
        <g class="flame" style="animation-delay: 0.05s;">
            <ellipse cx="15" cy="{spaceship_y + 5}" rx="12" ry="4" fill="url(#engineGlow)" opacity="0.9"/>
            <ellipse cx="12" cy="{spaceship_y + 5}" rx="8" ry="3" fill="#fbbf24" opacity="0.8"/>
        </g>
        
        <!-- Engine Cores -->
        <circle cx="23" cy="{spaceship_y - 5}" r="3" fill="#7c3aed" stroke="#a855f7" stroke-width="1"/>
        <circle cx="23" cy="{spaceship_y + 5}" r="3" fill="#7c3aed" stroke="#a855f7" stroke-width="1"/>
        
        <!-- Weapon/Gun (where lasers come from) -->
        <rect x="68" y="{spaceship_y - 2}" width="8" height="4" fill="#8b5cf6" rx="1"/>
        <circle cx="76" cy="{spaceship_y}" r="2" fill="{LASER_COLOR}" opacity="0.8"/>
        
        <!-- Detail Lines -->
        <line x1="35" y1="{spaceship_y}" x2="60" y2="{spaceship_y}" stroke="#a855f7" stroke-width="1" opacity="0.5"/>
    </g>
    
    <!-- Stats Text -->
    <text x="{width/2}" y="{height - 10}" text-anchor="middle" fill="#8b949e" font-family="'Segoe UI', Arial, sans-serif" font-size="11" font-weight="500">
        🚀 {total_contributions} targets locked • Cycle: {cycle_duration:.1f}s • Status: FIRING
    </text>
    
</svg>'''
    
    return svg

def main():
    print("🚀 Starting enhanced space contribution graph generator...")
    print(f"👤 Username: {USERNAME}")
    
    # Fetch contributions
    print("📊 Fetching contribution data from GitHub...")
    contributions = fetch_contributions()
    
    if not contributions:
        print("❌ No contributions found or error occurred")
        return
    
    total_contributions = sum(c['count'] for c in contributions)
    active_days = len([c for c in contributions if c['count'] > 0])
    print(f"✅ Found {len(contributions)} days with {total_contributions} total contributions")
    print(f"🎯 {active_days} active contribution days to target")
    
    # Generate SVG
    print("🎨 Generating SVG with spaceship animation...")
    svg_content = generate_svg(contributions)
    
    # Create output directory
    os.makedirs("dist", exist_ok=True)
    
    # Write SVG file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print(f"✅ Space contribution graph generated successfully!")
    print(f"📁 Output: {OUTPUT_FILE}")
    print(f"💡 The spaceship will fire {active_days} laser shots in sequence")

if __name__ == "__main__":
    main()
