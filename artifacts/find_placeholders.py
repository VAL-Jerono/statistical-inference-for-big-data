import re

with open('/Users/leonida/Documents/code/statistical-inference-for-big-data/report/HFVS_Full_Report.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

suspicious_patterns = [
    r'\[\[.*?\]\]',
    r'\{\{.*?\}\}',
    r'—\s*\|', # Table cell with empty/dash
    r'\|\s*—', # Table cell with empty/dash
    r'\b(TODO|placeholder|FIXME)\b/i',
    r'(\d+\.\d+\s*–\s*\d+\.\d+)', # ranges like 0.200 - 0.624
    r'(\d+\s*–\s*\d+)',          # ranges like 9.78 - 18.09
]

for idx, line in enumerate(lines):
    line_num = idx + 1
    matched = False
    for pat in suspicious_patterns:
        if re.search(pat, line, re.IGNORECASE):
            matched = True
            break
    # also print lines containing T1, T2, T3, T4, T5, T6, T7, N1, N2, N3, N4, N5, N6
    if not matched:
        for t in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6']:
            if t in line:
                matched = True
                break
    if matched:
        print(f"Line {line_num:4d}: {line.strip()}")
