from typing import Optional, List

from fastapi import APIRouter, UploadFile, Form, File, HTTPException

import controller.user.user_controller as controller
from controller.user.user_controller import search_user_by_full_name
from controller.ticket.ticket_controller import create_ticket
from models.user_model import RegisterUserModel, UpdateUserModel, SearchUserModel

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.post("/register")
async def register_new_user(
        full_name: str = Form(...),
        dob: str = Form(...),
        address: str = Form(...),
        phone_number: str = Form(...),
        face_image: UploadFile = File(...)
):
    user = await controller.register_user(
        full_name=full_name,
        dob=dob,
        address=address,
        phone_number=phone_number,
        file=face_image
    )

    if user:
        await create_ticket(user.user_id)
        return {"message": f"Đăng ký thành công cho người dùng: {full_name}"}
    else:
        return {"message": "Đăng ký không thành công"}


@router.post("/recognize")
async def recognize_user(face_image: UploadFile = File(...)):
    user = await controller.recognize_user(face_image)

    if user:
        return {"message": f"Nhận dạng thành công cho người dùng: {user.full_name}"}
    else:
        return {"message": "Không nhận dạng được người dùng"}


@router.put("/{user_id}")
async def update_user(user_id: int,
                      full_name: Optional[str] = Form(None),
                      dob: Optional[str] = Form(None),
                      address: Optional[str] = Form(None),
                      phone_number: Optional[str] = Form(None),
                      file: Optional[UploadFile] = None):

    result = await controller.update_user(user_id=user_id, full_name=full_name, dob=dob, address=address,
                                    phone_number=phone_number, file=file)

    if result:
        return {"message": f"Cập nhật thành công cho người dùng"}

@router.get("/search/{full_name}", response_model= List[SearchUserModel])
async def search_user(full_name: str):
    users = await search_user_by_full_name(full_name)
    if not users:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    return users

@router.get("/")
async def get_all_users():
    users = await controller.get_all_users()
    return users