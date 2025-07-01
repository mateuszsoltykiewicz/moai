from fastapi import APIRouter, Depends, Request
from Library.api.security import require_jwt_and_rbac
from Library.logging import get_logger
from .manager import BankManager
from .schemas import TransactionRequest, TransactionResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/bank", tags=["bank"])

@router.post("/transaction", response_model=TransactionResponse, dependencies=[Depends(lambda request: require_jwt_and_rbac(request, "bank", "write"))])
async def process_transaction(request: Request, req: TransactionRequest):
    try:
        result = await BankManager.process_transaction(req)
        return result
    except Exception as e:
        logger.error(f"Transaction failed: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")
