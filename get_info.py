import re
from utils import transaction_mapper


def get_customer_name(text):
    start = text.find("Customer Name")
    length = text[start:].find("\n")
    line = text[start : start + length]
    return line.split(":")[1]


def get_transactions(text):
    start = text.find("Receipt")
    start += text[start:].find("\n") + 1
    section = text[start:]
    pattern = r"(?=\bS[A-Z][A-Z0-9]{8}\b)"
    chunks = re.split(pattern, section)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    transactions = []
    for chunk in chunks:
        transaction = {}
        transaction["Transaction code"] = chunk[:10]
        transaction["Date"] = chunk[10:30].strip()
        info = chunk[30:].split("Completed ")
        mid = info[0].find(" -")

        if mid != -1:
            description = info[0].split(" -")
            transaction["Type"], transaction["Direction"] = transaction_mapper(
                description[0].strip().replace("\n", "")
            )
            transaction["Party"] = description[1].strip().replace("\n", "")
        if mid == -1:
            transaction["Type"] = transaction_mapper(info[0].strip())
            transaction["Party"] = "Safaricom"

        amounts = info[1].split(" ")
        transaction["Amount"] = amounts[0]
        transaction["Balance"] = amounts[1]

        transactions.append(transaction)
    return transactions
