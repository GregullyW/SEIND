import faiss
import utils
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def sample_for_embedding(df, column, max_samples=50, seed=42):
    series = (
        df[column]
        .dropna()
        .astype(str)
        .map(str.strip)
        .replace("", None)
        .dropna()
        .map(utils.normalize_text) #normalização 
    )

    if series.empty:
        return []

    unique_vals = pd.Series(series.unique())

    n = min(max_samples, len(unique_vals))

    return (
        unique_vals
        .sample(n=n, random_state=seed)
        .tolist()
    )

def column_to_text(df, table_name, column, values):
    if not values:
        return ""

    values_series = pd.Series(list(values))

    numeric_mask = pd.to_numeric(values_series, errors="coerce").notna()
    is_numeric = numeric_mask.all()

    if is_numeric:
        description = "numeric identifiers"
        tokens = [f"{column}{v}" for v in values]
    else:
        description = "textual values"
        tokens = list(values)
        

    return (
        f"The column {column} "
        f"contains {description} "
        f"such as: " + " , ".join(tokens)
    )


def extract_columns(tables, dataset_name):
    columns = []

    for table_name, df in tables.items():
        for col in df.columns:
            try:
                embed_values = sample_for_embedding(df, col)
                if not embed_values:
                    continue

                text = column_to_text(
                    df,
                    table_name,
                    col,
                    embed_values
                )

                if not text:
                    continue

                columns.append({
                    "dataset": dataset_name,
                    "table": table_name,
                    "column": col,
                    "text": text,                 # embedding
                    "embed_values": embed_values, # embedding
                })

            except Exception as e:
                print(f"Erro {table_name}.{col}: {e}")

    return columns

def instance_model(columns_data, num_tables, k=20):
    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

    texts = [c["text"] for c in columns_data]
    embeddings = model.encode(texts, normalize_embeddings=True)

    emb = np.array(embeddings).astype("float32")

    dimension = emb.shape[1]

    # índice FAISS para similaridade de cosseno
    index = faiss.IndexFlatIP(dimension)
    index.add(emb)

    # busca dos k vizinhos mais próximos
    distances, indices = index.search(emb, k)

    pairs = []

    for i, neighbors in enumerate(indices):

        col_i = columns_data[i]

        for pos, j in enumerate(neighbors):

            if i == j:
                continue

            col_j = columns_data[j]

            if num_tables > 1:
                if col_i["table"] == col_j["table"]:
                    continue
            else:
                if col_i["column"] == col_j["column"]:
                    continue

            sim = distances[i][pos]

            pairs.append({
                "lhs_table": col_i["table"],
                "lhs_column": col_i["column"],
                "rhs_table": col_j["table"],
                "rhs_column": col_j["column"],
                "cosine": float(sim)
            })

    return pairs

def filter_pairs(pairs, alpha):
    filtered_pairs = [
        p for p in pairs if p["cosine"] >= alpha
    ]
    return filtered_pairs


def filter_candidates(filtered_pairs):
    candidates = []

    for p in filtered_pairs:
        candidates.append({
            "lhs": f"{p['lhs_table']}.{p['lhs_column']}",
            "rhs": f"{p['rhs_table']}.{p['rhs_column']}",
            "score": p["cosine"]
        })
    
    return candidates