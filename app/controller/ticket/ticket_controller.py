import calendar
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from prisma.models import Tickets

from common.database import db

async def find_ticket_from_user(user_id: int):
    user = await db.users.find_unique(
        where={
            'user_id': user_id,
        },
        include={
            'ticket': True,
        }
    )

    return user.ticket

async def create_ticket(user_id: int):
    ticket = await find_ticket_from_user(user_id)

    if ticket:
        raise HTTPException(status_code=409, detail='Người dùng đã có vé.')

    await db.tickets.create(
        data={
            'user_id': user_id,
        }
    )

    return True

async def renew_ticket(user_id: int, start_month: datetime, end_month: Optional[datetime] = None):
    ticket = await find_ticket_from_user(user_id)

    start_date = start_month.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )

    if end_month is None:
        end_month = start_month

    last_day_of_month = calendar.monthrange(end_month.year, end_month.month)[1]

    end_date = end_month.replace(
        day=last_day_of_month, hour=23, minute=59, second=59, microsecond=999999
    )

    await db.tickets.update(
        where={
            'ticket_id': ticket.ticket_id,
        },
        data={
            'start_date': start_date,
            'end_date': end_date,
        }
    )

    return True

async def check_ticker(ticket: Tickets):
    now = datetime.now()

    if ticket.end_date < now:
        return False

    return True