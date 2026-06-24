#!/usr/bin/env python3
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

replacements = [
    # Data source title emoji
    ('\U0001f5c4\ufe0f <span class="en">Data Source', '<span class="en">Data Source'),
    # Theme toggle toast
    ("toast('\U0001f3a8 '+(next==='dark'?'Dark mode on':'Light mode on'))",
     "toast((next==='dark'?'Dark mode on':'Light mode on'))"),
    # Welcome toast
    ("toast('\U0001f1f0\U0001f1ea Welcome to HFVS Kenya \u2014 click any county to explore')",
     "toast('HFVS Kenya \u2014 click any county to explore')"),
    # Export profile toast
    ("toast(`\U0001f4c4 Profile exported for ${name}`)",
     "toast(`Profile exported for ${name}`)"),
    # CSV export toast
    ("toast('\U0001f4ca Full dataset exported as CSV')",
     "toast('Full dataset exported as CSV')"),
    # Share link copied toast
    ("navigator.clipboard.writeText(url).then(()=>toast('\U0001f517 Link copied!'))",
     "navigator.clipboard.writeText(url).then(()=>toast('Link copied!'))"),
    # Share fallback toast
    ("else toast('\U0001f517 Share: '+url)",
     "else toast('Share: '+url)"),
    # Added to compare toast
    ("toast(`\u2713 Added ${name} to compare`)",
     "toast(`Added ${name} to compare`)"),
    # Share county button emoji
    (">🔗</button>",
     ">link</button>"),
    # theme toggle JS update
    ("document.getElementById('theme-btn').textContent = next==='dark'?'\U0001f319':'\u2600\ufe0f';",
     "document.getElementById('theme-btn').textContent = next==='dark'?'\u25d1':'\u25d0';"),
    # Stakeholder emoji fields in data array — remove emoji key entirely
    ('{emoji:\'\U0001f3db\ufe0f\',role:\'Regulator\'', '{role:\'Regulator\''),
    ('{emoji:\'\U0001f3e0\',role:\'Housing Ministry\'', '{role:\'Housing Ministry\''),
    ('{emoji:\'\U0001f4b0\',role:\'Mortgage Finance\'', '{role:\'Mortgage Finance\''),
    ('{emoji:\'\U0001f3db\ufe0f\',role:\'County Government\'', '{role:\'County Government\''),
    ('{emoji:\'\U0001f91d\',role:\'Development Partners\'', '{role:\'Development Partners\''),
    ('{emoji:\'\U0001f3e1\',role:\'For Everyone\'', '{role:\'For Everyone\''),
    # Remove stk-emoji span from renderStakeholders template
    ('  <span class="stk-emoji">${s.emoji}</span>\n', ''),
    # Any leftover standalone emojis in AI hint text
    ('Ask Claude', 'Ask the AI Advisor'),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f'  Replaced: {repr(old[:60])}')
    else:
        print(f'  NOT FOUND: {repr(old[:60])}')

# Remove any remaining emoji characters using broad unicode ranges
def remove_emojis(text):
    emoji_pattern = re.compile(
        "[\U0001F300-\U0001F9FF"   # misc symbols and pictographs
        "\U0001FA00-\U0001FA9F"    # chess symbols etc
        "\U00002600-\U000027BF"    # misc symbols (but keep arrows: 2190-21FF)
        "\U0001F600-\U0001F64F"    # emoticons
        "\U0001F680-\U0001F6FF"    # transport
        "\U0001F1E0-\U0001F1FF"    # flags
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub('', text)

content = remove_emojis(content)
print('Emoji strip pass complete.')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('index.html updated successfully.')
