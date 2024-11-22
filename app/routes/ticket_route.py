from fastapi import APIRouter
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from controller.ticket import ticket_controller as controller
from models.ticket_model import RenewTicketRequest

router = APIRouter(
    tags=['ticket'],
    prefix='/ticket',
)

@router.post("/{user_id}", status_code=HTTP_201_CREATED)
async def create_new_ticket(user_id: int):
    result = await controller.create_ticket(user_id)

    if result:
        return {"message": "Tạo vé thành công!"}

@router.get("/{user_id}")
async def read_ticket(user_id: int):
    ticket = await controller.find_ticket_from_user(user_id)

    if not ticket:
        return {
            "message": "Người dùng chưa có vé."
        }

    ticket_dict = ticket.dict()
    ticket_dict.pop("user", None)
    ticket_dict.pop("payments", None)

    return ticket_dict

@router.put("/{user_id}", status_code=HTTP_204_NO_CONTENT)
async def renew_ticket(user_id: int, renew_ticket_request: RenewTicketRequest):
    result = await controller.renew_ticket(user_id, renew_ticket_request.start_month, renew_ticket_request.end_month)

    if not result:
        return {
            "message": "Gia hạn thất bại."
        }