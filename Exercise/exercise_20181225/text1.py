from bs4 import BeautifulSoup
import re
import requests
import pandas as pd


def download_csv(url):
    '''
        下载函数
    '''
    # 定义headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
         AppleWebKit/537.36\
        (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"}
    # 通过get方法获取
    result = requests.get(url, headers=headers)
    return result.content


def find_csv(csv_file):
    '''
        寻找到相应的数据返回数据及列标签
    '''
    # 通过beautifulsoup进行寻找相应投票记录字段
    soup = BeautifulSoup(csv_file, features="lxml")
    all_td = soup.find_all("table", attrs={"class", "ballots"})
    all_td_list = []
    for i in all_td:
        all_td_list.append(i.get_text())
    # 利用正则清洗投票结果
    pattern = re.compile(r"(\s\d\d?\.\s)")
    result1 = pattern.split(all_td_list[0])
    result2 = result1[1:]
    result3 = [i.replace(" ", "") for i in result2]

    # 分离投票结果及投票列标签
    result = []
    for i, j in enumerate(result3):
        if i % 2 != 0:
            m = re.findall(r"\d", j)
            result.append(m)
    result_index = re.compile(r"PEP\s\d{4}").findall(result1[0])

    return result, result_index


def csv_load(csv_list, csv_index):
    '''
        通过pandas转换成DataFrame并保存为json文件到当前文件夹
    '''
    # 手动添加末尾“讨论”标签
    csv_index.append("Further discussion")
    # 转换为dataframe格式
    result = pd.DataFrame(
        csv_list,
        index=list(range(1, 63)),
        columns=csv_index)
    # 保存
    with open("Voting_results.json", "a+") as f:
        result.to_json(f)


def main():
    '''
        主函数
    '''
    url_main = "https://civs.cs.cornell.edu/cgi-bin/results.pl?id=E_fe2b74aea628b45d"
    csv_file = download_csv(url_main)
    csv_list, csv_index = find_csv(csv_file)
    csv_load(csv_list, csv_index)


if __name__ == '__main__':
    main()
