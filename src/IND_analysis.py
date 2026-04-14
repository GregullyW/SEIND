import csv
import json
import re
from pathlib import Path
import glob
import os



def normalize_name(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip()
    s = re.sub(r'\.csv$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+', ' ', s)
    return s.lower().strip()


def evaluate_json_ind(arq, label, output):
    gt_path = Path(f"{label}")
    ground_truth_norm = set()

    with gt_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lhs_norm = normalize_name(row.get("LHS", ""))
            rhs_norm = normalize_name(row.get("RHS", ""))
            ground_truth_norm.add((lhs_norm, rhs_norm))

    res_path = Path(f"{arq}")

    discovered_norm = set()

    with res_path.open("r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue

            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if obj.get("type") != "InclusionDependency":
                continue

            dep = obj.get("dependant", {}).get("columnIdentifiers", [])
            ref = obj.get("referenced", {}).get("columnIdentifiers", [])

            if not dep or not ref:
                continue

            d = dep[0]
            r = ref[0]

            lhs_orig = f"{d['tableIdentifier'].replace('.csv','')}.{d['columnIdentifier']}"
            rhs_orig = f"{r['tableIdentifier'].replace('.csv','')}.{r['columnIdentifier']}"

            lhs_norm = normalize_name(lhs_orig)
            rhs_norm = normalize_name(rhs_orig)

            discovered_norm.add((lhs_norm, rhs_norm))

    tp_norm = discovered_norm & ground_truth_norm
    fp_norm = discovered_norm - ground_truth_norm
    fn_norm = ground_truth_norm - discovered_norm

    tp = len(tp_norm)
    fp = len(fp_norm)
    fn = len(fn_norm)

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall    = tp / (tp + fn) if (tp + fn) else 0
    f1        = 2*precision*recall / (precision+recall) if (precision+recall) else 0

    out_csv = Path(f"{output}")
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Fonte", "LHS", "RHS", "Status"])

        for lhs, rhs in ground_truth_norm:
            status = "TP" if (lhs, rhs) in discovered_norm else "FN"
            writer.writerow(["GroundTruth", lhs, rhs, status])

        for lhs, rhs in discovered_norm:
            status = "TP" if (lhs, rhs) in ground_truth_norm else "FP"
            writer.writerow(["Metanome", lhs, rhs, status])

        writer.writerow([])
        writer.writerow(["TP", "FP", "FN", "Precision", "Recall", "F1"])
        writer.writerow([tp, fp, fn, f"{precision:.2f}", f"{recall:.2f}", f"{f1:.2f}"])

    print(f"Arquivo salvo em: {out_csv}")
    print(f"TP={tp}, FP={fp}, FN={fn}, Precision={precision:.3f}, Recall={recall:.3f}, F1={f1:.3f}")



def evaluate_ind(input_dir, output_dir, label_file):
    os.makedirs(output_dir, exist_ok=True)

    all_files = glob.glob(os.path.join(input_dir, "*.txt"))

    txt_files = [f for f in all_files if not os.path.basename(f).endswith("_log.txt")]

    for txt_file in txt_files:
        base_name = os.path.splitext(os.path.basename(txt_file))[0]
        output_csv = os.path.join(output_dir, f"{base_name}.csv")
        
        evaluate_json_ind(arq=txt_file, label=label_file, output=output_csv)
        
        print(f"Processado: {txt_file} -> {output_csv}")

    