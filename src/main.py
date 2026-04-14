import os
import time
import argparse

import load_csv
import export_ind
import IND_analysis
import load_csv_parallel
import filter_embedding
import check_inclusion_ot_relat

def main(args):
    start = time.perf_counter()

    dataset_name = args.dataset_name

    n_files = len([f for f in os.listdir(args.data_path) if f.endswith(".csv")])

    if n_files > 1:
        tables = load_csv_parallel.load_tables_parallel(args.data_path)
    else:
        tables = load_csv.load_tables(args.data_path)

    coluns_data = filter_embedding.extract_columns(tables, dataset_name)
    pairs = filter_embedding.instance_model(coluns_data, n_files)

    filter_pairs = filter_embedding.filter_pairs(pairs, args.alpha)
    candidates = filter_embedding.filter_candidates(filter_pairs)

    valid_inds = check_inclusion_ot_relat.valid_INDs(tables, candidates, args.epsilon, save_path=f"../relat/relat_{dataset_name}_{start}.csv")

    os.makedirs(f"../results/{dataset_name}", exist_ok=True)

    output_file = f"../results/{dataset_name}/ind_result_{dataset_name}_{start}.txt"

    export_ind.export_inds_txt(valid_inds, output_file)

    if args.run_eval:
        IND_analysis.evaluate_ind(
            f"../results/{dataset_name}",
            f"../IND_analysis_result/{dataset_name}",
            args.label_file
        )

    end = time.perf_counter()
    print(f"Time: {end - start:.2f} s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline")

    parser.add_argument("--data_path", type=str, required=True, help="Path of csv folder")

    parser.add_argument("--dataset_name", type=str, default="dataset")

    parser.add_argument("--label_file", type=str, default=None, help="Ground Truth of dataset")

    parser.add_argument("--alpha", type=float, default=0.7, help="Threshold of similarity")

    parser.add_argument("--epsilon", type=float, default=0.15, help="Threshold of inclusion")
    
    parser.add_argument("--run_eval", action="store_true", help="Perform assessment using ground truth.")

    args = parser.parse_args()

    main(args)