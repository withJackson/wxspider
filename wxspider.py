#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import mysql.connector
import requests, os, bs4, sys
from PIL import Image
from bs4 import BeautifulSoup

DRIVER_PATH = "/usr/local/bin/chromedriver"
USERNAME = "" #账号
PASSWORD = "" #密码
OFFICIAL_ACCOUNT = u"xxxxxx" #公众号名称
BASE_URL = "https://mp.weixin.qq.com/"

reload(sys)
sys.setdefaultencoding("utf-8")


class WXSpider:

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=DRIVER_PATH)

    def crawl_gzh(self,num):
        self.__open_gzh()
        imgs=self.__get_img2(num)
        titles=self.__get_article(num)
        self.open_hou()
        self.__find_submit(2,titles,imgs)

    def __open_gzh(self):
        self.driver.get(BASE_URL)
        self.driver.maximize_window()

        WebDriverWait(driver=self.driver, timeout=400).until(
            ec.url_contains("cgi-bin/home?t=home/index")
        )
        # 一定要设置这一步，不然公众平台菜单栏不会自动展开
        self.driver.maximize_window()

    def __get_img2(self, num):
        imgs=[]
        liPages = self.driver.find_elements_by_css_selector("#list_container #list li")
        for m in range(0,len(liPages)):
            if m>0:
                break;
            liPage=liPages[m]
            images = liPage.find_elements_by_css_selector(".weui-desktop-mass__content i")
            for j in range(0, num):
                style = images[j].get_attribute('style')
                url = style.split('url("')[1].split('")')[0]
                resimg = requests.get(url)
                resimg.raise_for_status()
                now = str(round(time.time())).split('.')[0]
                imgname = os.path.join('/Users/qx/Documents/weixinimgs/', str(j) + now + '.jpg')
                imgfile = open(imgname, 'wb')
                for chunk in resimg.iter_content(100000):
                    imgfile.write(chunk)
                imgfile.close()
                imgimg = Image.open(imgname)
                width, height = imgimg.size
                print(width, height)
                size = 200
                if width > size and height > size:
                    if width > height:
                        height = int((size / width) * height)
                        width = 200
                    else:
                        width = int((200 / height) * width)
                        height = 200

                print(200, 200)
                resizeimg = imgimg.resize((200, 200))
                renow = str(round(time.time())).split('.')[0]
                resizeimg.save(
                    os.path.join('/Users/qx/Documents/weixinimgs/yasuo/', 'resize' + str(j) + renow + '.jpg'))
                imgname = '/Users/qx/Documents/weixinimgs/yasuo/resize' + str(j) + renow + '.jpg';
                imgs.append(imgname)
                time.sleep(3)
        return imgs

    def __get_article(self,num):

        links=[]
        titles=[]
        liPages = self.driver.find_elements_by_css_selector("#list_container #list li")
        for m in range(0, len(liPages)):
            if m > 0:
                break;
            liPage=liPages[m]
            articles = liPage.find_elements_by_css_selector(
                ".weui-desktop-mass__content  .weui-desktop-mass-appmsg__title")
            for i in range(0, num):
                link = articles[i].get_attribute('href')
                title = articles[i].text
                links.append(link)
                titles.append(title)
            a = {"links": links, "titles": titles}
        return a   

    def __find_submit(self,num, titles,imgs):
        #发布成功后 页面会进行刷新 所以要切换出iframe  然后再进去
        for i in range(0,int(num)):
            infos_element = self.driver.find_elements_by_css_selector(".childUlLi")[2]
            infos_element.click()
            time.sleep(1)

            infos_submit = infos_element.find_elements_by_css_selector('ul li')[0]
            infos_submit.click()
            time.sleep(5)

            self.driver.switch_to.frame("menuFrame")  # 切入
            time.sleep(3)

            infoclass=self.driver.find_element_by_tag_name('select')

            infoclass.click()
            info = infoclass.find_elements_by_tag_name('option')[16]
            info.click()
            time.sleep(3)

            # 标题
            time.sleep(3)
            ptitle = self.driver.find_element_by_css_selector('.textposition').find_elements_by_tag_name('p')[0].find_element_by_tag_name('input')
            ptitle.send_keys(titles["titles"][i])

            # 链接
            plink = self.driver.find_element_by_css_selector('.textposition').find_elements_by_tag_name('p')[2].find_element_by_tag_name('input')
            plink.send_keys(titles["links"][i])

            # 图片
            pimg = self.driver.find_element_by_css_selector('#photoimg')
            pimg.send_keys(imgs[i])  # 绝对路径
            upload=self.driver.find_element_by_css_selector('.upsub')
            upload.click()
            time.sleep(2)

            #发布
            upload = self.driver.find_element_by_css_selector('.newssub')
            # 改成点击发布

            upload.click()
            time.sleep(3)
            self.driver.switch_to.default_content()

    def open_hou(self):
        # 登录后台
        time.sleep(2)
        self.driver.get('http://xueyazhushou.com/bbs/admin/mlogin.php')  #后台地址
        time.sleep(2)
        username_element = self.driver.find_element_by_css_selector("#id")
        password_element = self.driver.find_element_by_css_selector("#password")
        login_btn = self.driver.find_element_by_tag_name("button")
        username_element.send_keys('') #后台账号
        password_element.send_keys('')  #后台密码
        login_btn.click()
        time.sleep(2)

if __name__ == '__main__':

    wx_spider = WXSpider()
    num = 2  #发布前两条数据

    wx_spider.crawl_gzh(num)
  