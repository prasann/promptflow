# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from fastapi import APIRouter

from promptflow._core.tool_meta_generator import generate_tool_meta_in_subprocess
from promptflow._core.tools_manager import collect_package_tools
from promptflow._utils.logger_utils import service_logger
from promptflow.executor._service.contracts.tool_request import RetrieveToolFuncResultRequest, ToolMetaRequest
from promptflow.executor._service.utils.process_utils import SHORT_WAIT_TIMEOUT, invoke_sync_function_in_process
from promptflow.executor._service.utils.service_utils import generate_error_response

router = APIRouter(prefix="/tool")


@router.get("/package_tools")
def list_package_tools():
    return collect_package_tools()


@router.post("/retrieve_tool_func_result")
async def retrieve_tool_func_result(request: RetrieveToolFuncResultRequest):
    from promptflow._core.tools_manager import retrieve_tool_func_result

    args = (request.func_call_scenario, request.func_path, request.func_kwargs, request.ws_triple)
    return await invoke_sync_function_in_process(retrieve_tool_func_result, args=args, wait_timeout=SHORT_WAIT_TIMEOUT)


@router.post("/meta")
def gen_tool_meta(request: ToolMetaRequest):
    tool_dict, exception_dict = generate_tool_meta_in_subprocess(request.working_dir, request.tools, service_logger)
    exception_dict = {
        source: generate_error_response(error_dict).to_dict() for source, error_dict in exception_dict.items()
    }
    return {"tools": tool_dict, "errors": exception_dict}
