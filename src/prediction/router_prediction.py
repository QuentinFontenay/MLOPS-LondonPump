from fastapi import Depends, HTTPException, APIRouter
from auth.schemas import User
from auth.service import get_current_user, get_current_admin

router = APIRouter()
