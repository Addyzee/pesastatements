from fastapi import FastAPI, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from typing import Annotated

from app.data_writing.write_data import get_customer_name, write_transactions_data2
from app.document_handling.extract import extract_and_clean2
from app.document_handling.decrypt import remove_password_from_pdf2
from app.data.clean import clean_data2
from app.analysis.analysis import (
    transaction_type_analysis,
    transaction_accounts_analysis,
    time_analysis
)
from app.analysis.totals import total_cashflow


app = FastAPI()


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload/")
async def upload_statement(file: UploadFile):
    return {"filename": file.filename}


@app.post("/decrypt/")
async def decrypt_pdf(file: UploadFile, password: Annotated[str, Body()]):
    try:
        decrypted_file = remove_password_from_pdf2(file.file, password)
        text = extract_and_clean2(file=decrypted_file)
        customer_name = await get_customer_name(text=text)
        data = await write_transactions_data2(text)
        clean_data = clean_data2(data)
        analysis = await basic_analysis(data=clean_data)

        return {
            "the_pdf": file.filename,
            "the_name": customer_name,
            "analysis": analysis,
        }
    except Exception as e:
        raise e


async def basic_analysis(data: pd.DataFrame):
    try:
        total_amounts = total_cashflow(data)
        types_analysis = transaction_type_analysis(data)
        accounts_analysis = transaction_accounts_analysis(data)
        months_analysis = time_analysis(data)

        return {
            "total_cashflow": total_amounts,
            "transaction_type_analysis": types_analysis,
            "accounts_analysis": accounts_analysis,
            "months_analysis": months_analysis,
        }
    except Exception as e:
        raise e
