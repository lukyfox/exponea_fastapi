import asyncio
import httpx
import logging
import time

from fastapi import FastAPI
from typing import List
from model.Response import Response, Counter

DEBUG = False
MAX_REQUESTS = 2
FIRST_RESPONSE_TIME_LIMIT = 300
MAX_TIMEOUT = 600
URL_TO_TEST = 'https://exponea-engineering-assignment.appspot.com/api/work'

FORMAT = "%(levelname)s:%(message)s"
if DEBUG:
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
else:
    logging.basicConfig(format=FORMAT, level=logging.ERROR)

app = FastAPI()


async def async_timer(limit: int) -> int:
    """
    Waiting for given limit of seconds, used as counter if first request responded in limit
    :param limit: seconds to wait before return
    :return: limit in seconds (float)
    """
    return await asyncio.sleep(limit, result=limit)


async def send_request(
        async_client: httpx.AsyncClient, url: str = URL_TO_TEST, timeout: int = MAX_TIMEOUT, counter: Counter = None
) -> Response:
    """
    Function for sending single request to URL
    :param async_client: AsyncClient context manage
    :param url: url for sending requests
    :param timeout: max portion of time in ms for remote service to respond, otherwise request failed
    :param counter:
    :return: Response instance
    """
    start = time.time()
    try:
        response = await async_client.get(url=url, timeout=timeout/1000.0)
        if response.status_code == 200:
            end = int((time.time() - start)*1000)
            if end > timeout:
                raise httpx.ReadTimeout
            result = Response(
                time=end,
                status=response.status_code,
                message='OK'
            )
            if counter:
                counter.response_sent = end
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
            message=f'timeout error - {timeout} ms exceeded'
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
        async_client: httpx.AsyncClient, request_count: int, timeout: int = MAX_TIMEOUT, counter: Counter = None
) -> List[Response]:
    """
    :param async_client: AsyncClient context manager
    :param request_count: number of asynchronous requests
    :param timeout: max portion of time in ms for remote service to respond
    :param counter: Counter class instance to store time of first response
    :return: list of Response instances (size equals to request_count)
    """

    response_list_secondary = []
    first_response = await send_request(async_client, timeout=timeout, counter=counter)
    if counter.response_sent > await async_timer(FIRST_RESPONSE_TIME_LIMIT/1000.0):
        request_list_secondary = [send_request(async_client, timeout=timeout) for _ in range(MAX_REQUESTS)]
        response_list_secondary = await asyncio.gather(*request_list_secondary)

    if response_list_secondary:
        response_list_secondary.append(first_response)
        return response_list_secondary
    return [first_response]

@app.get("/api/smart")
async def ask_remote_server(timeout: int = MAX_TIMEOUT) -> dict:
    """
    Main function for receiving and GET requests - process sending to remote entry point and process response
    :param timeout: url query parameter specifying max timeout in ms for GET request
    :return: application/json
    """

    timeout = timeout if 0 < timeout <= MAX_TIMEOUT else MAX_TIMEOUT
    counter = Counter(timeout)
    async with httpx.AsyncClient() as async_client:
        response_list = await send_multiple_requests(async_client, request_count=1, timeout=timeout, counter=counter)
        valid_response_list = [r.as_dict() for r in response_list if r.get_time() > 0]
        if not valid_response_list:
            if DEBUG:
                logging.debug(f'None of {MAX_REQUESTS+1} requests was successful')
            return {'time': 0}

        valid_response_list = sorted(valid_response_list, key=lambda by: by['time'])
        if DEBUG:
            return [r.as_dict() for r in response_list]
        return {'time': valid_response_list[0]['time']}
