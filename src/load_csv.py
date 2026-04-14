import os
import utils
import pandas as pd

def load_tables(base_dir):

    tables = {}
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]

    for entry in os.scandir(base_dir):

        if not entry.name.endswith(".csv"):
            continue

        path = entry.path
        fname = entry.name

        path = os.path.join(base_dir, fname)

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
            continue

        df.columns = [utils.normalize_text(c) for c in df.columns]

        tables[fname.replace(".csv", "")] = df

        print(
            f"Carregado {fname}: {df.shape} | encoding={encoding_used} | sep='{sep}'"
        )

    return tables