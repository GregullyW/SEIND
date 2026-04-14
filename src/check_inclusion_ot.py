import unicodedata

def normalize_string(s):
    if not isinstance(s, str):
        return s
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s

def build_domain(df, column):
    return set(
        df[column]
        .dropna()
        .astype(str)
        .map(normalize_string)
    )


def build_all_domains(tables):
    domains = {}

    for table_name, df in tables.items():
        for col in df.columns:
            domains[(table_name, col)] = set(
                df[col]
                .dropna()
                .astype(str)
                .map(normalize_string)
                .unique()
            )

    return domains

def check_epsilon_ind(lhs_domain, rhs_domain, epsilon=0.01, return_stats=False):

    if len(lhs_domain) == 0:
        return False if not return_stats else (False, 1.0, 0, [])

    violations = [v for v in lhs_domain if v not in rhs_domain]

    violation_ratio = len(violations) / len(lhs_domain)

    is_ind = violation_ratio <= epsilon

    if return_stats:
        return is_ind, violation_ratio, len(violations), violations

    return is_ind

def valid_INDs(tables, candidates, epsilon):

    valid_inds = []

    domains = build_all_domains(tables) 

    for p in candidates:

        lhs_table, lhs_col = p["lhs"].split(".")
        rhs_table, rhs_col = p["rhs"].split(".")

        lhs_domain = domains[(lhs_table, lhs_col)]
        rhs_domain = domains[(rhs_table, rhs_col)]

        is_ind, ratio, n_viol, viols = check_epsilon_ind(
            lhs_domain,
            rhs_domain,
            epsilon=epsilon,
            return_stats=True
        )

        if is_ind:
            valid_inds.append({
                **p,
                "epsilon": epsilon,
                "violation_ratio": ratio,
                "violations": viols[:10]
            })

    return valid_inds