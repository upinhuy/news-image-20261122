#!/usr/bin/env python3
"""Render the world news of Sunday 22 November 2026 as one 1024x1024 PNG.

Layout: navy masthead with the date, three lead stories, then a UTC timeline
of 47 further stories, each with its reporting wire as a source pill.
Deterministic: no timestamps, no randomness, fixed font metrics.
"""
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
NAVY = (22, 35, 63)
NAVY_LIGHT = (38, 56, 92)
INK = (24, 24, 24)
MUTED = (90, 86, 76)
RED = (178, 34, 34)
GOLD = (212, 175, 55)
RULE = (180, 172, 150)
ROW_ALT = (238, 232, 218)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
F_BIG = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 52)
F_MED = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 20)
F_KICK = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 14)
F_SUM = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 13)
F_SEC = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 14)
F_TIME = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 12)
F_TXT = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 13)
F_PILL = ImageFont.truetype(FONT_DIR + "DejaVuSans-Bold.ttf", 10)
F_FOOT = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 11)
F_SUB = ImageFont.truetype(FONT_DIR + "DejaVuSans.ttf", 14)

LEADS = [
    ("CLIMATE TALKS", "COP31 COLLAPSES WITH NO DEAL",
     "EU rejects a final draft that drops fossil fuels; talks end in Antalya with no agreement.",
     "REUTERS"),
    ("LIBYA", "DRONE BLAST HITS RUSSIAN WARSHIP",
     "Suspected Ukrainian sea drones strike a Russian vessel at the Benghazi naval base.",
     "REUTERS"),
    ("MEXICO", "\u2018EL CHAPO ISIDRO\u2019 CAPTURED",
     "11 killed as troops seize an FBI most-wanted cartel boss in a Sinaloa raid.",
     "AP"),
]

# (UTC time, headline, source) — every item reported on 22 November 2026.
TIMELINE = [
    ("00:30", "Iran strikes 3 tankers near Strait of Hormuz", "AP"),
    ("02:10", "Bahrain: Iranian strike wounded two at industrial site", "REUTERS"),
    ("03:22", "Russia-bound ship attacked by drones in Gulf of Finland", "BBC"),
    ("05:40", "Houthis fire on Saudi Arabia as Gulf tensions rise", "REUTERS"),
    ("06:00", "Verstappen wins Las Vegas Grand Prix", "BBC"),
    ("06:05", "Boat capsizes on way to funeral in Nigeria; 24 dead", "AP"),
    ("08:26", "F1 presses on with Qatar & Abu Dhabi finale", "AP"),
    ("09:24", "Eisenkot condemns settler attacks as \u2018terrorism\u2019", "AP"),
    ("09:50", "Netanyahu and Eisenkot open coalition talks", "REUTERS"),
    ("10:40", "Israeli strike in north Gaza wounds several", "AP"),
    ("11:05", "Russian missile hits Kryvyi Rih; 2 killed, scores hurt", "AP"),
    ("11:30", "Russia grasps US offer on European security", "AP"),
    ("12:00", "Poland says Russian missiles hit its territory", "AP"),
    ("12:14", "Russian drone hits Kyiv-region block; 14 missing", "REUTERS"),
    ("12:58", "Haugan wins men\u2019s World Cup slalom", "AP"),
    ("13:30", "Gukesh vs Sindarov: youngest World Chess final ever", "AL JAZEERA"),
    ("14:00", "China opposes US FCC ban on Chinese telecoms", "REUTERS"),
    ("14:30", "Australia criticises US budget office over AUKUS", "REUTERS"),
    ("15:05", "Indonesia factory fire: 3 dead, dozens missing", "BBC"),
    ("15:20", "Nepal PM Balen Shah begins first visit to India", "AP"),
    ("15:40", "US seeks answers from Nvidia on China chip sales", "REUTERS"),
    ("16:00", "Compass Group plans to move listing to New York", "FT"),
    ("16:12", "Bulgari jeweller Paolo Bulgari dies aged 89", "BBC"),
    ("16:30", "FBI investigates apparent hack of crime database", "BBC"),
    ("16:50", "Trump vows to work with Democrats on 10% card cap", "REUTERS"),
    ("17:10", "US Army to detonate unstable explosives despite court order", "BBC"),
    ("17:30", "UN talks extend \u2018killer robot\u2019 rules work to 2028", "AP"),
    ("17:57", "Boy, 7, pulled from rubble after Russian strike", "BBC"),
    ("18:05", "China, ASEAN struggle over South China Sea code", "DW"),
    ("18:08", "Drones hit homes and UN offices in Khartoum", "REUTERS"),
    ("18:20", "South Korea minister quits over AI exam-cheating scandal", "BBC"),
    ("18:40", "EU and Indonesia sign landmark trade deal", "REUTERS"),
    ("19:05", "UK and EU edge closer in landmark post-Brexit deal", "BBC"),
    ("19:30", "Myanmar junta calls ASEAN decision \u2018unfair\u2019", "REUTERS"),
    ("19:57", "France seeks UN meeting over Kyiv embassy strikes", "AP"),
    ("19:59", "Liverpool thrash 10-man Man Utd 4-0", "BBC"),
    ("20:15", "Alcaraz outplays Zverev for first ATP Finals title", "BBC"),
    ("20:26", "Democrats take largest House majority since 1992", "BBC"),
    ("20:28", "May warns Burnham \u2018Brexit is done\u2019 after EU talks", "BBC"),
    ("20:40", "Wall Street suffers worst week since Covid", "REUTERS"),
    ("21:00", "Anthropic\u2019s unusual IPO process chafed bankers", "NYT"),
    ("21:14", "Clariant and CD&R in talks to buy Ashland", "REUTERS"),
    ("21:22", "Miley Cyrus marries Maxx Morando in California", "BBC"),
    ("21:30", "Bank of England directors profited from slavery era", "GUARDIAN"),
    ("21:44", "FIFA to confirm UK as 2035 Women\u2019s World Cup host", "BBC"),
    ("21:55", "Kansas City Current win first NWSL title", "CBC"),
    ("22:05", "Wembanyama drops 50 as Spurs roll past Pelicans", "AP"),
]

PILL_COLORS = {
    "REUTERS": (255, 128, 0),
    "BBC": (187, 25, 25),
    "AP": (20, 20, 20),
    "AL JAZEERA": (0, 122, 122),
    "FT": (156, 43, 46),
    "DW": (0, 84, 160),
    "NYT": (60, 60, 60),
    "GUARDIAN": (0, 86, 179),
    "CBC": (195, 32, 32),
}


def pill(draw, x, y, label):
    """Draw a source pill with its right edge at x, top at y; return its width."""
    w = int(draw.textlength(label, font=F_PILL)) + 12
    h = 14
    draw.rounded_rectangle([x - w, y, x, y + h], radius=7,
                           fill=PILL_COLORS.get(label, (90, 90, 90)))
    draw.text((x - w + 6, y + 2), label, font=F_PILL, fill=(255, 255, 255))
    return w


def fit(draw, text, font, max_w):
    if draw.textlength(text, font=font) <= max_w:
        return text
    while text and draw.textlength(text + "\u2026", font=font) > max_w:
        text = text[:-1]
    return text + "\u2026"


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- masthead ---
    d.rectangle([0, 0, W, 104], fill=NAVY)
    d.rectangle([0, 104, W, 108], fill=GOLD)
    kick = "THE WORLD IN ONE DAY  \u00b7  50 STORIES FROM THE WORLD\u2019S WIRES"
    d.text((28, 12), kick, font=F_KICK, fill=GOLD)
    d.text((28, 34), "SUNDAY 22 NOVEMBER 2026", font=F_BIG, fill=(255, 255, 255))
    d.text((28, 88), "Sunday 22 November 2026  \u00b7  reported around the world, all times UTC",
           font=F_SUB, fill=(200, 208, 224))

    # --- three lead stories ---
    col_w = 312
    x0 = 28
    for i, (kicker, head, summ, src) in enumerate(LEADS):
        x = x0 + i * (col_w + 16)
        d.text((x, 122), kicker, font=F_KICK, fill=RED)
        d.line([x, 142, x + col_w, 142], fill=RULE, width=1)
        lines = textwrap.wrap(head, width=22)
        y = 150
        for ln in lines[:3]:
            d.text((x, y), ln, font=F_MED, fill=INK)
            y += 24
        sy = y + 4
        for ln in textwrap.wrap(summ, width=46)[:2]:
            d.text((x, sy), ln, font=F_SUM, fill=MUTED)
            sy += 16
        pill(d, x + col_w, 246, src)
    d.line([28, 268, W - 28, 268], fill=RULE, width=1)

    # --- timeline header ---
    d.text((28, 278), "THE DAY IN BRIEF", font=F_SEC, fill=NAVY)
    d.text((W - 28 - d.textlength("ALL TIMES UTC  \u00b7  SOURCE IN BRACKETS", font=F_KICK),
            280), "ALL TIMES UTC  \u00b7  SOURCE IN BRACKETS", font=F_KICK, fill=MUTED)

    # --- timeline rows ---
    top, bottom = 302, 1000
    n = len(TIMELINE)
    rh = (bottom - top) / n
    for i, (t, head, src) in enumerate(TIMELINE):
        y = top + i * rh
        if i % 2 == 1:
            d.rectangle([28, y, W - 28, y + rh], fill=ROW_ALT)
        d.text((30, y + 1), t, font=F_TIME, fill=NAVY_LIGHT)
        pw = int(d.textlength(src, font=F_PILL)) + 12
        max_txt = (W - 28 - pw - 8) - 84
        d.text((84, y + 1), fit(d, head, F_TXT, max_txt), font=F_TXT, fill=INK)
        pill(d, W - 30, y + 1, src)

    d.line([28, 1000, W - 28, 1000], fill=RULE, width=1)
    d.text((28, 1006), "Sources: Reuters \u00b7 BBC \u00b7 AP \u00b7 Al Jazeera \u00b7 NYT \u00b7 FT \u00b7 CBC \u00b7 DW \u00b7 Guardian",
           font=F_FOOT, fill=MUTED)

    img.save("entry.png", format="PNG", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
