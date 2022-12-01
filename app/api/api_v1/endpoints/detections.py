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
print(falcon.authenticated())


@router.get("/", response_model=List[Any], responses={200: {"model": List[Any]}, 400: {"model": exception.HTTPError}})
def list_detections(search_filter: Optional[str] = None, limit: Optional[int] = 10) -> Any:
    """
    List all detections. Results can be customized by passing a FQL filter.

    Filters can be provided using the -f argument, allowing you to reduce the number of results returned and filter down to just the records of interest to you.

    **Will not work** -> device.hostname:\\*\'*search-string\\*\'

    **Will work** -> "device.hostname:\\*\'*search-string\\*\'"
    """
    if falcon.token_fail_reason:
        print(str(falcon.token_fail_reason))
        raise HTTPException(status_code=400, detail=str(falcon.token_fail_reason))
    try:
        res = falcon.query_detects(filter=search_filter, limit=limit)
        if res["status_code"] == 200:
            items = res["body"]["resources"]
            if items:
                item_details = get_details(item_list=items)
                if isinstance(item_details, list):
                    return JSONResponse(status_code=200, content=item_details)
                else:
                    errors = item_details["body"]["errors"]
                    for err in errors:
                        ecode = err["code"]
                        emsg = err["message"]
                        logger.error(ecode + ":" + emsg)
                    return JSONResponse(status_code=200, content=errors)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{detection_id}", response_model=List[Any], responses={200: {"model": List[Any]}, 400: {"model": exception.HTTPError},
            404: {"model": exception.HTTPError}})
def get_detection_by_id(detection_id: str) -> Any:
    """
    Get detection by a single id. Multiple IDs can be specified by delimiting with comma (ID1,ID2,ID3).

    A maximum of 20 IDs may be specified in this manner.
    """
    if falcon.token_fail_reason:
        print(str(falcon.token_fail_reason))
        raise HTTPException(status_code=400, detail=str(falcon.token_fail_reason))
    try:
        filter_string = helper.create_id_filter(detection_id)
        res = falcon.query_detects(filter=filter_string)
        if res["status_code"] == 200:
            detailed = get_details(item_list=res["body"]["resources"])
            if not isinstance(detailed, list):
                return JSONResponse(status_code=404, content=str("Detection not found for the ID specified."))
            for detailer in detailed:
                result = helper.clean_result(detailer, extend=True)
                print(f"%-15s {result['id']}" % "Detection:")
                clr = result["status"]
                stat_disp = result["status"]
                print(f"%-15s {clr}{stat_disp}" % "Status:")
                aclr = ""
                if result['assigned'] != "Unassigned":
                    aclr = "Unassigned"
                print(f"%-15s {aclr}{result['assigned']}" % "Assigned to:")
                print(f"%-15s {result['hostname']}" % "Hostname:")
                print(f"%-15s {result['device_id']}" % "Agent ID:")
                print(f"%-15s {result['agent_version']}" % "Agent version:")
                print(f"%-15s {result['platform_name']} ({result['os_version']})" % "Platform:")
                if result["external_ip"] != "Not available":
                    print(f"%-15s {result['external_ip']}" % "External IP:")
                if result["local_ip"] != "Not available":
                    print(f"%-15s {result['local_ip']}" % "Local IP:")
                for ioc in result["behaviors"]:
                    print(f"%-15s {ioc['tactic']}" % "Tactic:",
                          f"({ioc['tactic_id']})"
                          )
                    print(f"%-15s {ioc['technique']}" % "Technique:",
                          f"({ioc['technique_id']})"
                          )
                    clean_ts = ioc["timestamp"].replace("T", " at ").replace("Z", "")
                    print(f"%-15s {clean_ts}" % "Occurred:")
                    full_description = helper.clean_description(ioc["description"].replace(". ", ".\n"))
                    print(f"{'═' * 72}")
                    print(f"{full_description}\n")
                    return JSONResponse(status_code=200, content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get-aggregate-detects", response_model=List[Any], responses={200: {"model": List[Any]}, 400: {"model": exception.HTTPError}})
def get_aggregate_detects() -> Any:
    """
    Get detect aggregates as specified via json in request body.
    """
    if falcon.token_fail_reason:
        print(str(falcon.token_fail_reason))
        raise HTTPException(status_code=400, detail=str(falcon.token_fail_reason))
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
            return JSONResponse(status_code=200, content=response["body"])
        else:
            errors = response["body"]["errors"]
            for err in errors:
                ecode = err["code"]
                emsg = err["message"]
                logger.error(ecode + ":" + emsg)
            return JSONResponse(status_code=200, content=errors)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def get_details(item_list: list) -> object:  # list or dict
    """Retrieve the details for the item list provided."""
    details = falcon.get_detect_summaries(ids=item_list)
    if details["status_code"] == 200:
        details = details["body"]["resources"]

    return details


@router.get("/get-detect-summary", response_model=List[Any], responses={200: {"model": List[Any]}, 400: {"model": exception.HTTPError}})
def get_detect_summary(id_list: str) -> Any:
    """
    View information about detections for all ids listed in the id_list
    """
    if falcon.token_fail_reason:
        raise HTTPException(status_code=400, detail=str(falcon.token_fail_reason))
    try:
        res = falcon.get_detect_summaries(ids=id_list)
        if res["status_code"] == 200:
            items = res["body"]["resources"]
            if items:
                return JSONResponse(status_code=200, content=items)
            else:
                errors = res["body"]["errors"]
                for err in errors:
                    ecode = err["code"]
                    emsg = err["message"]
                    logger.error(ecode + ":" + emsg)
                return JSONResponse(status_code=200, content=errors)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/update-detects-by-ids", response_model=List[Any], responses={200: {"model": List[Any]}, 400: {"model": exception.HTTPError}})
def update_detects_by_ids(id_list: str, status: str) -> Any:
    """
    Update the detection to the provided status.
    """
    if falcon.token_fail_reason:
        print(str(falcon.token_fail_reason))
        raise HTTPException(status_code=400, detail=str(falcon.token_fail_reason))
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
                    return JSONResponse(status_code=200, content=res_msg)
            else:
                errors = update_result["body"]["errors"]
                for err in errors:
                    ecode = err.get("code", 500)
                    emsg = err["message"]
                    res_msg = f"[{ecode}] {emsg}"
                    print(res_msg)
                    return JSONResponse(status_code=200, content=res_msg)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
