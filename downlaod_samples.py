"""
Download sample pitch decks from public sources.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Public Pitch Deck Sources
# -------------------------------------------------------------------

PITCH_DECKS = {
    "airbnb": {
        "name": "Airbnb_Pitch_Deck.pdf",
        "url": "https://www.slideshare.net/slideshow/embed_code/key/rtND9E3BgrzYyS",
        "description": "Airbnb's original Series A pitch deck (2009)",
    },
    "uber": {
        "name": "Uber_Pitch_Deck.pdf",
        "url": "https://www.slideshare.net/slideshow/embed_code/key/6sLSPOYVWnhALG",
        "description": "Uber's original pitch deck (2008)",
    },
    "buffer": {
        "name": "Buffer_Pitch_Deck.pdf",
        "url": "https://www.slideshare.net/slideshow/embed_code/key/qRaYQPp6iV9Piz",
        "description": "Buffer's seed round pitch deck",
    },
}


DIRECT_LINKS = [
    {
        "name": "Airbnb_Pitch_Deck_2009.pdf",
        "url": "https://www.circleup.com/wp-content/uploads/2015/07/Airbnb-Pitch-Deck-2009.pdf",
        "description": "Airbnb original pitch deck",
    },
    {
        "name": "LinkedIn_Pitch_Deck.pdf",
        "url": "https://www.cirrusinsight.com/wp-content/uploads/2020/03/LinkedIn-Pitch-Deck.pdf",
        "description": "LinkedIn Series B pitch deck",
    },
    {
        "name": "Facebook_Pitch_Deck.pdf",
        "url": "https://www.slidesharecdn.com/ss_thumbnails/facebookpitchdeck-120302143413-phpapp01-thumbnail-4.jpg",
        "description": "Facebook early pitch deck (reference)",
    },
    {
        "name": "Foursquare_Pitch_Deck.pdf",
        "url": "https://www.slidesharecdn.com/ss_thumbnails/foursquarepitchdeck-120302143415-phpapp01-thumbnail-4.jpg",
        "description": "Foursquare pitch deck",
    },
    {
        "name": "Mint_Pitch_Deck.pdf",
        "url": "https://www.slidesharecdn.com/ss_thumbnails/mintpitchdeck-120302143417-phpapp02-thumbnail-4.jpg",
        "description": "Mint.com pitch deck",
    },
    {
        "name": "BuzzFeed_Pitch_Deck.pdf",
        "url": "https://www.slidesharecdn.com/ss_thumbnails/buzzfeedpitchdeck-120302143419-phpapp01-thumbnail-4.jpg",
        "description": "BuzzFeed pitch deck",
    },
    {
        "name": "YouTube_Pitch_Deck.pdf",
        "url": "https://www.slidesharecdn.com/ss_thumbnails/youtubepitchdeck-120302143421-phpapp01-thumbnail-4.jpg",
        "description": "YouTube early pitch deck",
    },
    {
        "name": "WeWork_Pitch_Deck.pdf",
        "url": "https://www.slidesharecdn.com/ss_thumbnails/weworkpitchdeck-120302143423-phpapp02-thumbnail-4.jpg",
        "description": "WeWork pitch deck",
    },
    {
        "name": "Peloton_Pitch_Deck.pdf",
        "url": "https://www.slidesharecdn.com/ss_thumbnails/pelotonpitchdeck-120302143425-phpapp02-thumbnail-4.jpg",
        "description": "Peloton pitch deck",
    },
    {
        "name": "Square_Pitch_Deck.pdf",
        "url": "https://www.slidesharecdn.com/ss_thumbnails/squarepitchdeck-120302143427-phpapp01-thumbnail-4.jpg",
        "description": "Square pitch deck",
    },
]



# -------------------------------------------------------------------
# Download Function
# -------------------------------------------------------------------

def download_pitch_deck(
    url: str,
    filename: str,
    output_dir: str = "data/sample_pitchdecks",
) -> Optional[str]:
    """
    Download a pitch deck from a URL.

    Returns:
        Path to downloaded file or None if failed.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filepath = output_path / filename

    try:
        logger.info(f"Downloading {filename}...")

        response = requests.get(
            url,
            timeout=30,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                )
            },
        )
        response.raise_for_status()

        with open(filepath, "wb") as f:
            f.write(response.content)

        size_kb = len(response.content) / 1024
        logger.info(f"✅ Downloaded: {filepath} ({size_kb:.1f} KB)")

        return str(filepath)

    except Exception as e:
        logger.error(f"❌ Failed to download {filename}: {e}")
        return None


# -------------------------------------------------------------------
# Sample Deck Generator (Fallback)
# -------------------------------------------------------------------

def create_sample_pitch_deck() -> str:
    """Create a simple synthetic pitch deck for testing."""

    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch

    output_path = Path("data/sample_pitchdecks")
    output_path.mkdir(parents=True, exist_ok=True)

    filepath = output_path / "Sample_Startup_Deck.pdf"

    c = canvas.Canvas(str(filepath), pagesize=letter)
    width, height = letter

    def title_page(title: str, subtitle: str):
        c.setFont("Helvetica-Bold", 36)
        c.drawCentredString(width / 2, height - 2 * inch, title)
        c.setFont("Helvetica", 18)
        c.drawCentredString(width / 2, height - 2.5 * inch, subtitle)
        c.showPage()

    def section(title: str, bullets: List[str]):
        c.setFont("Helvetica-Bold", 24)
        c.drawString(inch, height - inch, title)

        c.setFont("Helvetica", 14)
        y = height - 1.5 * inch
        for bullet in bullets:
            c.drawString(inch, y, f"• {bullet}")
            y -= 0.5 * inch

        c.showPage()

    # Pages
    title_page(
        "TechStartup AI",
        "Revolutionizing Healthcare with AI"
    )

    section("Problem", [
        "Healthcare providers spend 50% of time on paperwork",
        "Medical errors cost $20B annually",
        "Doctors face burnout from administrative burden",
    ])

    section("Solution", [
        "AI-powered clinical documentation assistant",
        "Automatic note generation from voice",
        "HIPAA-compliant AI understanding medical context",
        "Integration with major EHR systems",
    ])

    section("Market Opportunity", [
        "TAM: $50B Healthcare AI market",
        "SAM: $5B clinical documentation",
        "SOM: $500M US hospitals",
        "Market growing at 35% CAGR",
    ])

    section("Business Model", [
        "SaaS subscription: $500/doctor/month",
        "Enterprise contracts: $50K–500K annually",
        "Average LTV: $120K",
        "CAC: $15K, LTV/CAC ratio: 8x",
    ])

    section("Traction", [
        "$2.5M ARR",
        "150+ doctors across 12 hospitals",
        "200% YoY revenue growth",
        "95% retention rate",
    ])

    section("Team", [
        "Jane Doe - CEO (Ex-Google, Stanford PhD AI)",
        "John Smith - CTO (Ex-Amazon ML systems)",
        "Dr. Sarah Johnson - CMO (15 years ER physician)",
    ])

    section("Competition", [
        "Competitors: Nuance Dragon, Suki, Abridge",
        "95% accuracy vs 80% industry average",
        "Native EHR integration",
        "Real-time processing",
    ])

    section("The Ask", [
        "Raising $5M Series A",
        "50% Engineering",
        "30% Sales & Marketing",
        "20% Operations & Compliance",
        "18-month runway to $10M ARR",
    ])

    c.save()

    logger.info(f"✅ Created sample pitch deck: {filepath}")
    return str(filepath)


# -------------------------------------------------------------------
# Script Entry
# -------------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("Downloading Sample Pitch Decks")
    print("=" * 60)

    downloaded: List[Dict[str, str]] = []

    # Download real decks
    for deck in DIRECT_LINKS:
        filepath = download_pitch_deck(deck["url"], deck["name"])
        if filepath:
            downloaded.append({
                "path": filepath,
                "description": deck["description"],
            })

    # Always create fallback sample
    sample_path = create_sample_pitch_deck()
    downloaded.append({
        "path": sample_path,
        "description": "Sample healthcare AI startup deck",
    })

    print("\n" + "=" * 60)
    print(f"✅ Ready to test! {len(downloaded)} pitch decks available:")
    print("=" * 60)

    for i, deck in enumerate(downloaded, 1):
        print(f"\n{i}. {Path(deck['path']).name}")
        print(f"   {deck['description']}")
        print(f"   Path: {deck['path']}")

    print("\n" + "=" * 60)
    print("Next: Run test_venturescope.py to analyze these decks!")
    print("=" * 60)
