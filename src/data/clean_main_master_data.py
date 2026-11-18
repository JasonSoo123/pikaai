import json
from pathlib import Path
import re

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


# ===== NAME NORMALIZATION (shared with clean_master_data.py) =====
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
    """Normalize species names in user prompt."""
    for display, canonical in SPECIES_NORMALIZE_MAP.items():
        text = re.sub(rf'\b{re.escape(display)}\b', canonical, text, flags=re.IGNORECASE)
    return text


def format_side_conditions(conditions):
    active = []
    for k, v in conditions.items():
        if v and v > 0:
            active.append(f"{k}: {v}")

    return ", ".join(active) if active else "None"


def format_pokemon(p):
    species = normalize_species(p['species'])
    parts = [f"Slot {p['slot']}: {species} ({p['hp_pct']}% HP, {p.get('item', 'unknown')}, {p.get('ability', 'unknown')}, status: {p.get('status', 'None')})"]
    return parts[0]

def format_pokemon_simple(p):
    species = normalize_species(p['species'])
    return f"{species} ({p['hp_pct']}% HP, status: {p.get('status', 'None')})"

def format_active(active):
    return ", ".join(format_pokemon(p) for p in active)

def format_bench(bench):
    return ", ".join(format_pokemon_simple(p) for p in bench)

def get_last_turn_flags(battle_history):
    if not battle_history:
        return "None"
    last_turn = battle_history[-1]
    flags = []
    for action in last_turn.get("opponent_action", []):
        # action format: "{species} uses {move} targeting {target}"
        lower = action.lower()
        if "uses" not in lower:
            continue
        species = action.split(" uses ")[0].strip()
        move = action.split(" uses ")[1].split(" targeting ")[0].strip().lower()
        if move in PROTECT_MOVES:
            flags.append(f"{normalize_species(species)} used {normalize_move(move)} (consecutive protect may fail)")
        elif move in RECHARGE_MOVES:
            flags.append(f"{normalize_species(species)} used {normalize_move(move)} (must recharge)")
    return "; ".join(flags) if flags else "None"

def format_terrain(terrain):
    if terrain in (None, "None", ""):
        return "None"
    return f"{{{terrain}: 4}}"

def convert_turn(record):
    field = record["field"]
    weather = field.get("weather", "None")
    terrain = field.get("terrain", "None")
    trick_room = field.get("trick_room", 0)

    opp_flags = get_last_turn_flags(record.get("battle_history", []))

    my_side = record["my_side"]
    opp_side = record["opponent_side"]

    my_conditions = format_side_conditions(my_side.get("side_conditions", {}))
    opp_conditions = format_side_conditions(opp_side.get("side_conditions", {}))

    user_content = (
        f"Weather: {weather}, Terrain: {format_terrain(terrain)}, Trick Room: {trick_room}\n"
        f"Opp Last-Turn Flags: {opp_flags}\n"
        f"My Side Conditions: {my_conditions} | My Active: {format_active(my_side['active'])} | My Bench: {format_bench(my_side['bench'])}\n"
        f"Opp Side Conditions: {opp_conditions} | Opp Active: {format_active(opp_side['active'])} | Opp Bench: {format_bench(opp_side['bench'])}\n"
        f"Provide optimal target orders."
    )

    # FIX: Only take first 2 orders from target_orders
    target_orders = record.get("target_orders", [])
    orders = target_orders[:2]  # At most 2 orders

    assistant_content = ", ".join(orders)

    # Normalize names in both user and assistant
    user_content = normalize_user_prompt(user_content)
    assistant_content = normalize_order_text(assistant_content)

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content}
        ]
    }

def clean_main_master_dataset(input_path, output_path, mode="w"):
    """
    Convert main_master.jsonl turns to ChatML format.

    Args:
        input_path: Path to main_master.jsonl
        output_path: Path to output file (clean_turns.jsonl)
        mode: File open mode - "w" to create new, "a" to append (default "w")
    """
    processed_examples = []
    order_counts_before = {}
    order_counts_after = {}
    dropped_unknown = 0
    truncated_orders = 0

    with open(input_path, "r") as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)

            # Count orders before truncation
            before_count = len(record.get("target_orders", []))
            order_counts_before[before_count] = order_counts_before.get(before_count, 0) + 1

            converted = convert_turn(record)

            # Check for "unknown" in assistant
            assistant_content = converted["messages"][2]["content"]
            if "unknown" in assistant_content.lower():
                dropped_unknown += 1
                continue

            # Count orders after truncation
            after_orders = assistant_content.split(", ")
            after_count = len(after_orders)
            order_counts_after[after_count] = order_counts_after.get(after_count, 0) + 1

            if before_count > 2:
                truncated_orders += 1

            processed_examples.append(converted)

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

    # Count conflicting labels (same user, different assistant)
    user_to_assistants = {}
    for ex in processed_examples:
        user_content = ex["messages"][1]["content"]
        assistant_content = ex["messages"][2]["content"]
        if user_content not in user_to_assistants:
            user_to_assistants[user_content] = set()
        user_to_assistants[user_content].add(assistant_content)

    conflicting_count = sum(1 for assists in user_to_assistants.values() if len(assists) > 1)

    # Write output (use specified mode)
    with open(output_path, mode, encoding="utf-8") as fout:
        for ex in deduplicated_examples:
            fout.write(json.dumps(ex, ensure_ascii=False) + "\n")

    # Generate cleaning report
    report_path = Path(output_path).with_name("cleaning_report_main.txt")
    with open(report_path, "w", encoding="utf-8") as rpt:
        rpt.write("=== CLEAN_MAIN_MASTER_DATA CLEANING REPORT ===\n\n")
        rpt.write(f"Input file: {input_path}\n")
        rpt.write(f"Output file: {output_path}\n\n")
        rpt.write(f"Total rows processed: {len(processed_examples) + dropped_unknown}\n")
        rpt.write(f"Dropped {dropped_unknown} rows containing 'unknown' in assistant.\n")
        rpt.write(f"Truncated {truncated_orders} rows from >2 orders to 2 orders.\n")
        rpt.write(f"Removed {exact_dupes_removed} exact duplicate (user, assistant) pairs.\n")
        rpt.write(f"Conflicting labels (same user, different assistant): {conflicting_count}\n")
        rpt.write(f"Final rows written: {len(deduplicated_examples)}\n\n")

        rpt.write("Order count distribution BEFORE truncation:\n")
        for k in sorted(order_counts_before.keys()):
            rpt.write(f"  {k} orders: {order_counts_before[k]} rows\n")
        rpt.write("\nOrder count distribution AFTER truncation:\n")
        for k in sorted(order_counts_after.keys()):
            rpt.write(f"  {k} orders: {order_counts_after[k]} rows\n")
        rpt.write("\n")

    print(
        f"Processed {len(processed_examples) + dropped_unknown} rows.\n"
        f"Dropped {dropped_unknown} rows with 'unknown'.\n"
        f"Truncated {truncated_orders} rows from >2 orders.\n"
        f"Removed {exact_dupes_removed} exact duplicate pairs.\n"
        f"Conflicting labels: {conflicting_count}\n"
        f"Successfully exported {len(deduplicated_examples)} clean turns to {output_path}.\n"
        f"Report written to {report_path}."
    )

if __name__ == "__main__":

    project_root = Path(__file__).resolve().parents[2]
    clean_main_master_dataset(
        input_path=project_root / "data/raw/main_master.jsonl",
        output_path=project_root / "data/processed/clean_turns.jsonl"
    )