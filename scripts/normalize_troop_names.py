"""
Script to normalize troop PNG file names.
This script renames all troop PNG files to a consistent naming convention.
"""
import os
import shutil
import json


# Mapping of old names to normalized names
TROOP_NAME_MAPPING = {
    # Super troops (keep s_ prefix)
    "s_arqueira": "s_archer",
    "s_barbaro": "s_barbarian",
    "s_balao": "s_balloon",
    "s_bruxa": "s_witch",
    "s_corredor": "s_runner",
    "s_dragao": "s_dragon",
    "s_gigante": "s_giant",
    "s_goblin": "s_goblin",
    "s_lancador": "s_lancer",
    "s_lava": "s_lava_hound",
    "s_mago": "s_wizard",
    "s_mineiro": "s_miner",
    "s_quebrador": "s_wall_breaker",
    "s_servo": "s_servant",
    "s_valk": "s_valkyrie",
    "s_yeti": "s_yeti",
    
    # Regular troops - abbreviated to full names
    "arq": "archer",
    "bb": "barbarian",
    "balao": "balloon",
    "bb_infernal": "inferno_dragon",
    "bbdragao": "baby_dragon",
    "bomb": "bomber",
    "bruxa": "witch",
    "cacadora": "hunter",
    "ciclope": "cyclops",
    "corredor": "runner",
    "curadoura": "healer",
    "dgdirigivel": "blimp",
    "dgeletrico": "electro_dragon",
    "dragao": "dragon",
    "druida": "druid",
    "fornalha": "furnace",
    "gg": "giant",
    "gob": "goblin",
    "golem": "golem",
    "golem_gelo": "ice_golem",
    "golem_meteoro": "meteor_golem",
    "hera": "queen",
    "lancador": "lancer",
    "lava": "lava_hound",
    "mago": "wizard",
    "mineiro": "miner",
    "mini_guardiao": "mini_guardian",
    "peka": "pekka",
    "servo": "servant",
    "titan": "titan",
    "valk": "valkyrie",
    "yeti": "yeti",
}


def normalize_troop_names():
    """Normalizes all troop PNG file names according to the mapping."""
    troops_dir = os.path.join("templates", "troops")
    
    if not os.path.exists(troops_dir):
        print(f"Error: Directory {troops_dir} not found!")
        return
    
    # Create backup directory
    backup_dir = os.path.join("templates", "troops_backup")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Created backup directory: {backup_dir}")
    
    renamed_files = []
    skipped_files = []
    
    # Process each file
    for filename in os.listdir(troops_dir):
        if not filename.endswith(".png"):
            continue
            
        old_name = filename.replace(".png", "")
        new_name = TROOP_NAME_MAPPING.get(old_name)
        
        if new_name is None:
            # File name is already normalized or not in mapping
            print(f"Skipping {filename} (not in mapping)")
            skipped_files.append(filename)
            continue
        
        old_path = os.path.join(troops_dir, filename)
        new_path = os.path.join(troops_dir, f"{new_name}.png")
        
        # Check if target already exists
        if os.path.exists(new_path):
            print(f"Warning: Target {new_name}.png already exists, skipping {filename}")
            skipped_files.append(filename)
            continue
        
        # Backup original
        backup_path = os.path.join(backup_dir, filename)
        shutil.copy2(old_path, backup_path)
        
        # Rename file
        os.rename(old_path, new_path)
        renamed_files.append((filename, f"{new_name}.png"))
        print(f"Renamed: {filename} -> {new_name}.png")
    
    # Save mapping for reference
    mapping_file = os.path.join("templates", "troops", "name_mapping.json")
    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump({
            "renamed_files": renamed_files,
            "skipped_files": skipped_files,
            "mapping": TROOP_NAME_MAPPING
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== Summary ===")
    print(f"Renamed: {len(renamed_files)} files")
    print(f"Skipped: {len(skipped_files)} files")
    print(f"Backup created in: {backup_dir}")
    print(f"Mapping saved to: {mapping_file}")
    
    if renamed_files:
        print("\n=== Renamed Files ===")
        for old, new in renamed_files:
            print(f"  {old} -> {new}")


def update_code_references():
    """Updates code references to use new normalized names."""
    # Files that might reference troop names
    code_files = [
        "config/army.json",
        "functions/create_army.py",
    ]
    
    # Read mapping
    mapping_file = os.path.join("templates", "troops", "name_mapping.json")
    if not os.path.exists(mapping_file):
        print("Error: name_mapping.json not found. Run normalize_troop_names() first!")
        return
    
    with open(mapping_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Create reverse mapping (old -> new)
    reverse_mapping = {}
    for old, new in data["mapping"].items():
        reverse_mapping[old] = new
    
    # Update army.json
    army_json = os.path.join("config", "army.json")
    if os.path.exists(army_json):
        with open(army_json, "r", encoding="utf-8") as f:
            army_config = json.load(f)
        
        updated = False
        for troop in army_config.get("troops", []):
            old_name = troop.get("name")
            if old_name in reverse_mapping:
                troop["name"] = reverse_mapping[old_name]
                updated = True
                print(f"Updated army.json: {old_name} -> {reverse_mapping[old_name]}")
        
        if updated:
            # Backup original
            backup_path = army_json + ".backup"
            shutil.copy2(army_json, backup_path)
            
            # Save updated
            with open(army_json, "w", encoding="utf-8") as f:
                json.dump(army_config, f, indent=2, ensure_ascii=False)
            print(f"Updated {army_json} (backup saved to {backup_path})")


if __name__ == "__main__":
    print("=== Normalizing Troop PNG File Names ===\n")
    
    response = input("This will rename troop PNG files. A backup will be created. Continue? (y/n): ")
    if response.lower() != "y":
        print("Cancelled.")
        exit(0)
    
    normalize_troop_names()
    
    print("\n=== Updating Code References ===\n")
    response = input("Update code references (army.json)? (y/n): ")
    if response.lower() == "y":
        update_code_references()
    
    print("\n=== Done ===")
