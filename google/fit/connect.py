from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from lib import report
from lib.fit import Fit


router = APIRouter()


@router.get("/connect/")
async def handler(
    social_id: int,
):
    try:
        url = Fit().oauth(social_id)
    except Exception as e:
        await report.error("Connect", {"social_id": social_id}, error=e)
        return

    return RedirectResponse(url=url)
