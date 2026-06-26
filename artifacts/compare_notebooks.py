import json

with open('/Users/leonida/Documents/code/statistical-inference-for-big-data/HFVS_Report_Notebook.ipynb', 'r') as f:
    nb_active = json.load(f)

with open('/Users/leonida/Documents/code/statistical-inference-for-big-data/HFVS_Report_Notebook_backup_20260624_1647.ipynb', 'r') as f:
    nb_backup = json.load(f)

print(f"Active cells count: {len(nb_active['cells'])}")
print(f"Backup cells count: {len(nb_backup['cells'])}")

for i in range(min(len(nb_active['cells']), len(nb_backup['cells']))):
    c_act = nb_active['cells'][i]
    c_bak = nb_backup['cells'][i]
    if c_act['cell_type'] != c_bak['cell_type']:
        print(f"Cell {i} type mismatch: Active {c_act['cell_type']} vs Backup {c_bak['cell_type']}")
        continue
    
    act_src = "".join(c_act.get('source', []))
    bak_src = "".join(c_bak.get('source', []))
    if act_src != bak_src:
        print(f"Cell {i} content mismatch:")
        print("  Active first line:", act_src.splitlines()[0] if act_src.splitlines() else "")
        print("  Backup first line:", bak_src.splitlines()[0] if bak_src.splitlines() else "")
