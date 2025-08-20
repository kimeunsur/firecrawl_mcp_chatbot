from fastapi import APIRouter, Depends, HTTPException, status
from app.models.policy import Policy
from app.db.repositories.policy_repository import PolicyRepository
from app.api.dependencies import get_policy_repository

router = APIRouter()

@router.post("/create", response_model=Policy, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy: Policy,
    policy_repo: PolicyRepository = Depends(get_policy_repository),
):
    """
    새로운 정책을 생성하고 데이터베이스에 저장합니다.
    """
    try:
        inserted_id = await policy_repo.create_policy(policy)
        created_policy = await policy_repo.get_policy_by_id(inserted_id)
        if not created_policy:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="정책 생성 후 조회에 실패했습니다.",
            )
        return Policy(**created_policy)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"정책 생성 중 오류 발생: {e}",
        )
