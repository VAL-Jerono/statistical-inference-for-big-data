import re

with open('/Users/leonida/.gemini/antigravity/brain/f649987a-99c5-40ca-88d5-e841a1d98d65/scratch/stats_extracted.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's split by the separator
cells = text.split("================================================================================")

for cell in cells:
    if "=== CELL" not in cell:
        continue
    # Extract cell number
    cell_num = re.search(r"=== CELL (\d+) \(CODE\) ===", cell).group(1)
    
    # We want to print cell code comments and the output stream text
    lines = cell.split('\n')
    header_comment = []
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
            in_source = False
            in_outputs = True
            continue
        
        if in_source:
            source_lines.append(line)
            # Capture comments that might explain what cell it is
            if line.strip().startswith("#"):
                header_comment.append(line.strip())
        elif in_outputs:
            output_lines.append(line)
            
    # If the output has meaningful text (not just empty lines or image output placeholders)
    # let's print it
    out_text = "\n".join(output_lines).strip()
    if out_text:
        print(f"Cell {cell_num}:")
        if header_comment:
            # Print first 3 comments
            for comm in header_comment[:5]:
                print("  " + comm)
        print("Outputs:")
        # Print first 30 lines of output
        out_lines = out_text.split('\n')
        for line in out_lines[:30]:
            print("  " + line)
        if len(out_lines) > 30:
            print("  ... (truncated output)")
        print("-" * 50)
