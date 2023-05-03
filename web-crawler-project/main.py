import multiprocessing
import time

import pandas as pd

# import utils to get getTableData and run_websocket function
from utils import *

def primary_code(dict_stock_stock_data_pair_manager):
    """
    :param dict_stock_stock_data_pair_manager:
    :return:

    This function handles will convert the dictionary type data into dataframe
    """
    time_to_print_df = 0
    while True:
        df = pd.DataFrame(list(dict_stock_stock_data_pair_manager.values()))
        time.sleep(1)

        if time.perf_counter() - time_to_print_df > 10:
            # testing to ensure that the table is generated correctly, checks every 10 sec
            print(df)

def data_socket(dict_stock_stock_data_pair_manager):
    """

    :param dict_stock_stock_data_pair_manager:
    """

    dict_of_dict = get_table_data()
    run_websocket(dict_of_dict, dict_stock_stock_data_pair_manager)


if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        # dict type manager that link the primary_process with data_socket_process
        new_dict_stock_stock_data_pair_manager = manager.dict()

        primary_process = multiprocessing.Process(target=primary_code, args=[
            new_dict_stock_stock_data_pair_manager])

        data_socket_process = multiprocessing.Process(target=data_socket, args=[
            new_dict_stock_stock_data_pair_manager])

        primary_process.start()
        data_socket_process.start()

        primary_process.join()
        data_socket_process.join()