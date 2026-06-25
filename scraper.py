import feedparser

def get_live_updates():
    # Using an open, community-driven gaming feed node that doesn't block automation
    feed_url = "https://reddit.com/r/GTA6/.rss"
    
    # Add a custom User-Agent so the website knows we are a safe browser utility
    custom_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ViceMatrixBot/1.0"
    
    try:
        feed = feedparser.parse(feed_url, agent=custom_agent)
        
        if not feed.entries:
            raise Exception("Feed returned empty data.")
            
        updates = []
        for entry in feed.entries[:3]:
            # Clean up the titles slightly for your sleek display box
            title = entry.title
            if len(title) > 65:
                title = title[:62] + "..."
                
            updates.append({
                "title": title,
                "link": entry.link
            })
        return updates
    except Exception as e:
        # Secure fallback data if the external networks are down
        return [
            {"title": "ALERT: Pre-Orders Launch Matrix Engaged Live", "link": "#"},
            {"title": "EXPLOIT: Tracking Inactive Database Sequences...", "link": "#"},
            {"title": "SYSTEM: Vercel Instant Node Online", "link": "#"}
        ]

if __name__ == "__main__":
    print("Testing Automation Engine (v2)...")
    live_data = get_live_updates()
    for item in live_data:
        print(f"- {item['title']}")
