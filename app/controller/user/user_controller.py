import base64
from copyreg import pickle
from datetime import datetime
import pickle
from typing import Optional

import cv2
import numpy as np
import face_recognition
from fastapi import UploadFile, HTTPException
from prisma import Base64
from pydantic import BaseModel

from common.database import db
from models.user_model import UpdateUserModel


async def register_user(full_name: str, dob: str, file: UploadFile, address: str, phone_number: str):
    try:
        dob_date = datetime.strptime(dob, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400,
                            detail="Định dạng ngày sinh không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD.")

    content = await file.read()

    try:
        image = np.frombuffer(content, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không thể giải mã ảnh: {str(e)}")

    if image is None:
        raise HTTPException(status_code=400, detail="File ảnh không hợp lệ hoặc không được hỗ trợ.")

    face_encodings = face_recognition.face_encodings(image)

    if len(face_encodings) == 0:
        raise HTTPException(status_code=400, detail="Không tìm thấy khuôn mặt trong ảnh.")

    face_encoding = face_encodings[0]
    face_encoding_bytes = face_encoding.tobytes()

    try:
        user = await db.users.create(
            data={
                "full_name": full_name,
                "dob": dob_date,
                "address": address,
                "phone_number": phone_number,
                "face_data": Base64.encode(face_encoding_bytes)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lưu người dùng: {str(e)}")

    return user

async def recognize_user(file: UploadFile):
    try:
        content = await file.read()

        try:
            image = np.frombuffer(content, np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Không thể giải mã ảnh: {str(e)}")

        if image is None:
            raise HTTPException(status_code=400, detail="File ảnh không hợp lệ hoặc không được hỗ trợ.")

        unknown_face_encodings = face_recognition.face_encodings(image)
        if len(unknown_face_encodings) == 0:
            raise HTTPException(status_code=400, detail="Không tìm thấy khuôn mặt trong ảnh.")

        unknown_face_encoding = unknown_face_encodings[0]

        users = await db.users.find_many(
            order={
                'created_at' : 'desc',
            }
        )

        for user in users:
            face_encoding_base64 = user.face_data

            try:
                face_encoding_bytes = Base64.decode(face_encoding_base64)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Lỗi khi giải mã base64 từ face_data: {str(e)}")

            try:
                face_encoding = np.frombuffer(face_encoding_bytes, dtype=np.float64)
            except ValueError as e:
                raise HTTPException(status_code=500,
                                    detail=f"Lỗi khi chuyển dữ liệu từ bytes sang numpy array: {str(e)}")

            match = face_recognition.compare_faces([face_encoding], unknown_face_encoding)
            if match[0]:
                return user

        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng khớp với khuôn mặt.")

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống không xác định: {str(e)}")

async def update_user(user_id: int, full_name: Optional[str] = None, dob: Optional[str]= None, address: Optional[str]= None, phone_number: Optional[str]= None, file: Optional[UploadFile]= None):
    user = db.users.find_first(
        where={
            'user_id': user_id
        }
    )


    if user is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")

    update_data = {}

    if full_name is not None:
        update_data["full_name"] = full_name

    if dob is not None:
        try:
            dob_date = datetime.strptime(dob, "%Y-%m-%d")
            update_data["dob"] = dob_date
        except ValueError:
            raise HTTPException(status_code=400,
                                detail="Định dạng ngày sinh không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD.")

    if address:
        update_data['address'] = address

    if phone_number:
        update_data['phone_number'] = phone_number

    if file is not None:
        content = await file.read()

        try:
            image = np.frombuffer(content, np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Không thể giải mã ảnh: {str(e)}")

        if image is None:
            raise HTTPException(status_code=400, detail="File ảnh không hợp lệ hoặc không được hỗ trợ.")

        face_encodings = face_recognition.face_encodings(image)

        if len(face_encodings) == 0:
            raise HTTPException(status_code=400, detail="Không tìm thấy khuôn mặt trong ảnh.")

        face_encoding = face_encodings[0]
        face_encoding_bytes = face_encoding.tobytes()

        update_data['face_data'] = Base64.encode(face_encoding_bytes)


    if update_data:
        await db.users.update(
            where={
                'user_id': user_id
            },
            data=update_data
        )
        return True

async def search_user_by_full_name(full_name: str):
    users = await db.users.find_many()

    matching_users = [
        user for user in users if full_name.lower() in user.full_name.lower()
    ]

    return matching_users

async def get_all_users():
    users = await db.users.find_many(

    )

    return users