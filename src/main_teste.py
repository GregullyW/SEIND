import filter_embedding
import check_inclusion_ot_relat
import load_csv
import export_ind
import IND_analysis
import time
import numpy as np

inicio = time.perf_counter()
tables = load_csv.load_tables("../data/COMERCY_corrigido/")

dataset_name = "COMERCY_corrigido_novo_11_04"
num_tables = 2 #config para o numero de tabelas, 1 para uma, qualquer coisa para mais
columns_data = filter_embedding.extract_columns(tables, dataset_name)
pairs = filter_embedding.instance_model(columns_data, num_tables)

alpha = 0.70
filter_pairs = filter_embedding.filter_pairs(pairs, alpha)
candidates = filter_embedding.filter_candidates(filter_pairs)

epsilon = 0.15
valid_inds = check_inclusion_ot_relat.valid_INDs(tables, candidates, epsilon)

export_ind.export_inds_txt(valid_inds, f"../results/{dataset_name}/COMERCY_corrigido_novo_11_04aa_relatorio.txt")

input_dir = f"../results/{dataset_name}"
output_dir = f"../IND_analysis_result/{dataset_name}"
label_file = "../data/GT/COMERCY_GT_corrigido.csv"
IND_analysis.evaluate_ind(input_dir, output_dir, label_file)
fim = time.perf_counter()
print(f"Tempo: {fim - inicio:.6f} segundos")