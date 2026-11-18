import json
from pathlib import Path
from typing import Any

PROTECT_MOVES = {
    "protect",
    "detect",
    "spikyshield",
    "banefulbunker",
    "kingsshield",
    "obstruct",
    "silktrap",
    "burningbulwark",
    "endure",
    "wideguard",
    "quickguard",
}

RECHARGE_MOVES = {
    "hyperbeam",
    "gigaimpact",
    "frenzyplant",
    "blastburn",
    "hydrocannon",
    "rockwrecker",
    "roaroftime",
    "meteorassault",
    "eternabeam",
}

SYSTEM_PROMPT = (
    "You are an expert Pokemon VGC battle strategist. "
    "Analyze the given state of the battle to output optimal target orders. "
    "Note: If an opponent used a protection move last turn, a consecutive protect has a high chance to fail; "
    "if an opponent used a recharge move last turn, they must recharge and cannot act this turn."
)


# ===== NAME NORMALIZATION =====
# Maps Showdown display names to canonical Showdown-id style (lowercase, no spaces/hyphens/apostrophes)
SPECIES_NORMALIZE_MAP = {
    # Mega forms
    "charizard-mega-y": "charizardmegay",
    "charizardmegay": "charizardmegay",
    "garchomp-mega-z": "garchompmegaz",
    "garchompmegaz": "garchompmegaz",
    "raichu-mega-y": "raichumegay",
    "raichumegay": "raichumegay",
    "raichu-mega-x": "raichumegax",
    "raichumegax": "raichumegax",
    "golisopod-mega": "golisopodmega",
    "golisopodmega": "golisopodmega",
    "floette-eternal": "floetteeternal",
    "floetteeternal": "floetteeternal",
    "staraptor-mega": "staraptormega",
    "staraptormega": "staraptormega",
    "tyranitar-mega": "tyranitarmega",
    "tyranitarmega": "tyranitarmega",
    "delphox-mega": "delphoxmega",
    "delphoxmega": "delphoxmega",
    "salamence-mega": "salamencemega",
    "salamencemega": "salamencemega",
    "metagross-mega": "metagrossmega",
    "metagrossmega": "metagrossmega",
    "froslass-mega": "froslassmega",
    "froslassmega": "froslassmega",
    "blastoise-mega": "blastoisemega",
    "blastoisemega": "blastoisemega",
    "gengar-mega": "gengarmega",
    "gengarmega": "gengarmega",
    "aerodactyl-mega": "aerodactylmega",
    "aerodactylmega": "aerodactylmega",
    "gardevoir-mega": "gardevoirmega",
    "gardevoirmega": "gardevoirmega",
    "blaziken-mega": "blazikenmega",
    "blazikenmega": "blazikenmega",
    "dragonite-mega": "dragonitemega",
    "dragonitemega": "dragonitemega",
    # Regional forms
    "arcanine-hisui": "arcaninehisui",
    "arcaninehisui": "arcaninehisui",
    "basculegion-f": "basculegionf",
    "basculegionf": "basculegionf",
    "indeedee-f": "indeedeef",
    "indeedeef": "indeedeef",
}

MOVE_NORMALIZE_MAP = {
    # Two-word moves -> canonical
    "fake out": "fakeout",
    "fakeout": "fakeout",
    "sucker punch": "suckerpunch",
    "suckerpunch": "suckerpunch",
    "close combat": "closecombat",
    "closecombat": "closecombat",
    "wood hammer": "woodhammer",
    "woodhammer": "woodhammer",
    "electro shot": "electroshot",
    "electroshot": "electroshot",
    "parting shot": "partingshot",
    "partingshot": "partingshot",
    "flare blitz": "flareblitz",
    "flareblitz": "flareblitz",
    "wave crash": "wavecrash",
    "wavecrash": "wavecrash",
    "iron head": "ironhead",
    "ironhead": "ironhead",
    "draco meteor": "dracometeor",
    "dracometeor": "dracometeor",
    "shadow ball": "shadowball",
    "shadowball": "shadowball",
    "dire claw": "direclaw",
    "direclaw": "direclaw",
    "leech life": "leechlife",
    "leechlife": "leechlife",
    "hyper voice": "hypervoice",
    "hypervoice": "hypervoice",
    "kowtow cleave": "kowtowcleave",
    "kowtowcleave": "kowtowcleave",
    "rock slide": "rockslide",
    "rockslide": "rockslide",
    "high horsepower": "highhorsepower",
    "highhorsepower": "highhorsepower",
    "make it rain": "makeitrain",
    "makeitrain": "makeitrain",
    "grassy glide": "grassyglide",
    "grassyglide": "grassyglide",
    "helping hand": "helpinghand",
    "helpinghand": "helpinghand",
    "muddy water": "muddywater",
    "muddywater": "muddywater",
    "leaf storm": "leafstorm",
    "leafstorm": "leafstorm",
    "follow me": "followme",
    "followme": "followme",
    "psychic fangs": "psychicfangs",
    "psychicfangs": "psychicfangs",
    "volt switch": "voltswitch",
    "voltswitch": "voltswitch",
    "expanding force": "expandingforce",
    "expandingforce": "expandingforce",
    "calm mind": "calmmind",
    "calmmind": "calmmind",
    "rain dance": "raindance",
    "raindance": "raindance",
    "dragon claw": "dragonclaw",
    "dragonclaw": "dragonclaw",
    "solar beam": "solarbeam",
    "solarbeam": "solarbeam",
    "stomping tantrum": "stompingtantrum",
    "stompingtantrum": "stompingtantrum",
    "trick room": "trickroom",
    "trickroom": "trickroom",
    "aqua jet": "aquajet",
    "aquajet": "aquajet",
    "knock off": "knockoff",
    "knockoff": "knockoff",
    "throat chop": "throatchop",
    "throatchop": "throatchop",
    "dazzling gleam": "dazzlinggleam",
    "dazzlinggleam": "dazzlinggleam",
    "body press": "bodypress",
    "bodypress": "bodypress",
    "u-turn": "uturn",
    "uturn": "uturn",
    "low kick": "lowkick",
    "lowkick": "lowkick",
    "shell smash": "shellsmash",
    "shellsmash": "shellsmash",
    "dragon dance": "dragondance",
    "dragondance": "dragondance",
    "bulk up": "bulkup",
    "bulkup": "bulkup",
    "ice beam": "icebeam",
    "icebeam": "icebeam",
    "dragon pulse": "dragonpulse",
    "dragonpulse": "dragonpulse",
    "focus blast": "focusblast",
    "focusblast": "focusblast",
    "power gem": "powergem",
    "powergem": "powergem",
    "heat wave": "heatwave",
    "heatwave": "heatwave",
    "earth power": "earthpower",
    "earthpower": "earthpower",
    "sludge bomb": "sludgebomb",
    "sludgebomb": "sludgebomb",
    "strength sap": "strengthsap",
    "strengthsap": "strengthsap",
    "head smash": "headsmash",
    "headsmash": "headsmash",
    "shadow claw": "shadowclaw",
    "shadowclaw": "shadowclaw",
    "dark pulse": "darkpulse",
    "darkpulse": "darkpulse",
    "air slash": "airslash",
    "airslash": "airslash",
    "flash cannon": "flashcannon",
    "flashcannon": "flashcannon",
    "moonblast": "moonblast",
    "earthquake": "earthquake",
    "protect": "protect",
    "detect": "detect",
    "wide guard": "wideguard",
    "wideguard": "wideguard",
    "quick guard": "quickguard",
    "quickguard": "quickguard",
    "spiky shield": "spikyshield",
    "spikyshield": "spikyshield",
    "baneful bunker": "banefulbunker",
    "banefulbunker": "banefulbunker",
    "king's shield": "kingsshield",
    "kingsshield": "kingsshield",
    "obstruct": "obstruct",
    "silk trap": "silktrap",
    "silktrap": "silktrap",
    "burning bulwark": "burningbulwark",
    "burningbulwark": "burningbulwark",
    "endure": "endure",
    "hyper beam": "hyperbeam",
    "hyperbeam": "hyperbeam",
    "giga impact": "gigaimpact",
    "gigaimpact": "gigaimpact",
    "frenzy plant": "frenzyplant",
    "frenzyplant": "frenzyplant",
    "blast burn": "blastburn",
    "blastburn": "blastburn",
    "hydro cannon": "hydrocannon",
    "hydrocannon": "hydrocannon",
    "rock wrecker": "rockwrecker",
    "rockwrecker": "rockwrecker",
    "roar of time": "roaroftime",
    "roaroftime": "roaroftime",
    "meteor assault": "meteorassault",
    "meteorassault": "meteorassault",
    "eternabeam": "eternabeam",
}

def normalize_species(name: str) -> str:
    """Normalize species name to Showdown-id style."""
    key = name.lower().strip()
    return SPECIES_NORMALIZE_MAP.get(key, key.replace("-", "").replace(" ", "").replace("'", ""))

def normalize_move(name: str) -> str:
    """Normalize move name to Showdown-id style."""
    key = name.lower().strip()
    return MOVE_NORMALIZE_MAP.get(key, key.replace(" ", "").replace("-", "").replace("'", ""))

def normalize_order_text(text: str) -> str:
    """Normalize species and move names in an order string."""
    import re

    # Split by ", " to handle each order separately
    orders = text.split(", ")
    normalized_orders = []

    for order in orders:
        order = order.strip()
        if not order:
            continue

        # Handle "switches to" orders: "<species> switches to <target>"
        switch_match = re.match(r'^(.+?)\s+switches to\s+(.+)$', order)
        if switch_match:
            species = switch_match.group(1).strip()
            target = switch_match.group(2).strip()
            normalized = f"{normalize_species(species)} switches to {normalize_species(target)}"
            normalized_orders.append(normalized)
            continue

        # Handle "uses" orders with targeting: "<species> uses <move> targeting <target>"
        use_target_match = re.match(r'^(.+?)\s+uses\s+(.+?)\s+targeting\s+(.+)$', order)
        if use_target_match:
            species = use_target_match.group(1).strip()
            move = use_target_match.group(2).strip()
            target = use_target_match.group(3).strip()
            normalized = f"{normalize_species(species)} uses {normalize_move(move)} targeting {target}"
            normalized_orders.append(normalized)
            continue

        # Handle "uses" orders without targeting: "<species> uses <move>"
        use_match = re.match(r'^(.+?)\s+uses\s+(.+)$', order)
        if use_match:
            species = use_match.group(1).strip()
            move = use_match.group(2).strip()
            normalized = f"{normalize_species(species)} uses {normalize_move(move)}"
            normalized_orders.append(normalized)
            continue

        # Fallback: return as-is if no pattern matches
        normalized_orders.append(order)

    return ", ".join(normalized_orders)

def normalize_user_prompt(text: str) -> str:
    """Normalize species names in user prompt (species appear in active/bench sections)."""
    for display, canonical in SPECIES_NORMALIZE_MAP.items():
        # Replace in context like "Slot 1: charizard-mega-y (100% HP..."
        import re
        text = re.sub(rf'\b{re.escape(display)}\b', canonical, text, flags=re.IGNORECASE)
    return text


def format_side_conditions(sc: dict[str, int]) -> str:
    """Formats active side conditions (Tailwind, screens, hazards) concisely."""
    active_sc = [f"{k}: {v}" for k, v in sc.items() if v > 0]
    return ", ".join(active_sc) if active_sc else "None"


def format_field(field: dict[str, Any]) -> str:
    """Formats field conditions, appending a duration of 4 turns if weather or terrain is active."""
    weather = field.get("weather", "None")
    terrain = field.get("terrain", "None")
    trick_room = field.get("trick_room", 0)

    weather_str = f"{{{weather}: 4}}" if weather and weather.lower() != "none" else "None"
    terrain_str = f"{{{terrain}: 4}}" if terrain and terrain.lower() != "none" else "None"

    return f"Weather: {weather_str}, Terrain: {terrain_str}, Trick Room: {trick_room}"


def is_double_switch(target_orders: list[str]) -> bool:
    """Returns True if target_orders is ordering two switches on the same turn."""
    switch_count = sum(1 for order in target_orders if "switches to" in order.lower())
    return switch_count >= 2


def extract_opp_last_turn_flags(turn: dict[str, Any]) -> str:
    """Extracts only Protect-type and Recharge moves used by active opponents on the previous turn."""
    history = turn.get("battle_history", [])
    if not history:
        return "None"

    last_opp_actions = history[-1].get("opponent_action", [])
    active_opp_species = {p["species"].lower() for p in turn["opponent_side"].get("active", [])}

    flags: list[str] = []
    for action in last_opp_actions:
        act_lower = action.lower()
        if " uses " not in act_lower:
            continue

        species, move_part = act_lower.split(" uses ", 1)
        species = species.strip()
        move = move_part.split()[0].strip()

        if species not in active_opp_species:
            continue

        if move in PROTECT_MOVES:
            flags.append(f"{species} used {move} last turn (consecutive protect likely fails)")
        elif move in RECHARGE_MOVES:
            flags.append(f"{species} used {move} last turn (must recharge this turn)")

    return "; ".join(flags) if flags else "None"


def get_interaction_signature(turn: dict[str, Any]) -> tuple[str, ...]:
    """Extracts a semantic signature of the turn's matchups: [Attacker]:[Move]->[Defender]."""
    opp_slots = {p["slot"]: p["species"].lower() for p in turn["opponent_side"].get("active", [])}
    my_species_list = [p["species"].lower() for p in turn["my_side"].get("active", [])]

    interactions: list[str] = []
    for order in turn.get("target_orders", []):
        order_lower = order.lower()

        attacker = "unknown"
        for sp in my_species_list:
            if order_lower.startswith(sp):
                attacker = sp
                break

        action = "other"
        if "uses " in order_lower:
            action = order_lower.split("uses ", 1)[1].split(" targeting")[0].strip()
        elif "switches to" in order_lower:
            action = "switch"

        defender = "none"
        if "targeting opponent slot " in order_lower:
            try:
                slot = int(order_lower.split("targeting opponent slot ")[-1].strip())
                defender = opp_slots.get(slot, "unknown")
            except ValueError:
                pass

        interactions.append(f"{attacker}:{action}->{defender}")

    return tuple(sorted(interactions))


def format_turn_to_chatml(turn: dict[str, Any]) -> dict[str, Any]:
    """Converts a board state into a turn-agnostic ChatML training pair."""
    field_str = format_field(turn["field"])

    # Build user prompt with normalized species names
    my_active = ", ".join(
        f"Slot {p['slot']}: {normalize_species(p['species'])} ({p['hp_pct']}% HP, {p.get('item') or 'no item'}, {p.get('ability')}, status: {p['status']})"
        for p in turn["my_side"].get("active", [])
    )
    my_bench = (
        ", ".join(
            f"{normalize_species(p['species'])} ({p['hp_pct']}% HP, status: {p.get('status', 'None')})"
            for p in turn["my_side"].get("bench", [])
        )
        or "None"
    )

    opp_active = ", ".join(
        f"Slot {p['slot']}: {normalize_species(p['species'])} ({p['hp_pct']}% HP, status: {p['status']})"
        for p in turn["opponent_side"].get("active", [])
    )
    opp_bench = (
        ", ".join(
            f"{normalize_species(p['species'])} ({p['hp_pct']}% HP)"
            for p in turn["opponent_side"].get("bench", [])
        )
        or "None"
    )

    my_sc = format_side_conditions(turn["my_side"].get("side_conditions", {}))
    opp_sc = format_side_conditions(turn["opponent_side"].get("side_conditions", {}))
    opp_flags = extract_opp_last_turn_flags(turn)

    user_prompt = (
        f"{field_str}\n"
        f"Opp Last-Turn Flags: {opp_flags}\n"
        f"My Side Conditions: {my_sc} | My Active: {my_active} | My Bench: {my_bench}\n"
        f"Opp Side Conditions: {opp_sc} | Opp Active: {opp_active} | Opp Bench: {opp_bench}\n"
        f"Provide optimal target orders."
    )

    # FIX: Only take first 2 orders from target_orders (one per active Pokémon)
    # IGNORE following_orders entirely (they are forced switches, not player choices)
    target_orders = turn.get("target_orders", [])
    orders = target_orders[:2]  # At most 2 orders

    # Build assistant completion and normalize names
    assistant_completion = ", ".join(orders)
    assistant_completion = normalize_order_text(assistant_completion)

    # Also normalize user prompt (for consistency, though species already normalized above)
    user_prompt = normalize_user_prompt(user_prompt)

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": assistant_completion},
        ]
    }


def clean_master_dataset(
    input_path: Path, output_path: Path, max_per_interaction: int = 3
) -> None:
    """Filters winning mid-game turns and applies matchup interaction deduplication without a hard cap."""
    processed_examples: list[dict[str, Any]] = []
    interaction_counts: dict[tuple[str, ...], int] = {}
    total_matches = 0
    kept_matches = 0
    dropped_duplicates = 0
    dropped_double_switches = 0
    dropped_unknown = 0
    truncated_orders = 0
    order_counts_before = {}
    order_counts_after = {}

    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            total_matches += 1
            match = json.loads(line)

            if match.get("match_outcome") != "win":
                continue

            total_turns = match.get("total_turns", 0)
            if not (5 <= total_turns <= 15):
                continue

            turns = match.get("turns", [])
            mid_game_turns = turns[2:-2]
            if not mid_game_turns:
                continue

            kept_matches += 1
            for turn in mid_game_turns:
                target_orders = turn.get("target_orders", [])
                if not target_orders:
                    continue

                # Count orders before truncation
                all_orders = list(target_orders)
                following = turn.get("following_orders", [])
                if following:
                    all_orders.extend(following)
                before_count = len(all_orders)
                order_counts_before[before_count] = order_counts_before.get(before_count, 0) + 1

                if is_double_switch(target_orders):
                    dropped_double_switches += 1
                    continue

                interaction_sig = get_interaction_signature(turn)
                if interaction_counts.get(interaction_sig, 0) >= max_per_interaction:
                    dropped_duplicates += 1
                    continue

                interaction_counts[interaction_sig] = interaction_counts.get(interaction_sig, 0) + 1

                # Generate ChatML row
                chatml = format_turn_to_chatml(turn)

                # Check for "unknown" in assistant completion (after normalization)
                assistant_content = chatml["messages"][2]["content"]
                if "unknown" in assistant_content.lower():
                    dropped_unknown += 1
                    continue

                # Count orders after truncation
                after_orders = assistant_content.split(", ")
                after_count = len(after_orders)
                order_counts_after[after_count] = order_counts_after.get(after_count, 0) + 1

                if before_count > 2:
                    truncated_orders += 1

                processed_examples.append(chatml)

    # Deduplicate exact (user, assistant) pairs
    seen_pairs = set()
    deduplicated_examples = []
    exact_dupes_removed = 0
    for ex in processed_examples:
        user_content = ex["messages"][1]["content"]
        assistant_content = ex["messages"][2]["content"]
        pair = (user_content, assistant_content)
        if pair in seen_pairs:
            exact_dupes_removed += 1
            continue
        seen_pairs.add(pair)
        deduplicated_examples.append(ex)

    # Write output (write mode, not append, to new file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as out:
        for ex in deduplicated_examples:
            out.write(json.dumps(ex, ensure_ascii=False) + "\n")

    # Generate cleaning report
    report_path = output_path.with_name("cleaning_report.txt")
    with report_path.open("w", encoding="utf-8") as rpt:
        rpt.write("=== CLEAN_MASTER_DATA CLEANING REPORT ===\n\n")
        rpt.write(f"Input file: {input_path}\n")
        rpt.write(f"Output file: {output_path}\n\n")
        rpt.write(f"Scanned {total_matches} battles -> Kept {kept_matches} winning battles.\n")
        rpt.write(f"Dropped {dropped_double_switches} double switches and {dropped_duplicates} repetitive matchup turns (interaction sig).\n")
        rpt.write(f"Dropped {dropped_unknown} rows containing 'unknown' in assistant.\n")
        rpt.write(f"Truncated {truncated_orders} rows from >2 orders to 2 orders.\n")
        rpt.write(f"Removed {exact_dupes_removed} exact duplicate (user, assistant) pairs.\n")
        rpt.write(f"Final rows written: {len(deduplicated_examples)}\n\n")

        rpt.write("Order count distribution BEFORE truncation:\n")
        for k in sorted(order_counts_before.keys()):
            rpt.write(f"  {k} orders: {order_counts_before[k]} rows\n")
        rpt.write("\nOrder count distribution AFTER truncation:\n")
        for k in sorted(order_counts_after.keys()):
            rpt.write(f"  {k} orders: {order_counts_after[k]} rows\n")
        rpt.write("\n")

    print(
        f"Scanned {total_matches} battles -> Kept {kept_matches} winning battles.\n"
        f"Dropped {dropped_double_switches} double switches and {dropped_duplicates} repetitive matchup turns.\n"
        f"Dropped {dropped_unknown} rows with 'unknown'.\n"
        f"Truncated {truncated_orders} rows from >2 orders.\n"
        f"Removed {exact_dupes_removed} exact duplicate pairs.\n"
        f"Successfully exported {len(deduplicated_examples)} clean turns to {output_path}.\n"
        f"Report written to {report_path}."
    )


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]
    clean_master_dataset(
        input_path=project_root / "data/raw/master.jsonl",
        output_path=project_root / "data/processed/clean_turns.jsonl",
        max_per_interaction=3,
    )