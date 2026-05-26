from pydantic import BaseModel
from typing import List, Optional

class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None

class InvoiceData(BaseModel):
    document_type: str
    vendor_name: str
    invoice_number: str
    invoice_date: str
    total_amount: float
    confidence_score: float
    line_items: List[LineItem]