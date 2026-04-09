import pandas as pd
import numpy as np

def apply_remediation(df, rules):
    """
    Applies remediation rules to a dataframe.
    rules: dict like {"global": "drop_duplicates", "columns": {"Age": "impute_mean", "Income": "clip_outliers"}}
    """
    initial_rows = len(df)
    impact_columns = {}
    
    initial_state = {}
    for col in df.columns:
        initial_state[col] = {
            "missing": int(df[col].isnull().sum() + (df[col] == "").sum() if pd.api.types.is_object_dtype(df[col]) else df[col].isnull().sum()),
            "unique": int(df[col].nunique())
        }
    
    if rules.get("global") == "drop_duplicates":
        df = df.drop_duplicates()
    elif rules.get("global") == "drop_near_duplicates":
        cols_to_check = [col for col in df.columns if df[col].nunique() < initial_rows]
        if cols_to_check:
            df = df.drop_duplicates(subset=cols_to_check)
            
    for col, strategy in rules.get("columns", {}).items():
        if col not in df.columns:
            continue
            
        if strategy == "none":
            continue
            
        applied_action = strategy
        
        if strategy == "drop_column" or strategy == "drop_constant_column":
            df = df.drop(columns=[col])
            
        elif strategy == "drop_rows":
            if pd.api.types.is_object_dtype(df[col]):
                df = df.replace({col: {"": np.nan}}).dropna(subset=[col])
            else:
                df = df.dropna(subset=[col])
            
        elif strategy == "impute_mean":
            mean_val = df[col].mean()
            df[col] = df[col].fillna(mean_val)
            
        elif strategy == "impute_median":
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            
        elif strategy == "impute_mode":
            mode_val = df[col].mode()[0] if not df[col].mode().empty else np.nan
            if pd.api.types.is_object_dtype(df[col]):
                df[col] = df[col].replace("", np.nan).fillna(mode_val)
            else:
                df[col] = df[col].fillna(mode_val)
            
        elif strategy == "clip_outliers":
            if pd.api.types.is_numeric_dtype(df[col]):
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                
        elif strategy == "standardize_text":
            if pd.api.types.is_object_dtype(df[col]):
                df[col] = df[col].astype(str).str.strip().str.title()
                df[col] = df[col].replace(['Nan', 'None', ''], np.nan)
                
        if col in df.columns:
            final_missing = int(df[col].isnull().sum() + (df[col] == "").sum() if pd.api.types.is_object_dtype(df[col]) else df[col].isnull().sum())
            missing_reduced = initial_state[col]["missing"] - final_missing
            
            impact_columns[col] = {
                "action_taken": strategy.replace("_", " ").title(),
                "missing_resolved": missing_reduced if missing_reduced > 0 else 0
            }
            if strategy == "standardize_text":
                impact_columns[col]["text_standardized"] = True
        else:
             impact_columns[col] = {
                "action_taken": "Dropped Column",
                "missing_resolved": initial_state[col]["missing"]
            }
                
    final_rows = len(df)
    
    impact = {
        "rows_dropped": initial_rows - final_rows,
        "retention_rate": round(final_rows / initial_rows * 100, 2) if initial_rows > 0 else 0,
        "columns_impact": impact_columns
    }
    
    return df, impact
