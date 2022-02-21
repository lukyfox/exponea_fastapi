import asyncio
import ast
import httpx
import logging

from fastapi import FastAPI
from typing import List
from model.Response import Response

DEBUG = False
MAX_REQUESTS = 2
TIME_LIMIT = 300
MAX_TIMEOUT = 600
URL_TO_TEST = 'https://exponea-engineering-assignment.appspot.com/api/work'

FORMAT = "%(levelname)s:%(message)s"
if DEBUG:
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
else:
    logging.basicConfig(format=FORMAT, level=logging.ERROR)

app = FastAPI()


async def send_request(
        async_client: httpx.AsyncClient, url: str = URL_TO_TEST, timeout: int = MAX_TIMEOUT
) -> Response:
    """
    Function for sending single request to URL
    :param async_client: AsyncClient context manage
    :param url: url for sending requests
    :param timeout: max portion of time in ms for remote service to respond
    :return: Response instance
    """
    try:
        response = await async_client.get(url=url, timeout=timeout/1000.0)
        if response.status_code == 200:
            result = Response(
                time=ast.literal_eval(response.content.decode())['time'],
                status=response.status_code,
                message='OK'
            )
            return result
        result = Response(
            time=0,
            status=response.status_code,
            message=f'Invalid result from {url}'
        )
        if DEBUG:
            logging.debug(result.as_dict())
        return result

    except httpx.ReadTimeout as read_timeout:
        result = Response(
            time=0,
            status='error',
            message=f'timeout error: {read_timeout.args}'
        )
        if DEBUG:
            logging.debug(result.as_dict())
        return result

    except Exception as e:
        result = Response(
            time=0,
            status='error',
            message=f'unspecified error: {e.args}'
        )
        if DEBUG:
            logging.debug(result.as_dict())
        return result


async def send_multiple_requests(
        async_client: httpx.AsyncClient, request_count: int, timeout: int = MAX_TIMEOUT
) -> List[Response]:
    """
    :param async_client: AsyncClient context manager
    :param request_count: number of asynchronous requests
    :param timeout: max portion of time in ms for remote service to respond
    :return: list of Response instances (size equals to request_count)
    """
    request_list = [send_request(async_client, timeout=timeout) for _ in range(request_count)]
    response_list = await asyncio.gather(*request_list)
    return response_list


@app.get("/api/smart")
async def ask_remote_server(timeout: int = MAX_TIMEOUT) -> dict:
    """
    Main function for receiving and GET requests - process sending to remote entry point and process response
    :param timeout: url query parameter specifying max timeout in ms for GET request
    :return: application/json
    """

    async with httpx.AsyncClient() as async_client:
        response_list = await send_multiple_requests(async_client, request_count=1, timeout=timeout)
        if 0 < response_list[0].get_time() <= TIME_LIMIT:
            if DEBUG:
                response_list[0].set_message('1st request successful')
                logging.debug(response_list[0].as_dict())
            return {'time': response_list[0].get_time()}

        response_list.extend(await send_multiple_requests(async_client, MAX_REQUESTS, timeout))
        valid_response_list = [r.as_dict() for r in response_list if r.get_time() > 0]
        if not valid_response_list:
            if DEBUG:
                logging.debug(f'None of {MAX_REQUESTS+1} requests was successful')
                logging.debug([r.as_dict() for r in response_list])
            return {'time': 0}

        valid_response_list = sorted(valid_response_list, key=lambda by: by['time'])
        return {'time': valid_response_list[0]['time']}
