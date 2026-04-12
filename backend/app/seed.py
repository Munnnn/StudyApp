"""
Seed a demo Step 1 deck (~20 cards across cardio / renal / micro).
Run once after migrations:
    python -m app.seed
"""
import asyncio
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AsyncSessionLocal, engine, Base
from app.models.deck import Deck, SourceType
from app.models.card import Card
from app.models.schedule_state import ScheduleState
from app.models.user import User

DEMO_DEVICE_ID = "seed-demo-device-0000"

CARDS = [
    # ─── Cardio ─────────────────────────────────────────────────────────────
    ("What ECG finding is classic for hyperkalemia?", "Peaked T-waves (earliest), then PR prolongation, wide QRS, sine wave, VF", "cardio", "ECG", 2),
    ("What is the mechanism of cardiac action of adenosine?", "Activates A1 receptors → increased K+ conductance → hyperpolarization → AV node slowing", "cardio", "antiarrhythmics", 3),
    ("What causes pulsus paradoxus?", "Cardiac tamponade (exaggerated inspiratory drop in systolic BP >10 mmHg)", "cardio", "tamponade", 2),
    ("Which valve lesion causes a midsystolic click followed by a murmur?", "Mitral valve prolapse", "cardio", "valvular", 2),
    ("What is the most common cause of aortic stenosis in adults >60?", "Calcific (senile) degeneration", "cardio", "valvular", 2),
    ("What drug class is first-line for HFrEF to reduce mortality?", "ACE inhibitors (or ARBs) + beta-blockers + aldosterone antagonists", "cardio", "heart failure", 2),
    ("Mechanism of nitrate tolerance?", "Depletion of sulfhydryl groups needed to convert nitrates to NO", "cardio", "nitrates", 3),
    # ─── Renal ──────────────────────────────────────────────────────────────
    ("What causes hypercalcemia with low PTH?", "Malignancy (PTHrP secretion)", "renal", "calcium", 2),
    ("Muddy brown granular casts indicate?", "Acute tubular necrosis (ATN)", "renal", "casts", 2),
    ("What is the equation for GFR using creatinine clearance?", "GFR = (UCr × Uvolume) / PCr (simplified Cockcroft-Gault)", "renal", "GFR", 3),
    ("Mechanism of loop diuretics?", "Block Na-K-2Cl cotransporter in thick ascending limb of Henle", "renal", "diuretics", 2),
    ("Which diuretic is used for nephrogenic DI?", "Thiazide diuretics (paradoxical concentration by reducing GFR)", "renal", "DI", 3),
    ("RBC casts in urine indicate?", "Glomerulonephritis (nephritic pattern)", "renal", "casts", 2),
    # ─── Micro ──────────────────────────────────────────────────────────────
    ("What toxin causes watery diarrhea by activating adenylate cyclase?", "Cholera toxin (V. cholerae) — ADP-ribosylates Gs → constitutive cAMP elevation", "micro", "GI pathogens", 2),
    ("Which bug causes 'rice-water' stools?", "Vibrio cholerae", "micro", "GI pathogens", 1),
    ("Mechanism of diphtheria toxin?", "ADP-ribosylation of EF-2 → inhibits protein synthesis → pseudomembrane + myocarditis", "micro", "toxins", 3),
    ("What does C. difficile toxin B do?", "Glucosylates Rho GTPases → actin cytoskeleton disruption → colonic mucosal damage", "micro", "C diff", 3),
    ("Which organism causes 'rose spot' rash?", "Salmonella typhi (typhoid fever)", "micro", "enteric fever", 2),
    ("Macrophage that cannot kill an intracellular organism — what is the defect?", "Impaired IFN-γ signaling (e.g. IL-12 or IL-12R deficiency) — required to activate microbicidal machinery", "micro", "immunology", 4),
    ("What is the CAMP test used for?", "Identify Group B Strep (S. agalactiae) — enhances β-hemolysin of S. aureus", "micro", "strep", 3),
]


async def seed():
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select

        # Get or create demo user
        r = await db.execute(select(User).where(User.device_id == DEMO_DEVICE_ID))
        user = r.scalar_one_or_none()
        if not user:
            user = User(device_id=DEMO_DEVICE_ID, display_name="Demo Student")
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print(f"Created demo user {user.id}")

        # Check if deck already exists
        r2 = await db.execute(select(Deck).where(Deck.owner_id == user.id))
        existing = r2.scalars().first()
        if existing:
            print("Demo deck already exists — skipping seed.")
            return

        deck = Deck(
            owner_id=user.id,
            title="Step 1 Demo Deck",
            description="20 high-yield cards across Cardio, Renal, and Micro",
            source_type=SourceType.manual,
        )
        db.add(deck)
        await db.commit()
        await db.refresh(deck)
        print(f"Created deck: {deck.id}")

        now = datetime.now(timezone.utc)
        for front, back, system, topic, diff in CARDS:
            card = Card(
                deck_id=deck.id,
                front=front,
                back=back,
                system_tag=system,
                topic_tag=topic,
                difficulty=diff,
            )
            db.add(card)
            await db.flush()

            ss = ScheduleState(
                user_id=user.id,
                card_id=card.id,
                next_due_at=now,
                interval_min=10,
            )
            db.add(ss)

        await db.commit()
        print(f"Seeded {len(CARDS)} cards.")
        print(f"\nDemo device ID for testing: {DEMO_DEVICE_ID}")
        print("Use this as X-Device-Id header in API calls.")


if __name__ == "__main__":
    asyncio.run(seed())
