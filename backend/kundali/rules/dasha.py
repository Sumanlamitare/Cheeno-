"""Rule-based interpretation of the running Dasha periods."""

from __future__ import annotations

from ..jyotish.constants import DUSTHANAS, KENDRAS, ordinal
from .data.dasha import DASHA_THEME
from .data.houses import HOUSE_MATTERS
from .engine import ChartContext, rule, run_rules, synthesize

C = "dasha"
THEMES = {
    "dasha.strength": "Condition of the period lords",
    "dasha.stability": "Stability and foundation",
    "dasha.fortune": "Fortune and growth",
    "dasha.gains": "Gains and resources",
    "dasha.challenge": "Challenges and adjustments",
    "dasha.yoga": "Yogas activated",
    "dasha.harmony": "Relationship between the period lords",
    "dasha.transit": "Supporting transits",
}


def _level_rules(level: str, label: str, tier_main: str, tier_sub: str):
    L = level
    return [
        rule(f"dasha_{L}_strong", C, "dasha.strength", tier_main, "positive", [{"t": "strong", "p": L}],
             f"The {label} lord {{{L}}} is strong, which tradition regards as favourable for the matters it signifies "
             "and rules.", f"Strong {label} lord", subject=L),
        rule(f"dasha_{L}_weak", C, "dasha.strength", tier_main, "negative", [{"t": "weak", "p": L}],
             f"The {label} lord {{{L}}} is weak, so tradition expects its results to need more effort and patience.",
             f"Weak {label} lord", subject=L),
        rule(f"dasha_{L}_kendra", C, "dasha.stability", tier_sub, "positive", [{"t": "in_house", "p": L, "h": [1, 4, 7, 10]}],
             f"{{{L}}} occupies a kendra, which tradition associates with stability and visible results during its "
             f"{label}.", f"{label} lord in a kendra"),
        rule(f"dasha_{L}_trikona", C, "dasha.fortune", tier_sub, "positive", [{"t": "in_house", "p": L, "h": [5, 9]}],
             f"{{{L}}} occupies a trikona, which tradition associates with fortune, merit and support during its "
             f"{label}.", f"{label} lord in a trikona"),
        rule(f"dasha_{L}_gains", C, "dasha.gains", tier_sub, "positive", [{"t": "in_house", "p": L, "h": [2, 11]}],
             f"{{{L}}} occupies a house of wealth, which tradition associates with gains and resources during its "
             f"{label}.", f"{label} lord in 2nd/11th"),
        rule(f"dasha_{L}_dusthana", C, "dasha.challenge", tier_sub, "negative",
             [{"t": "in_house", "p": L, "h": [6, 8, 12]}, {"t": "not", "c": {"t": "dusthana_lord", "p": L}}],
             f"{{{L}}} occupies a dusthana, which tradition associates with obstacles, expenses or changes that call "
             f"for care during its {label}.", f"{label} lord in a dusthana"),
        rule(f"dasha_{L}_viparita", C, "dasha.challenge", tier_sub, "mixed",
             [{"t": "in_house", "p": L, "h": [6, 8, 12]}, {"t": "dusthana_lord", "p": L}],
             f"{{{L}}} rules and occupies dusthanas (a Viparita pattern): tradition describes difficulties that turn "
             f"unexpectedly to advantage during its {label}.", f"{label} lord: dusthana lord in dusthana"),
        rule(f"dasha_{L}_owns_trikona", C, "dasha.fortune", tier_sub, "positive",
             [{"t": "dasha_lord_owns", "level": L, "h": [5, 9]}],
             f"As a trikona lord, {{{L}}} is a natural giver of good results for this Lagna.", f"{label} lord rules a trikona"),
        rule(f"dasha_{L}_owns_kendra", C, "dasha.stability", "minor", "positive",
             [{"t": "dasha_lord_owns", "level": L, "h": [1, 4, 7, 10]}],
             f"As a kendra lord, {{{L}}} brings the affairs of that pillar of the chart into focus.", f"{label} lord rules a kendra"),
        rule(f"dasha_{L}_owns_dusthana", C, "dasha.challenge", "minor", "mixed",
             [{"t": "dasha_lord_owns", "level": L, "h": [6, 8, 12]}],
             f"{{{L}}} also rules a dusthana, so tradition expects some of its results to involve work, change or "
             "expenditure.", f"{label} lord rules a dusthana"),
        rule(f"dasha_{L}_yoga", C, "dasha.yoga", tier_main, "positive", [{"t": "in_yoga", "p": L}],
             f"{{{L}}} forms yogas in the birth chart; tradition holds that yogas give their results chiefly in the "
             "periods of the planets that form them.", f"{label} lord forms yogas"),
        rule(f"dasha_{L}_vargottama", C, "dasha.strength", "minor", "positive", [{"t": "vargottama", "p": L}],
             f"{{{L}}} is Vargottama, lending steadiness to its {label}.", f"Vargottama {label} lord"),
    ]


def build_rules():
    rules = _level_rules("MD", "Mahadasha", "major", "strong") + _level_rules("AD", "Antardasha", "strong", "moderate")
    rules += [
        rule("dasha_AD_from_MD_good", C, "dasha.harmony", "moderate", "positive",
             [{"t": "from_planet", "p": "AD", "ref": "MD", "h": [1, 4, 5, 7, 9, 10, 11]}],
             "The Antardasha lord is well placed from the Mahadasha lord, which tradition reads as cooperation between "
             "the two periods.", "Antardasha lord's position from the Mahadasha lord"),
        rule("dasha_AD_from_MD_bad", C, "dasha.harmony", "moderate", "negative",
             [{"t": "from_planet", "p": "AD", "ref": "MD", "h": [6, 8, 12]}],
             "The Antardasha lord is in the 6th, 8th or 12th from the Mahadasha lord, which tradition reads as some "
             "friction between the two periods' agendas.", "Antardasha lord's position from the Mahadasha lord"),
    ]
    return rules


RULES = build_rules()


def _activation(ctx: ChartContext, planet: str, label: str) -> dict:
    c = ctx.chart
    owned = c.houses_ruled_by(planet)
    house = c.house_of(planet)
    parts = []
    if owned:
        parts.append(f"as lord of the {', '.join(ordinal(h) for h in owned)} house"
                     f"{'s' if len(owned) > 1 else ''} it brings forward "
                     + "; ".join(HOUSE_MATTERS[h] for h in owned))
    parts.append(f"placed in the {ordinal(house)} house it channels results through {HOUSE_MATTERS[house]}")
    tone = ("supportive" if (house in KENDRAS or house in (5, 9, 11)) and not ctx.is_weak(planet)
            else "demanding" if house in DUSTHANAS and not set(owned) <= DUSTHANAS else "mixed")
    return {
        "planet": planet,
        "level": label,
        "theme": DASHA_THEME[planet],
        "activation": f"During the {planet} {label}, " + "; ".join(parts) + ".",
        "tone": tone,
        "why": [f"{planet} rules the {', '.join(ordinal(h) for h in owned)}" if owned else f"{planet} rules no sign",
                f"{planet} occupies the {ordinal(house)} house"],
    }


def analyze(ctx: ChartContext, gochar: dict | None, sadesati: dict | None) -> dict:
    out = synthesize("the current period", run_rules(ctx, RULES), THEMES)
    out["activations"] = [_activation(ctx, ctx.dasha[k], {"MD": "Mahadasha", "AD": "Antardasha", "PD": "Pratyantardasha"}[k])
                          for k in ("MD", "AD", "PD") if ctx.dasha.get(k)]
    support = []
    if gochar:
        for row in gochar["rows"]:
            if row["planet"] in ("Saturn", "Jupiter"):
                support.append({
                    "text": (f"Transiting {row['planet']} in the {ordinal(row['houseFromMoon'])} from the Moon is "
                             f"traditionally {'favourable' if row['result'] == 'favourable' else 'obstructed by Vedha' if row['result'] == 'obstructed' else 'challenging'}"
                             f", {'supporting' if row['result'] == 'favourable' else 'qualifying'} the results of the "
                             "running periods."),
                    "polarity": "positive" if row["result"] == "favourable" else "negative",
                    "why": [f"{row['planet']} transits {row['signName']}, the {ordinal(row['houseFromMoon'])} from the "
                            f"natal Moon"],
                })
    if sadesati and sadesati.get("active"):
        support.append({"text": f"Sade Sati is active ({sadesati['status'].lower()}), adding Saturn's themes of "
                                "responsibility and patience to this period.", "polarity": "mixed",
                        "why": [f"Saturn transits {sadesati['saturnSignNow']}, relative to the natal Moon in "
                                f"{sadesati['moonSign']}"]})
    out["transitSupport"] = support
    return out
