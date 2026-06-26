import json
import os

with open('/Users/leonida/Documents/code/statistical-inference-for-big-data/HFVS_Report_Notebook.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

output_path = '/Users/leonida/.gemini/antigravity/brain/f649987a-99c5-40ca-88d5-e841a1d98d65/scratch/stats_extracted.txt'

with open(output_path, 'w', encoding='utf-8') as out_f:
    for idx, cell in enumerate(nb['cells']):
        cell_type = cell.get('cell_type', '')
        if cell_type == 'code':
            source = "".join(cell.get('source', []))
            keywords = ["one_sample", "ttest", "anova", "ols", "mannwhitney", "kruskal", "spearmanr", "kstest", "wilcoxon", "bootstrap", "beta.fit"]
            # We want to extract cells that perform statistical tests or modeling
            # or print metrics
            if any(kw in source.lower() for kw in keywords) or "fig" in source.lower() or "model" in source.lower() or "table" in source.lower():
                out_f.write(f"=== CELL {idx} (CODE) ===\n")
                out_f.write("Source:\n")
                out_f.write(source)
                out_f.write("\n\n")
                
                outputs = cell.get('outputs', [])
                if outputs:
                    out_f.write("Outputs:\n")
                    for out_idx, out in enumerate(outputs):
                        output_type = out.get('output_type', '')
                        out_f.write(f"  [{out_idx}] Type: {output_type}\n")
                        if output_type == 'stream':
                            out_f.write("".join(out.get('text', [])))
                        elif output_type in ['execute_result', 'display_data']:
                            data = out.get('data', {})
                            if 'text/plain' in data:
                                out_f.write("".join(data['text/plain']))
                                out_f.write("\n")
                            if any(mime.startswith('image/') for mime in data):
                                out_f.write(f"[IMAGE OUTPUT: {', '.join(mime for mime in data if mime.startswith('image/'))}]\n")
                        elif output_type == 'error':
                            out_f.write("  ERROR:\n")
                            out_f.write("\n".join(out.get('traceback', [])))
                            out_f.write("\n")
                out_f.write("\n" + "="*80 + "\n\n")

print(f"Extracted stats saved to {output_path}")
