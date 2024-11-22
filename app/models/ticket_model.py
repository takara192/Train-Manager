from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RenewTicketRequest(BaseModel):
    start_month: datetime
    end_month: Optional[datetime] = None