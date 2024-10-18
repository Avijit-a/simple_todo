from fastapi import APIRouter

router = APIRouter()


@router.get("/api/autoroute")
async def sample():
    return {'message': 'Routes Working'}
