from core.pitch_deck_registry import PitchDeckRegistry
from core.orchestrator import VentureScopeOrchestrator

registry = PitchDeckRegistry()
orchestrator = VentureScopeOrchestrator()

for deck in registry.get_unanalyzed():

    path = f"data/pitch_decks/{deck['file']}"

    print(f"Analyzing {deck['company']}...")

    result = orchestrator.analyze_pitch_deck(path)

    registry.mark_analyzed(deck["id"])

print("✅ Batch analysis complete.")
