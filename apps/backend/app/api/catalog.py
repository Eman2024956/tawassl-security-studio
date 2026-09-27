from typing import List, Optional
from fastapi import APIRouter
from apps.backend.app.catalog.registry import get_all_test_modules, TestModuleMetadata

router = APIRouter(prefix="/api/catalog", tags=["Coverage Catalog"])


@router.get("", response_model=List[TestModuleMetadata])
async def list_catalog(category: Optional[str] = None):
    """Retrieve coverage catalog test modules, metadata, requirements, and implementation status."""
    modules = get_all_test_modules()
    if category:
        modules = [m for m in modules if m.category == category]
    return modules
