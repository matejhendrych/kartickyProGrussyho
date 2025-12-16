"""
Services router for FastAPI
Handles service endpoints like health checks
"""
from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "message": "All is well :)"}


@router.get("/401")
async def unauthorized():
    """Test 401 error"""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized"
    )


@router.get("/403")
async def forbidden():
    """Test 403 error"""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden"
    )


@router.get("/404")
async def not_found():
    """Test 404 error"""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not found"
    )


@router.get("/500")
async def internal_error():
    """Test 500 error"""
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal server error"
    )
