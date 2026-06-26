import re

with open('/Users/leonida/.gemini/antigravity/brain/f649987a-99c5-40ca-88d5-e841a1d98d65/scratch/stats_extracted.txt', 'r', encoding='utf-8') as f:
    text = f.read()

cells = text.split("================================================================================")

with open('/Users/leonida/.gemini/antigravity/brain/f649987a-99c5-40ca-88d5-e841a1d98d65/scratch/notebook_clean_summary.txt', 'w', encoding='utf-8') as out_f:
    for idx, cell in enumerate(cells):
        if "=== CELL" not in cell:
            continue
        m = re.search(r"=== CELL (\d+) \(CODE\) ===", cell)
        if not m:
            continue
        cell_num = m.group(1)
        
        # Get all text from cell
        lines = cell.split('\n')
        comment_lines = []
        output_lines = []
        in_source = False
        in_outputs = False
        
        for line in lines:
            if line.startswith("Source:"):
                in_source = True
                in_outputs = False
                continue
            elif line.startswith("Outputs:"):
                in_source = False
                in_outputs = True
                continue
            
            if in_source:
                if line.strip().startswith("#"):
                    comment_lines.append(line.strip())
            elif in_outputs:
                output_lines.append(line)
        
        out_f.write(f"CELL {cell_num}\n")
        if comment_lines:
            out_f.write("  Comments:\n")
            for cl in comment_lines[:15]:
                out_f.write("    " + cl + "\n")
            if len(comment_lines) > 15:
                out_f.write("    ...\n")
        if output_lines:
            out_f.write("  Outputs:\n")
            # Remove empty outputs and binary image data
            filtered = [l for l in output_lines if l.strip() and "binary image data" not in l and "display_data" not in l and "stream" not in l]
            for fl in filtered:
                out_f.write("    " + fl + "\n")
        out_f.write("="*80 + "\n\n")

print("Saved clean summary to scratch/notebook_clean_summary.txt")
