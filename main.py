from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import pandas as pd
import io
import os
import json
from analysis import assess_dataframe
from remediation import apply_remediation

app = FastAPI(title="Data Quality Assessment Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_data = {}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        file_id = "temp_dataset"
        session_data[file_id] = df.copy()
        
        assessment = assess_dataframe(df)
        
        return {
            "message": "File uploaded successfully",
            "file_id": file_id,
            "filename": file.filename,
            "rows": len(df),
            "columns": len(df.columns),
            "assessment": assessment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/remediate")
async def remediate(rules: str = Form(...), file_id: str = Form(...)):
    try:
        if file_id not in session_data:
             raise HTTPException(status_code=404, detail="File session not found.")
             
        df = session_data[file_id].copy()
        parsed_rules = json.loads(rules)
        
        cleaned_df, impact_metrics = apply_remediation(df, parsed_rules)
        
        session_data[file_id + "_cleaned"] = cleaned_df
        
        return {
            "message": "Remediation applied",
            "impact": impact_metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{file_id}")
async def download_file(file_id: str):
    if file_id not in session_data:
         raise HTTPException(status_code=404, detail="File session not found.")
    
    df = session_data[file_id]
    temp_path = f"temp_{file_id}.csv"
    df.to_csv(temp_path, index=False)
    
    return FileResponse(path=temp_path, filename=f"{file_id}.csv", media_type='text/csv')
