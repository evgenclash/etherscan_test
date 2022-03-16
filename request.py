import typing
from functools import reduce
import requests
from datetime import datetime

from constants import TXHASH, API_KEY, CONTRACT_ADDRESS, INCOME_TYPE


def get_transaction_by_hash() -> typing.Dict:
    return make_request(
        f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={TXHASH}&apikey={API_KEY}")


def get_etc20(address: str) -> typing.Dict:
    resquest_response = make_request(
        f"https://api.etherscan.io/api?module=account&action=tokentx"
        f"&contractaddress={CONTRACT_ADDRESS}"
        f"&address={address}&page=1&offset=100&startblock=0&endblock=27025780&sort=asc"
        f"&apikey={API_KEY}"
    )

    blocks = sort_by_date(resquest_response["result"])

    return create_response(blocks)


def sort_by_date(blocks: typing.List) -> typing.List:
    response = []
    sorted_block = []
    date = ""
    for block in blocks:
        if date == timestamp_to_date(block):
            sorted_block.append(block)
        else:
            if sorted_block:
                response.append(structure_data(sorted_block))
            date = timestamp_to_date(block)
            sorted_block = [block]

    return response


def timestamp_to_date(block):
    return datetime.fromtimestamp(int(block["timeStamp"])).strftime('%d-%m-%y')


def structure_data(blocks: typing.List) -> typing.List[typing.Dict]:
    structured_data = {}
    for block in blocks:
        if not structured_data:
            structured_data = initial_structure_of_block(block)
        else:
            add_eth_income(block, structured_data)

    structured_data["incomeUSD"] = round(structured_data["incomeETH"] * get_eth_price(), 2)
    return structured_data


def add_eth_income(block: typing.Dict, structured_data):
    structured_data["incomeETH"] += int(block["gas"]) * int(block["gasPrice"]) / 1000000000000000000


def initial_structure_of_block(block):
    return {
        "date": timestamp_to_date(block),
        "income_type": INCOME_TYPE,
        "partner": block["tokenName"],
        "asset": block["tokenSymbol"],
        "incomeETH": int(block["gas"]) * int(block["gasPrice"]) / 1000000000000000000
    }


def create_response(blocks: typing.List[typing.Dict]) -> typing.Dict:
    return {
        "result": blocks,
        "total_income_usd": reduce(lambda result, value: result + value["incomeUSD"], blocks, 0)
    }


def get_eth_price() -> float:
    resquest_response = make_request(f"https://api.etherscan.io/api?module=stats&action=ethprice&apikey={API_KEY}")

    return float(resquest_response["result"]["ethusd"])


def make_request(url: str) -> typing.Dict:
    res = requests.get(url)

    return res.json()
