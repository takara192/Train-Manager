from typing import List
from fastapi import APIRouter, UploadFile
from prisma.enums import ActionType
from controller.ticket.ticket_controller import find_ticket_from_user, check_ticker
from controller.user.user_controller import recognize_user
from controller.check_in_out.check_in_out_controller import check_in_out_user, get_all_check_in_out_logs, \
    get_log_by_user_id
from models.check_in_out_model import CheckInOutLogResponse

router = APIRouter(
    tags=['check_in_out'],
    prefix='/check_in_out',
)

@router.post('/')
async def check_in_out(file: UploadFile):
    user = await recognize_user(file)

    if user is None:
        return {
            'message': 'Không tìm thấy người dùng'
        }

    ticket = await find_ticket_from_user(user.user_id)

    if ticket is None:
        return {
            'message': f'Không tìm thấy vé cho người dùng {user.full_name}'
        }

    result = check_ticker(ticket)

    if not result:
        return {
            'message': 'Vé đã hết hạn'
        }

    record = await check_in_out_user(user.user_id)

    if record is None:
        return {
            'message': 'Cannot check in/out user'
        }

    return {
        'status': 'Thành công',
        'message': f' {user.full_name} {check_enum(record.action)} thành công',
        'timestamp' : record.check_time,
    }

@router.get('/get_all')
async def get_all_check_in_out():
    logs = await get_all_check_in_out_logs()

    if not logs:
        return {
            'message': 'Không có dữ liệu'
        }

    result = [
        {
            "user_id": log.user.user_id,
            "full_name": log.user.full_name,
            "log_id": log.log_id,
            "check_time": log.check_time,
            "action": log.action
        }

        for log in logs
    ]

    return result

@router.get('/get_logs_by_user_id/{user_id}', response_model=List[CheckInOutLogResponse])
async def get_user_logs(user_id: int):
    logs = await get_log_by_user_id(user_id)

    if not logs:
        return []



    return logs

def check_enum (action: ActionType):
    if action == ActionType.CHECK_IN:
        return 'check in'
    return 'check out'