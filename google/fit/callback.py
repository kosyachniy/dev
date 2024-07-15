from fastapi import APIRouter
from fastapi.responses import RedirectResponse


from lib import cfg, report
from lib.queue import save
from lib.fit import Fit
from models.user import Customer


router = APIRouter()


@router.get("/callback/")
async def handler(
    state: int,
    code: str,
    # scope: str = None,
):
    try:
        creds = Fit().get_creds(code)
    except Exception as e:
        await report.error("Callback", {"social_id": state, "code": code}, error=e)
        return

    users = Customer.get(social_id=state)
    if not users:
        user = Customer(social_id=state)
        user.save()
    else:
        user = users[0]

    user.creds = creds
    user.save()
    save(f"gfit{state}", creds, 3600)

    return RedirectResponse(f"https://t.me/{cfg('tg.bot')}/app")
