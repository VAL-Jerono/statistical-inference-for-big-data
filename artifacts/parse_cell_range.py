import re

with open('/Users/leonida/.gemini/antigravity/brain/f649987a-99c5-40ca-88d5-e841a1d98d65/scratch/all_cell_outputs.txt', 'r', encoding='utf-8') as f:
    text = f.read()

cells = text.split("============================================================\n\n")

for cell in cells:
    if "=== CELL" not in cell:
        continue
    m = re.search(r"=== CELL (\d+) ===", cell)
    if not m:
        continue
    cell_num = int(m.group(1))
    
    # We want to print comments and outputs for cells 6 to 39
    if 6 <= cell_num <= 39:
        print(f"=== CELL {cell_num} ===")
        # Print comments and outputs from this cell
        lines = cell.split('\n')
        # Print up to 10 comments and 30 outputs
        comm_lines = []
        out_lines = []
        in_comm = False
        in_out = False
        for l in lines:
            if l.startswith("Comments:"):
                in_comm = True
                in_out = False
                continue
            elif l.startswith("Outputs:"):
                in_comm = False
                in_out = True
                continue
            
            if in_comm:
                comm_lines.append(l)
            elif in_out:
                out_lines.append(l)
        
        if comm_lines:
            print("  Comments:")
            for cl in comm_lines[:6]:
                print("    " + cl)
            if len(comm_lines) > 6:
                print("    ...")
        if out_lines:
            print("  Outputs:")
            for ol in out_lines[:25]:
                print("    " + ol)
            if len(out_lines) > 25:
                print("    ...")
        print("-" * 50)
