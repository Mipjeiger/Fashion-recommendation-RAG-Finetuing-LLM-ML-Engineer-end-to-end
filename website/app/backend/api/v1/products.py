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
    Get a list of fashion products from fashion_recommendation table.
    """
    from sqlalchemy import text
    query = text("SELECT * FROM fashion_recommendation LIMIT 100;")
    
    # We execute a raw SQL query
    result = await db.execute(query)
    products = []
    
    for row in result:
        row_dict = dict(row._mapping)
        item_id = row_dict.get("item_id")
        raw_image_path = row_dict.get("image_path", "")
        
        # Normalize image_path: DB stores paths like "../../../fashion_images/dataset_clean/men_cargos/img_0969.jpg"
        # We need just the part after "dataset_clean/" since /images is mounted at that directory
        image_path = ""
        if raw_image_path:
            marker = "dataset_clean/"
            idx = raw_image_path.find(marker)
            if idx != -1:
                image_path = raw_image_path[idx + len(marker):]
            else:
                # Fallback: use as-is if it doesn't contain the marker
                image_path = raw_image_path
        
        # Derive a readable category name from image_path (e.g. "casual_shirts/img_001.jpg" -> "Casual Shirts")
        category_name = "Fashion Item"
        if image_path and "/" in image_path:
            raw_category = image_path.split("/")[0]
            category_name = raw_category.replace("_", " ").title()
        
        # Build the final product dictionary expected by frontend
        product = {
            "id": str(item_id),
            "name": f"IndoCloth {category_name}".strip(),
            "price": float(row_dict.get("price", 0) if row_dict.get("price") is not None else 0),
            "image": f"/images/{image_path}" if image_path else "/api/placeholder/300/400",
            "sales": int(row_dict.get("sales", 0) if row_dict.get("sales") is not None else 0),
            "profit_status": row_dict.get("profit_status", "unknown"),
            "conversion_rate": float(row_dict.get("conversion_rate", 0) if row_dict.get("conversion_rate") is not None else 0),
            "stocks": int(row_dict.get("stocks", 0) if row_dict.get("stocks") is not None else 0),
            "view_count": int(row_dict.get("view_count", 0) if row_dict.get("view_count") is not None else 0),
            "purchase_count": int(row_dict.get("purchase_count", 0) if row_dict.get("purchase_count") is not None else 0),
        }
            
        products.append(product)
        
    return products
