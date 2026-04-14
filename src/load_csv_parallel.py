import os
import utils
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_single_table(entry):
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]

    path = entry.path
    fname = entry.name

    sep = utils.detect_separator(path)

    df = None
    encoding_used = None

    for enc in encodings:
        try:
            df = pd.read_csv(
                path,
                encoding=enc,
                sep=sep,
                low_memory=False,
                on_bad_lines="skip",
                dtype=str
            )
            encoding_used = enc
            break
        except Exception:
            continue

    if df is None:
        print(f"Falha ao carregar {fname}")
        return None

    df.columns = [utils.normalize_text(c) for c in df.columns]

    print(f"Carregado {fname}: {df.shape} | encoding={encoding_used} | sep='{sep}'")

    return fname.replace(".csv", ""), df

def load_tables_parallel(base_dir, max_workers=8):
    tables = {}

    entries = [e for e in os.scandir(base_dir) if e.name.endswith(".csv")]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(load_single_table, e) for e in entries]

        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                key, df = result
                tables[key] = df

    return tables