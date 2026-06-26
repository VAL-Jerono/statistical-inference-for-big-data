import re

with open('/Users/leonida/.gemini/antigravity/brain/f649987a-99c5-40ca-88d5-e841a1d98d65/scratch/stats_extracted.txt', 'r', encoding='utf-8') as f:
    text = f.read()

cells = text.split("================================================================================")

with open('/Users/leonida/.gemini/antigravity/brain/f649987a-99c5-40ca-88d5-e841a1d98d65/scratch/all_cell_outputs.txt', 'w', encoding='utf-8') as out_f:
    for cell in cells:
        if "=== CELL" not in cell:
            continue
        cell_num = re.search(r"=== CELL (\d+) \(CODE\) ===", cell).group(1)
        lines = cell.split('\n')
        
        source_lines = []
        output_lines = []
        in_source = False
        in_outputs = False
        
        for line in lines:
            if line.startswith("Source:"):
                in_source = True
                in_outputs = False
                continue
            elif line.startswith("Outputs:"):
                in_source = True # Actually we want to write source comments too
                in_outputs = True
                continue
            
            if in_source and not in_outputs:
                # Capture comments only to keep it clean
                if line.strip().startswith("#"):
                    source_lines.append(line)
            elif in_outputs:
                output_lines.append(line)
        
        out_f.write(f"=== CELL {cell_num} ===\n")
        if source_lines:
            out_f.write("Comments:\n")
            out_f.write("\n".join(source_lines) + "\n")
        if output_lines:
            out_f.write("Outputs:\n")
            # Filter out lines containing binary image data
            filtered_outputs = [l for l in output_lines if "binary image data" not in l]
            out_f.write("\n".join(filtered_outputs) + "\n")
        out_f.write("="*60 + "\n\n")

print("Saved all cell outputs to scratch/all_cell_outputs.txt")
