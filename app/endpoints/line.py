from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from ..db.supabase import SupabaseClient
from ..schemas.line import Line, LineFilter

router = APIRouter(prefix="/quotes", tags=["quotes"])

db = SupabaseClient().get_client()

@router.get("/search/", response_model=List[Line])
async def get_quotes(
    quote: str = Query(..., min_length=3, 
                        description="Search term for the quote",
                       example="everything's cool in Dobby Club.")
    ) -> List[Line]:
    
    sanitised_quote = quote.strip()
    
    query = db.table("line").select(
        "line_content, spoken_by, spoken_to, line_number, \
            script(series, episode), location(name), meme_metadata(file_name, file_type, file_url)"
    )
    
    query = query.ilike("line_content", f"%{sanitised_quote}%")
    
    response = query.execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    return [
        Line(**line) for line in response.data
    ]
    
    
@router.get("/filter/", response_model=List[LineFilter])
async def get_quotes(
    spoken_by: Optional[str] = Query(None, 
                                    description="Character who spoke the quote",
                                    example="Mark"),
    spoken_to: Optional[str] = Query(None,
                                    description="Character who the quote was spoken to",
                                    example="Jeremy"),
    ) -> List[LineFilter]:

    query = db.table("line").select(
        "line_content, spoken_by, spoken_to, line_number"
        )
    
    if spoken_by:
        spoken_by = spoken_by.capitalize()
        query = query.ilike("spoken_by", spoken_by)
    if spoken_to:
        spoken_to = spoken_to.capitalize()
        query = query.ilike("spoken_to", spoken_to)
        
    response = query.execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    return [
        LineFilter(**line) for line in response.data
    ]
    

@router.get("/random/", response_model=LineFilter)
async def get_quotes() -> LineFilter:

    import random

    query = db.table("line").select(
        "line_content, spoken_by, spoken_to, line_number"
        )
        
    response = query.execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Quote not found")

    return LineFilter(**random.choice(response.data))
    
    