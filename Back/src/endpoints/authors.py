import fastapi
import models.content as models
import db_management.authors as authors_db
from utility.logging import logger
from db_management.connection import connect_db
import decorators.users_type as users_type

router = fastapi.APIRouter()

@router.get("/search", tags=["Authors management"])
async def search_authors_endpoint(request: fastapi.Request, author_name: str = fastapi.Query(...), max_results: int = fastapi.Query(10)) -> models.AuthorPageModel:
    db = None
    try:
        db = connect_db()
        author_name = author_name.strip().lower().replace(" ", "_")
        authors = authors_db.search_authors(db, author_name, max_results)
        return authors
    except Exception as e:
        logger.error("Error searching authors")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("", tags=["Authors management"])
async def get_authors_endpoint(request: fastapi.Request, page: int = fastapi.Query(1), size: int = fastapi.Query(10)) -> models.AuthorPageModel:
    db = None
    try:
        db = connect_db()
        authors = authors_db.get_authors_page(db, page, size)
        return authors
    except Exception as e:
        logger.error("Error getting authors")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/{author_id}", tags=["Authors management"])
async def get_author_endpoint(request: fastapi.Request, author_id: int) -> models.AuthorModel:
    db = None
    try:
        db = connect_db()
        author = authors_db.get_author(db, author_id)
        if author is None:
            return fastapi.responses.Response(status_code=404)
        return author
    except Exception as e:
        logger.error("Error getting author")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.post("", tags=["Authors management"])
@users_type.admin_required
async def post_authors_endpoint(request: fastapi.Request, author_name: str = fastapi.Query(...)):
    db = None
    try:
        db = connect_db()
        success = authors_db.add_author(db, author_name, request.state.user.id)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error adding author")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.put("/{author_id}", tags=["Authors management"])
@users_type.admin_required
async def put_authors_endpoint(request: fastapi.Request, author_id: int, author_name: str = fastapi.Query(...)):
    db = None
    try:
        db = connect_db()
        success = authors_db.edit_author(db, author_id, author_name)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error updating author")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.delete("/{author_id}", tags=["Authors management"])
@users_type.admin_required
async def delete_authors_endpoint(request: fastapi.Request, author_id: int):
    db = None
    try:
        db = connect_db()
        success = authors_db.delete_author(db, author_id)
        if not success:
            return fastapi.responses.Response(status_code=409)
        return fastapi.responses.Response(status_code=200)
    except Exception as e:
        logger.error("Error deleting author")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()

@router.get("/{author_name}", tags=["Authors management"])
async def get_author_by_name_endpoint(request: fastapi.Request, author_name: str):
    db = None
    try:
        db = connect_db()
        author = authors_db.get_author_by_name(db, author_name)
        if author is None:
            return fastapi.responses.Response(status_code=404)
        return author
    except Exception as e:
        logger.error("Error getting author")
        logger.error(e)
        return fastapi.responses.Response(status_code=500)
    finally:
        if db is not None:
            db.close()
