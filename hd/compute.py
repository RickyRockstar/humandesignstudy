# hd/compute.py
import swisseph as swe
from datetime import datetime, timedelta

GATE_SIZE = 360 / 64
LINE_SIZE = GATE_SIZE / 6

PLANETS = [
    swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS,
    swe.JUPITER, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO
]

# Channel -> (gate1, gate2)
CHANNELS = {
    # Sacral channels
    "Sacral": [(3,60),(5,15),(9,52),(14,2),(27,50),(29,46),(34,20),(42,53)],
    # Manifestor / Throat channels (approximation)
    "Manifestor": [(12,22),(16,48),(35,36),(45,21),(51,25),(55,39)],
    # Other centers just for Reflector calculation
    "G": [(1,2),(10,15),(13,33),(25,51)],
    "Splenic": [(48,16),(18,58),(28,38),(32,54)],
    "Emotional": [(6,59),(7,31),(19,49),(30,41)],
    "Root": [(52,58),(53,42),(54,32),(58,38)]
}


def longitude_to_gate_and_line(longitude):
    gate = int(longitude // GATE_SIZE) + 1
    line = int((longitude % GATE_SIZE) // LINE_SIZE) + 1
    return gate, line


def compute_planet_gates(jd):
    """Compute gates for all planets"""
    gates = {}
    for planet in PLANETS:
        long = swe.calc_ut(jd, planet)[0][0]
        gate, line = longitude_to_gate_and_line(long)
        gates[planet] = {"gate": gate, "line": line}
    return gates


def is_channel_complete(channel, personality_gates, design_gates):
    """Check if both gates of a channel are hit by any planet in personality or design chart"""
    all_gates = [g["gate"] for g in personality_gates.values()] + \
                [g["gate"] for g in design_gates.values()]
    return channel[0] in all_gates and channel[1] in all_gates


def compute_centers(personality_gates, design_gates):
    """Determine which centers are defined"""
    centers_defined = {}
    for center, channels in CHANNELS.items():
        centers_defined[center] = any(is_channel_complete(ch, personality_gates, design_gates) for ch in channels)
    return centers_defined


def determine_type(centers):
    sacral = centers.get("Sacral", False)
    manifestor = centers.get("Manifestor", False)
    # Reflector: no centers defined
    if not any(centers.values()):
        return "Reflector"
    elif not sacral and manifestor:
        return "Manifestor"
    elif sacral and manifestor:
        return "Manifesting Generator"
    elif sacral and not manifestor:
        return "Generator"
    elif not sacral and not manifestor:
        return "Projector"
    else:
        return "Projector"  # fallback


def compute_hd_gates(year, month, day, hour, lat, lon):
    birth_dt = datetime(year, month, day) + timedelta(hours=hour)
    jd_personality = swe.julday(
        birth_dt.year, birth_dt.month, birth_dt.day,
        birth_dt.hour + birth_dt.minute / 60
    )
    jd_design = swe.julday(
        (birth_dt - timedelta(days=88)).year,
        (birth_dt - timedelta(days=88)).month,
        (birth_dt - timedelta(days=88)).day,
        (birth_dt - timedelta(days=88)).hour
        + (birth_dt - timedelta(days=88)).minute / 60
    )

    personality_gates = compute_planet_gates(jd_personality)
    design_gates = compute_planet_gates(jd_design)

    # Profile
    p_sun_line = personality_gates[swe.SUN]["line"]
    d_sun_line = design_gates[swe.SUN]["line"]
    profile = f"{p_sun_line}/{d_sun_line}"

    # Centers
    centers = compute_centers(personality_gates, design_gates)

    # Type
    hd_type = determine_type(centers)

    return {
        "personality": personality_gates,
        "design": design_gates,
        "profile": profile,
        "type": hd_type,
        "centers": centers
    }