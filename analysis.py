import pandas as pd
import numpy as np

def detect_outliers_iqr(series):
    if not pd.api.types.is_numeric_dtype(series):
        return 0
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = series[(series < lower_bound) | (series > upper_bound)]
    return len(outliers)

def detect_text_inconsistencies(series):
    if not pd.api.types.is_object_dtype(series):
        return 0
    has_whitespace = series.astype(str).str.contains(r'^\s+|\s+$', regex=True, na=False)
    return int(has_whitespace.sum())

def suggest_remediation(missing_pct, has_outliers, dtype, unique_count, total_rows, text_issues):
    suggestions = []
    
    if unique_count == 1 and total_rows > 1:
        suggestions.append("drop_constant_column")
        
    if missing_pct > 0:
        if missing_pct > 50:
            suggestions.append("drop_column")
        elif pd.api.types.is_numeric_dtype(dtype):
            suggestions.append("impute_mean")
            suggestions.append("impute_median")
        else:
            suggestions.append("impute_mode")
            suggestions.append("drop_rows")
            
    if has_outliers > 0:
        suggestions.append("clip_outliers")
        
    if text_issues > 0:
        suggestions.append("standardize_text")
        
    if not suggestions:
        suggestions.append("none")
        
    return suggestions

def assess_dataframe(df):
    total_rows = len(df)
    duplicates = df.duplicated().sum()
    
    cols_to_check = [col for col in df.columns if df[col].nunique() < total_rows]
    near_duplicates = df.duplicated(subset=cols_to_check).sum() if cols_to_check else 0
    
    columns_report = {}
    
    for col in df.columns:
        series = df[col]
        missing_count = series.isnull().sum()
        
        if pd.api.types.is_object_dtype(series):
            missing_count += (series == "").sum()
            
        missing_pct = (missing_count / total_rows) * 100 if total_rows > 0 else 0
        
        outliers_count = detect_outliers_iqr(series) if pd.api.types.is_numeric_dtype(series) else 0
        text_issues = detect_text_inconsistencies(series)
        unique_count = int(series.nunique())
        
        dtype_str = str(series.dtype)
        
        suggestions = suggest_remediation(missing_pct, outliers_count, series.dtype, unique_count, total_rows, text_issues)
        
        columns_report[col] = {
            "type": dtype_str,
            "missing_count": int(missing_count),
            "missing_pct": round(missing_pct, 2),
            "unique_count": unique_count,
            "outliers_count": int(outliers_count),
            "text_inconsistencies": text_issues,
            "is_constant": (unique_count == 1 and total_rows > 1),
            "suggestions": suggestions
        }
        
    return {
        "global": {
            "total_rows": total_rows,
            "total_columns": len(df.columns),
            "duplicate_rows": int(duplicates),
            "near_duplicate_rows": int(near_duplicates)
        },
        "columns": columns_report
    }
