from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, FastAPI, File
from starlette.responses import JSONResponse

from app.core.config import Settings, logger
from app.crud import crud_detects
from falconpy import Detects

from app.utils import exception, logging, helper

router = APIRouter()

settings = Settings()

falcon = Detects(client_id=settings.CLIENT_ID, client_secret=settings.CLIENT_SECRET)


@router.get("/list-detections", response_model=List[Any])
def list_detections(search_filter: Optional[str] = None, limit: Optional[int] = 100) -> Any:
    if falcon.token_fail_reason:
        return JSONResponse(status_code=400, content=str(falcon.token_fail_reason))
    try:
        res = falcon.query_detects(filter=search_filter, limit=limit)
        if res["status_code"] == 200:
            items = res["body"]["resources"]
            if items:
                item_details = get_details(item_list=items)
                if isinstance(item_details, list):
                    JSONResponse(status_code=200, content=item_details)
                else:
                    errors = item_details["body"]["errors"]
                    for err in errors:
                        ecode = err["code"]
                        emsg = err["message"]
                        logger.error(ecode + ":" + emsg)
                    JSONResponse(status_code=200, content=errors)
    except Exception as e:
        return JSONResponse(status_code=400, content=str(e))


@router.get("/get-aggregate-detects", response_model=List[Any])
def get_aggregate_detects() -> Any:
    if falcon.token_fail_reason:
        return JSONResponse(status_code=400, content=str(falcon.token_fail_reason))
    try:
        date_range = {
            "from": "string",
            "to": "string"
        }
        search_range = {
            "From": int,
            "To": int
        }

        response = falcon.get_aggregate_detects(date_ranges=[date_range],
                                                field="string",
                                                filter="string",
                                                interval="string",
                                                min_doc_count=int,
                                                missing="string",
                                                name="string",
                                                q="string",
                                                ranges=[search_range],
                                                size=int,
                                                sort="string",
                                                time_zone="string",
                                                type="string"
                                                )
        if response["status_code"] == 200:
            JSONResponse(status_code=200, content=response["body"])
        else:
            errors = response["body"]["errors"]
            for err in errors:
                ecode = err["code"]
                emsg = err["message"]
                logger.error(ecode + ":" + emsg)
            JSONResponse(status_code=200, content=errors)
    except Exception as e:
        return JSONResponse(status_code=400, content=str(e))


def get_details(item_list: list) -> object:  # list or dict
    """Retrieve the details for the item list provided."""
    details = falcon.get_detect_summaries(ids=item_list)
    if details["status_code"] == 200:
        details = details["body"]["resources"]

    return details


@router.get("/get-detect-summary", response_model=List[Any])
def get_detect_summary(id_list: Optional[str] = None) -> Any:
    if falcon.token_fail_reason:
        return JSONResponse(status_code=400, content=str(falcon.token_fail_reason))
    try:
        res = falcon.get_detect_summaries(ids=id_list)
        if res["status_code"] == 200:
            items = res["body"]["resources"]
            if items:
                JSONResponse(status_code=200, content=items)
            else:
                errors = res["body"]["errors"]
                for err in errors:
                    ecode = err["code"]
                    emsg = err["message"]
                    logger.error(ecode + ":" + emsg)
                JSONResponse(status_code=200, content=errors)
    except Exception as e:
        return JSONResponse(status_code=400, content=str(e))


@router.get("/update-detects-by-ids", response_model=List[Any])
def update_detects_by_ids(id_list: str, status: str) -> Any:
    if falcon.token_fail_reason:
        return JSONResponse(status_code=400, content=str(falcon.token_fail_reason))
    try:
        filter_string = helper.create_id_filter(id_list)
        detail_lookup = falcon.query_detects(filter=filter_string)
        if detail_lookup["status_code"] == 200:
            upd = detail_lookup["body"]["resources"]
            update_result = falcon.update_detects_by_ids(ids=upd, status=status)
            if update_result["status_code"] == 200:
                stat_disp = helper.clean_status_string(status)
                for updated in id_list.split(","):
                    res_msg = f"Changed {updated} status to {stat_disp}."
                    print(res_msg)
                    JSONResponse(status_code=200, content=res_msg)
            else:
                errors = update_result["body"]["errors"]
                for err in errors:
                    ecode = err.get("code", 500)
                    emsg = err["message"]
                    res_msg = f"[{ecode}] {emsg}"
                    print(res_msg)
                    JSONResponse(status_code=200, content=res_msg)
    except Exception as e:
        return JSONResponse(status_code=400, content=str(e))
