import requests
from bs4 import BeautifulSoup
import csv
from fontTools.ttLib import TTFont
import os
import re

class Spider():

    def __url_download(self, url):
        '''利用requests进行页面抓取并下载'''
        self.headers = {
            'user - agent': 'Mozilla / 5.0(Windows NT 10.0;\
            WOW64) AppleWebKit / 537.36(KHTML, like\
            Gecko) Chrome / 71.0.3578.98\
            Safari / 537.36'
        }
        try:
            html = requests.get(url, headers=self.headers, timeout=10)
            if html.status_code == 200:
                htmls = html.text
        except requests.RequestException:
            htmls = None
        return htmls

    def __url_clean(self, htmls):
        '''通过beautifulsoup进行数据清洗'''
        soup = BeautifulSoup(htmls,features='lxml')
        find_datas = soup.find_all(name="p",class_=("name","star","releasetime",
                                                    "month-wish","total-wish"))
        mouth_nums = re.findall('>本月新增想看：<span><span class="stonefont">(.+?)<',htmls)
        all_nums = re.findall('>总想看：<span><span class="stonefont">(.+?)<',htmls)
        find_font = re.findall(r"colorstone/(\w+\.woff)", htmls)
        find_datas_results = []
        mouth_nums_list = []
        all_nums_list = []
        for i in find_datas:
            find_datas_results.append(i.get_text())
        for i in mouth_nums:
            i = i.replace('&#x', '')
            i = i.split(';')[:-1]
            mouth_nums_list.append(i)
        for i in all_nums:
            i = i.replace('&#x', '')
            i = i.split(';')[:-1]
            all_nums_list.append(i)
        return find_datas_results,mouth_nums_list,all_nums_list,str(find_font[0])


    def __datas_font(self,font):
        '''通过对比下载加密字体并转换'''
        file_list = os.listdir('./fonts')
        if font not in file_list:
            print('不在字体库中, 下载:', font)
            font_url = 'http://vfile.meituan.net/colorstone/' + font
            font_response = requests.get(font_url, headers=self.headers)
            font_response = font_response.content
            with open('./fonts/' + font, 'wb') as f:
                f.write(font_response)
        fonts = TTFont('./fonts/' + font)
        return fonts

    def __datas_font_chance(self,find_font):
        '''将新下载字体进行比对分析得出真实数字映射关系'''
        font_obj = self.__datas_font(find_font)
        uni_list_new = font_obj.getGlyphOrder()[2:]

        font_original  = TTFont('original.woff')
        uni_list_original = font_original.getGlyphOrder()[2:]
        font_dict = {'uniF827': '0','uniEF9E': '1','uniE69E': '2',
                'uniE175': '3','uniE2E8': '4','uniE9FE': '5',
                'uniF83E': '6','uniEC05': '7','uniE446': '8',
                'uniF888': '9'}
        new_font_list = []
        for uni_new in uni_list_new:
            obj_new = font_obj['glyf'][uni_new]
            for uni_original in uni_list_original:
                obj_original = font_original['glyf'][uni_original]
                if obj_original == obj_new:
                    obj_list = {}
                    nui_new_lower = uni_new[3:].lower()
                    obj_list[nui_new_lower] = font_dict[uni_original]
                    new_font_list.append(obj_list)
        new_font_dict = {}
        for i in new_font_list:
            for k, j in i.items():
                new_font_dict[k] = j
        return new_font_dict

    def __font_nums(self,nums,find_font):
        '''字体解密后还原'''
        nums_new = []
        for i in nums:
            list1 = []
            for k in i:
                if k in find_font:
                    j = find_font[k]
                    list1.append(j)
            i = ''.join(list1)
            nums_new.append(i)
        return nums_new

    def __url_analysis(self,datas,mount_person_nums,all_person_nums):
        '''整理数据并写入csv文件'''
        csv_data = []
        with open('maoyan.csv', 'a+', encoding='utf-8', newline='') as f:
            file = csv.writer(f)
            csv_line = []
            for i in datas:
                if i[0] == "总":
                    csv_line.append(i)
                    csv_data.append(csv_line)
                    csv_line = []
                else:
                    csv_line.append(i)
            for i, k in enumerate(csv_data):
                k[-2] = "本月新增想看" + mount_person_nums[i] + "人"
                k[-1] = "总想看" + all_person_nums[i] + "人"
                file.writerow(k)


    def go(self, url):
        '''实例对象的接口函数'''
        htmls = self.__url_download(url)
        datas,mount_nums,all_nums,find_font = self.__url_clean(htmls)
        find_font = self.__datas_font_chance(find_font)
        mount_person_nums = self.__font_nums(mount_nums,find_font)
        all_person_nums = self.__font_nums(all_nums,find_font)
        self.__url_analysis(datas,mount_person_nums,all_person_nums)

def main():
    '''主函数，进行循环页面并多进程爬取数据'''
    spider = Spider()
    url_head = "https://maoyan.com/board/6?offset="
    for i in range(5):
        url = url_head+str(i*10)
        spider.go(url)



if __name__ == '__main__':
    main()
