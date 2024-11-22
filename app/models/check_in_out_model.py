from datetime import datetime

from prisma.enums import ActionType
from pydantic import BaseModel


class CheckInOutLogResponse(BaseModel):
    log_id: int
    check_time: datetime
    action: ActionType