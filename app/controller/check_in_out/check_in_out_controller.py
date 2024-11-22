from prisma.enums import ActionType

from common.database import db


async def check_in_out_user(user_id: int):
    last_record = await db.checkinoutlogs.find_first(
        where={
            'user_id' : user_id
        },
        order={
            'check_time': 'desc'
        }
    )

    action = ActionType.CHECK_IN

    if last_record is not None and last_record.action == ActionType.CHECK_IN:
        action = ActionType.CHECK_OUT

    record = await db.checkinoutlogs.create(
        data={
            'user_id': user_id,
            'action': action,
        }
    )

    return record

async def get_all_check_in_out_logs():
    return await db.checkinoutlogs.find_many(
        order={
            'check_time': 'desc'
        },
        include={
            'user': True
        }
    )

async def get_log_by_user_id(user_id: int):
    return await db.checkinoutlogs.find_many(
        where={
            'user_id': user_id
        },
        
        order={
            'check_time': 'desc'
        },
    )
