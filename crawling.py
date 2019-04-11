import os
from bs4 import BeautifulSoup
from selenium import webdriver
import urllib.request

from selenium.common.exceptions import TimeoutException

if __name__ == '__main__':
    root_path = "./car_dir/"
    if not os.path.isdir(root_path):
        os.mkdir(root_path)

    driver = webdriver.Chrome('./chromedriver/chromedriver')
    driver.set_page_load_timeout(10)
    url = 'http://www.bobaedream.co.kr/cyber/CyberCar.php'

    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    maker_li_list = soup.find("ul", {'class': 'finder-option-list'})\
                        .find_all("li")
    maker_button_list = [maker_li.find("button") for maker_li in maker_li_list]
    maker_button_list.pop(0)

    maker_dic = {}
    model_dic = {}

    for maker_button in maker_button_list:
        maker_name = maker_button.get_text()
        maker_name = maker_name.replace("/", ", ")
        maker_id = int(maker_button["onclick"].replace("car_depth_cyber('", "")
                                              .replace("', 1, '', this);", ""))
        print(maker_name, maker_id)

        maker_path = root_path+maker_name + "/"
        if not os.path.isdir(maker_path):
            os.mkdir(maker_path)

        maker_url = "{}?maker_no={}".format(url, maker_id)

        driver.get(maker_url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        model_li_list = soup.find("div", {"id": "finder-model"})\
                            .find("div", {"class": "layer-cont"})\
                            .find("ul")\
                            .find_all("li")
        model_button_list = [model_li.find("button") for model_li in model_li_list]

        for model_button in model_button_list:
            model_name = model_button.get_text()
            model_id = int(model_button["onclick"].replace("selChange('", "")
                                                  .replace("', this)", ""))
            print("\t", model_name, model_id)

            model_path = maker_path + model_name + "/"
            if not os.path.isdir(model_path):
                os.mkdir(model_path)

            model_url = "{}&model_no={}".format(maker_url, model_id)
            driver.get(model_url)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            detail_li_list = soup.find("div", {"id": "finder-detail"})\
                                 .find("div", {"class": "layer-cont"})\
                                 .find("ul")\
                                 .find_all("li")
            detail_li_list.pop(0)

            for detail_li in detail_li_list:
                detail_cat = int(detail_li["data-gb"][1:])
                if model_id == detail_cat:
                    detail_button = detail_li.find("button")
                    detail_name = detail_button.get_text()
                    detail_id = int(detail_button["onclick"].replace("car_depth_cyber('", "")
                                                            .replace("', '2', '', this)", ""))
                    print("\t\t", detail_name, detail_id)

                    detail_path = model_path + detail_name + "/"
                    if not os.path.isdir(detail_path):
                        os.mkdir(detail_path)

                    detail_url = "{}?model_no={}&maker_no={}&group_no={}".format(url, detail_id, maker_id, model_id)
                    page_num = 1

                    while True:
                        detail_page_url = "{}&page={}".format(detail_url, page_num)
                        print("\t\t\t", "page {}".format(page_num))

                        driver.get(detail_page_url)
                        html = driver.page_source
                        soup = BeautifulSoup(html, 'html.parser')

                        car_li_list = soup.find("div", {"class": "wrap-thumb-list"})\
                                          .find("ul", {"class": "clearfix"})\
                                          .find_all("li", {"class": "product-item"})
                        if not car_li_list:
                            break

                        for i, car_li in enumerate(car_li_list):
                            try:
                                car_url = car_li.find("div", {"class": "thumb"})\
                                                .find("a")["href"]
                                car_url = "http://www.bobaedream.co.kr" + car_url
                                print("\t\t\t\t", (page_num-1)*70 + i)

                                driver.get(car_url)
                                html = driver.page_source
                                soup = BeautifulSoup(html, 'html.parser')

                                car_img_a_list = soup.find("div", {"class": "gallery-thumb"}) \
                                    .find_all("a")

                                for car_img_a in car_img_a_list[:3]:
                                    car_img_url = car_img_a.find("img")["onerror"]
                                    car_img_url = car_img_url.replace("this.src='", "").replace("'", "")
                                    car_img_name = car_img_url.split('/')[-1]
                                    print("\t\t\t\t\t", car_img_name)
                                    if not os.path.isfile(detail_path + car_img_name):
                                        urllib.request.urlretrieve(car_img_url, detail_path + car_img_name)
                            except TimeoutException:
                                print("\t\t\t\t\t", "except")
                                driver.quit()

                                driver = webdriver.Chrome('./chromedriver/chromedriver')
                                driver.set_page_load_timeout(5)
                                continue

                        page_num += 1
