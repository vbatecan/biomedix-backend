import fastapi

from app.database.auth_schemas import LoginRequest
from app.database.schemas import MessageResponse
from app.services.authentication_service import AuthenticationService
from app.database.database import get_db

router = fastapi.APIRouter()


@router.post("/login")
async def login(login_request: LoginRequest, response: fastapi.Response, db=fastapi.Depends(get_db)):
    result = await AuthenticationService.authenticate(db, login_request.email, login_request.password)
    if type(result) == MessageResponse:
        return result
    response.set_cookie("token", result.access_token, httponly=True)
    return result


@router.post("/logout")
async def logout(response: fastapi.Response):
    response.delete_cookie("token")
    return response
