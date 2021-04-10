# imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import random
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from dateutil.relativedelta import relativedelta


def sleep_for(option1, option2):
    time_for = random.uniform(option1, option2)
    time_for_int = int(round(time_for))
    sleep(abs(time_for_int - time_for))
    for i in range(time_for_int, 0, -1):
        sleep(1)


def list_of_dates(start_date, end_date, num_days):
    cur_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()

    dates_list = []
    dates_list.append(start_date)
    while cur_date < end:
        cur_date = cur_date + relativedelta(days=num_days)
        dates_list.append(cur_date)

    # if last date is after the end date, remove
    if dates_list[-1] > end:
        dates_list.pop(-1)

    # add the last day
    dates_list.append(end)

    # list of tuples of each date pairing
    tup_list = []
    counter = 1
    for i in dates_list:
        try:
            tup_list.append([i, dates_list[counter]])
            counter += 1
        except:
            pass
    return tup_list


def twitter_scraper(urls, scroll_down_num, post_element_xpath, start_date, end_date, days_between, filename):
    # setting up chrome driver
    driver = webdriver.Chrome()
    driver.set_page_load_timeout(100)

    # dataframe to append tweet to
    df = pd.DataFrame()

    dates_list = list_of_dates(start_date, end_date, days_between)

    # loop through the list of urls parsed in
    for original_url in tqdm(urls):
        for day_tuple in dates_list:
            url = original_url + '%20until%3A' + str(day_tuple[1]) + \
                  '%20since%3A' + str(day_tuple[0]) + '&src=typed_query'

            driver.get(url)
            sleep_for(5, 10)

            for i in range(0, scroll_down_num):
                driver.find_element_by_xpath('//body').send_keys(Keys.END)
                sleep_for(2, 4)

            # get a list of each post
            post_list = driver.find_elements_by_xpath(post_element_xpath)

            post_text = [x.text for x in post_list]

            # create temp dataset of each tweet
            temp_df = pd.DataFrame(post_text, columns={'all_text'})

            df = df.append(temp_df)

    driver.quit()
    filepath = filename + '.csv'
    df.to_csv(filepath)
