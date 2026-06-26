import re

with open('/Users/leonida/.gemini/antigravity/brain/f649987a-99c5-40ca-88d5-e841a1d98d65/scratch/notebook_clean_summary.txt', 'r', encoding='utf-8') as f:
    text = f.read()

cells = text.split("================================================================================\n\n")

def print_batch(start, end):
    for cell in cells:
        m = re.search(r"CELL (\d+)", cell)
        if not m:
            continue
        cell_num = int(m.group(1))
        if start <= cell_num <= end:
            print(cell.strip())
            print("="*80)

# Let's print cells 31 to 42
print_batch(31, 42)
