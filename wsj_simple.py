from urllib.request import urlretrieve
import urllib.error
import datetime
import os

sections = "ABCDM"
date = datetime.date.today()
for section in sections:
    page = 0;
    page_valid = True
    len = 1
    while len > 0:
        download_url = "http://online.wsj.com/public/resources/documents/print/WSJ_-{0}{1:03}-{2}.pdf".format(section, page, date.strftime("%Y%m%d"))
        output_file = os.path.join("C:\\WSJ",date.isoformat())
        try:
            file, headers = urlretrieve(download_url, os.path.join(output_file, "{0}_{1}.pdf".format(section,page)))
            len = int(headers.get("Content-Length"))
        except urllib.error.HTTPError as err:
            len = 0



