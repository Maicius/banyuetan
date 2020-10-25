import requests
import pdfkit
import re
import datetime
from PyPDF2 import PdfFileReader, PdfFileWriter
import os

class banyuetan():
    req = requests.Session()
    pdf_tool = '/usr/local/bin/wkhtmltopdf'
    confg = pdfkit.configuration(wkhtmltopdf=pdf_tool)
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
        "host": "mp.weixin.qq.com"}

    count = 1000
    # 默认是10月21日的时政小测验
    url = 'https://mp.weixin.qq.com/s/i9JfkYZUY2WD3eRz2Md8vg'
    pre_path = './pdf/'
    # 停止时间
    last_year = datetime.datetime.now() - datetime.timedelta(days = 365)
    last_year_stamp = last_year.replace(tzinfo=datetime.timezone.utc).timestamp()

    answers_style = 'display: inline-block;width: 100%;vertical-align: top;overflow: hidden;align-self: flex-start;font-family: -apple-system-font, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;letter-spacing: 0.034em;box-sizing: border-box;'
    def __init__(self, index = 0):
        self.index = index

    def create_pdf(self):
        while self.index < self.count:
            res = self.req.get(self.url,headers=self.headers).text
            next_href_reg = re.compile('(http://mp.weixin.qq.com/s\?[_a-zA-Z0-9\;=&]+)\#wechat_redirect\"')
            text_val_reg = re.compile('textvalue=\"([0-9]+)\"')
            # 上一天测验的链接，如果获取不到，就结束
            next_href = re.findall(next_href_reg, res)[-1]
            text_val = re.findall(text_val_reg, res)[0]
            dd = datetime.datetime.strptime(text_val, "%Y%m%d") + datetime.timedelta(days = 1)
            dd_timestamp = dd.replace(tzinfo=datetime.timezone.utc).timestamp()

            if dd_timestamp < self.last_year_stamp:
                break
            dc = dd.strftime("%Y%m%d")
            print("正在转换date...", dc)
            file_path = self.pre_path + dc + '.pdf'
            try:
                # 这一步比较花时间，可以异步操作
                # 但这样的好处是可以避免爬虫太过频繁触发反爬
                pdfkit.from_string(res, file_path, configuration=self.confg)
            except BaseException as e:
                pass
            finally:
                # 删掉每个pdf的最后一页
                pdf = PdfFileReader(file_path)
                pdf_writer = PdfFileWriter()
                for page in range(pdf.getNumPages()):
                    pdf_writer.addPage(pdf.getPage(page))

                with open(file_path, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)

            self.url = next_href
            self.index += 1
    def run(self):
        try:
            self.create_pdf()
        except BaseException as e:
            print(e)
            print("爬虫结束，开始合并pdf...")
        self.combine_all_pdf()

    def combine_all_pdf(self):
        files = os.listdir(self.pre_path)
        files = sorted(files, reverse=True)
        pdf_writer = PdfFileWriter()
        for file in files:
            pdf = PdfFileReader(os.path.join(self.pre_path, file))
            for page in range(pdf.getNumPages() - 1):
                pdf_writer.addPage(pdf.getPage(page))

        with open("半月谈时政小测验.pdf", 'wb') as output_pdf:
            pdf_writer.write(output_pdf)


if __name__ =='__main__':
    ban = banyuetan()
    ban.run()
