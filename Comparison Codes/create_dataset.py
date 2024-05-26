import json

speech_dataset = {
    1: "turn left",
    2: "turn right",
    3: "turn right by 90 degree",
    4: "turn left by 180 degree",
    5: "brake",
    6: "turn on engine",
    7: "activate voice control",
    8: "deactivate voice control",
    9: "go forward",
    10: "go backward",
    11: "accelerate",
    12: "turn off engine",
    13: "turn on Engine",
    14: "adjust speed to 5 kmph",
    15: "help",
    16: "fire alert",
    17: "damage alert",
    18: "increase speed to 2 kmph",
    19: "decrease speed to 2 kmph",
    20: "lock hatch",
    21: "rotate turret by 60 degree",
}

with open("speech_dataset_vino.json", "w") as file:
    json.dump(speech_dataset, file, indent=4)  # Add indentation for readability
