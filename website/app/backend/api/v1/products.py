"""
Products API endpoints.
"""
from fastapi import APIRouter, Depends
from typing import List, Dict, Any

from database.connection import get_db

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_products(db=Depends(get_db)):
    """
    Get a list of fashion products.
    """
    from sqlalchemy import text
    query = text("SELECT * FROM fashion_system LIMIT 24;")
    
    # We execute a raw SQL query
    result = await db.execute(query)
    products = []
    
    # The result from asyncpg execute is likely a list of records
    for row in result:
        row_dict = dict(row._mapping)
        item_id = row_dict.get("item_id")
        image_path = row_dict.get("image_path")
        
        # Build the final product dictionary expected by frontend
        product = {
            "id": str(item_id),
            "name": f"{row_dict.get('brand', 'IndoCloth')} {row_dict.get('category', 'Fashion Item')}".strip(),
            "price": float(row_dict.get("price", 0.0) if row_dict.get("price") is not None else 0.0),
            "image": f"http://localhost:8000/images/{image_path}" if image_path else "/api/placeholder/300/400"
        }
            
        products.append(product)
        
    return products
