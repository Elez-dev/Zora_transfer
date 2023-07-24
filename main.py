import threading
from web3 import Web3
import time
import random
from threading import Thread
from web3.exceptions import TransactionNotFound

value_send_min = 0.00001                                               # Минимальное и
value_send_max = 0.00003                                               # Максимальное количество эфира для отправки самому себе - возьмёт рандомное среднее

number_transactions_min = 10                                           # Минимальное и
number_transactions_max = 20                                           # Максимальное количество транзакций на аккаунт - одна транза стоит примерно 5-7 центов 

time_delay_min = 5                                                     # Минимальное и
time_delay_max = 10                                                    # Максимальное время задержки между транзакциями

number_of_thread = 1                                                   # Количество потоков(акков, которые будут работать одновременно)
RPC_ZORA = 'https://rpc.zora.co/'                                      # RPC, если не работает эта -- можете попробовать эту: https://rpc.zora.energy/
RPC_ETH = 'https://rpc.ankr.com/eth'
MAX_GAS_ETH = 30                                                       # Максимальный газ в сети Ethereum, если он больше заданного, скрипт спит


def chek_gas_eth(max_gas):
    try:
        eth_w3 = Web3(Web3.HTTPProvider(RPC_ETH, request_kwargs={'timeout': 60}))
        while True:
            res = int(round(Web3.from_wei(eth_w3.eth.gas_price, 'gwei')))
            print(f'Газ сейчас - {res} gwei\n')
            if res <= max_gas:
                break
            else:
                time.sleep(100)
                continue
    except:
        return 0


class Zora:
    def __init__(self, private_key, web3, number_thread):
        self.web3 = web3
        self.private_key = private_key
        self.address_wallet = self.web3.eth.account.from_key(private_key).address
        self.number_thread = number_thread

    def send(self, amount_eth, retry=0):
        balance = self.web3.eth.get_balance(self.address_wallet)
        value = Web3.to_wei(amount_eth, 'ether')
        if value > balance:
            value = balance - Web3.to_wei(0.00005, 'ether')
            if value <= 0:
                print(f'{self.number_thread} || Insufficient funds')
                return 'balance'
        val = round(Web3.from_wei(value, 'ether'), 10)
        print(f'{self.number_thread} || Send {val} ETH')
        try:
            txn = {
                'chainId': 7777777,
                'from': self.address_wallet,
                'to': self.address_wallet,
                'value': value,
                'nonce': self.web3.eth.get_transaction_count(self.address_wallet),
                'gasPrice': Web3.to_wei(0.005, 'gwei'),                        # газ, тут и так стоит минмальный, но если хотите больше можете увеличить
                'gas': 100000
            }
            gas = self.web3.eth.estimate_gas(txn)
            txn.update({'gas': gas})

            signed_txn = self.web3.eth.account.sign_transaction(txn, private_key=self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f'{self.number_thread} || Отправил транзакцию')
            time.sleep(5)
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300, poll_latency=20)
            if tx_receipt.status == 1:
                print(f'{self.number_thread} || Транзакция смайнилась успешно')
            else:
                print(f'{self.number_thread} || Транзакция сфейлилась, пытаюсь еще раз')
                time.sleep(30)
                retry += 1
                if retry > 5:
                    return 0
                self.send(amount_eth, retry)
                return

            print(f'{self.number_thread} || Send {val} ETH YourSelf || https://explorer.zora.energy/tx/{Web3.to_hex(tx_hash)}\n')

        except TransactionNotFound:
            print(f'{self.number_thread} || Транзакция не смайнилась за долгий промежуток времени, пытаюсь еще раз')
            time.sleep(30)
            retry += 1
            if retry > 5:
                return 0
            self.send(amount_eth, retry)

        except ConnectionError:
            print(f'{self.number_thread} || Ошибка подключения к интернету или проблемы с РПЦ')
            time.sleep(30)
            retry += 1
            if retry > 5:
                return 0
            self.send(amount_eth, retry)

        except Exception as error:
            if isinstance(error.args[0], dict):
                if 'insufficient funds' in error.args[0]['message']:
                    print(f'{self.number_thread} || Ошибка, скорее всего нехватает комсы')
                    return 'balance'
            else:
                print(error)
                time.sleep(30)
                retry += 1
                if retry > 5:
                    return 0
                self.send(amount_eth, retry)


class Worker(Thread):
    def __int__(self):
        super().__init__()

    def run(self):
        while keys_list:
            private_key = keys_list.pop(0)
            web3 = Web3(Web3.HTTPProvider(RPC_ZORA, request_kwargs={'timeout': 60}))
            number_thread = threading.current_thread().name
            address = web3.eth.account.from_key(private_key).address
            print('----------------------------------------------------------------------------')
            print(f'|   Сейчас работает аккаунт - {address}   |')
            print('----------------------------------------------------------------------------\n\n')

            number_repetitions = random.randint(number_transactions_min, number_transactions_max)
            zora = Zora(private_key, web3, number_thread)
            for _ in range(number_repetitions):
                chek_gas_eth(MAX_GAS_ETH)
                value_send = random.uniform(value_send_min, value_send_max)
                res = zora.send(value_send)
                if res == 'balance':
                    print(f'{number_thread} || На аккаунте {address} закончился баланс')
                    break
                time.sleep(random.randint(time_delay_min, time_delay_max))


if __name__ == '__main__':
    print('  _  __         _               _                                           _ _         ')
    print(' | |/ /___   __| | ___ _ __ ___| | ____ _ _   _  __ _        _____   ____ _| | | ____ _ ')
    print(" | ' // _ \ / _` |/ _ \ '__/ __| |/ / _` | | | |/ _` |      / __\ \ / / _` | | |/ / _` |")
    print(r' | . \ (_) | (_| |  __/ |  \__ \   < (_| | |_| | (_| |      \__ \\ V / (_| | |   < (_| |')
    print(' |_|\_\___/ \__,_|\___|_|  |___/_|\_\__,_|\__, |\__,_|      |___/ \_/ \__,_|_|_|\_\__,_|')
    print('                                          |___/                                    ', '\n')
    print('https://t.me/developercode1')
    print('https://t.me/developercode1')
    print('https://t.me/developercode1\n')

    with open("private_key.txt", "r") as f:
        keys_list = [row.strip() for row in f if row.strip()]

    while keys_list:
        worker = Worker()
        worker.start()
        time.sleep(10)
