import json
import os

def export_inds_txt(valid_inds, output_path):
    output_dir = os.path.dirname(output_path)
    if output_dir:  
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for ind in valid_inds:
            lhs_table, lhs_col = ind["lhs"].split(".")
            rhs_table, rhs_col = ind["rhs"].split(".")

            record = {
                "type": "InclusionDependency",
                "dependant": {
                    "columnIdentifiers": [
                        {
                            "tableIdentifier": f"{lhs_table}.csv",
                            "columnIdentifier": lhs_col
                        }
                    ]
                },
                "referenced": {
                    "columnIdentifiers": [
                        {
                            "tableIdentifier": f"{rhs_table}.csv",
                            "columnIdentifier": rhs_col
                        }
                    ]
                }
            }

            f.write(json.dumps(record, ensure_ascii=False))
            f.write("\n")