import fastapi

from app.database.auth_schemas import LoginRequest, LoginSuccess
from app.database.schemas import MessageResponse
from app.services.authentication_service import AuthenticationService
from app.database.database import get_db

router = fastapi.APIRouter()


@router.post("/login")
async def login(
    login_request: LoginRequest, response: fastapi.Response, db=fastapi.Depends(get_db)
):
    result: LoginSuccess = await AuthenticationService.authenticate(
        db, login_request.email, login_request.password
    )
    if isinstance(result, MessageResponse):
        raise fastapi.HTTPException(status_code=401, detail=result.message)

    if not result.user.is_active:
        raise fastapi.HTTPException(
            status_code=401,
            detail="User is inactive. Please contact the administrator.",
        )

    response.set_cookie("token", result.access_token, httponly=True)
    return result


@router.post("/logout")
async def logout(response: fastapi.Response):
    response.delete_cookie("token")
    return response
