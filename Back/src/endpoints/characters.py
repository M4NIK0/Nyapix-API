import fastapi
router = fastapi.APIRouter()
import models.content as models
from db_management.connection import connect_db
import db_management.characters as characters_db
from utility.logging import logger
import decorators.users_type as users_type

@router.get("/search", tags=["Characters management"])
async def search_characters_endpoint(request: fastapi.Request, character_name: str = fastapi.Query(...), max_results: int = fastapi.Query(10)) -> models.CharacterPageModel:
    db = None
    try:
        db = connect_db()
        character_name = character_name.strip().lower().replace(" ", "_")
        characters = characters_db.search_characters(db, character_name, max_results)
        return characters
    except Exception as e:
        logger.error("Error searching characters")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("", tags=["Characters management"])
async def get_characters_endpoint(request: fastapi.Request, page: int = fastapi.Query(1), size: int = fastapi.Query(10)) -> models.CharacterPageModel:
    db = None
    try:
        db = connect_db()
        characters = characters_db.get_characters_page(db, page, size)
        return characters
    except Exception as e:
        logger.error("Error getting characters")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/{character_id}", tags=["Characters management"])
async def get_character_endpoint(request: fastapi.Request, character_id: int) -> models.CharacterModel:
    db = None
    try:
        db = connect_db()
        character = characters_db.get_character(db, character_id)
        if character is None:
            return fastapi.responses.Response(status_code=404)
        return character
    except Exception as e:
        logger.error("Error getting character")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.post("", tags=["Characters management"])
@users_type.admin_required
async def post_characters_endpoint(request: fastapi.Request, character_name: str = fastapi.Query(...)):
    db = None
    try:
        db = connect_db()
        character_name = character_name.strip().lower().replace(" ", "_")
        success = characters_db.add_character(db, character_name, request.state.user.id)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error adding character")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.put("/{character_id}", tags=["Characters management"])
@users_type.admin_required
async def put_characters_endpoint(request: fastapi.Request, character_id: int, character_name: str = fastapi.Query(...)):
    db = None
    try:
        db = connect_db()
        character_name = character_name.strip().lower().replace(" ", "_")
        success = characters_db.edit_character(db, character_id, character_name)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error updating character")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.delete("/{character_id}", tags=["Characters management"])
@users_type.admin_required
async def delete_characters_endpoint(request: fastapi.Request, character_id: int):
    db = None
    try:
        db = connect_db()
        success = characters_db.delete_character(db, character_id)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error deleting character")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/{character_name}", tags=["Characters management"])
async def get_character_by_name_endpoint(request: fastapi.Request, character_name: str):
    db = None
    try:
        db = connect_db()
        character = characters_db.get_character_by_name(db, character_name)
        if character is None:
            return fastapi.responses.Response(status_code=404)
        return character
    except Exception as e:
        logger.error("Error getting character")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()
