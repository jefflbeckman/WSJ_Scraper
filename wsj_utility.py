"""
Wall Street Journal PDF Download Utility

This module is used to automate the process of downloading the
Wall Street Journal from public URLs such as:

    Section A Main Section

    http://online.wsj.com/public/resources/documents/print/WSJ_-A001-20161230.pdf
    to
    http://online.wsj.com/public/resources/documents/print/WSJ_-A016-20161230.pdf


    Section B  Business and Finance

    http://online.wsj.com/public/resources/documents/print/WSJ_-B001-20161230.pdf
    to
    http://online.wsj.com/public/resources/documents/print/WSJ_-B010-20161230.pdf



    Section M Mansions Fridays only

    http://online.wsj.com/public/resources/documents/print/WSJ_-M001-20161230.pdf
    to
    http://online.wsj.com/public/resources/documents/print/WSJ_-M008-20161230.pdf


    Section C Review Saturdays only

    http://online.wsj.com/public/resources/documents/print/WSJ_-C001-20161224.pdf
    to
    http://online.wsj.com/public/resources/documents/print/WSJ_-C014-20161224.pdf


    Section D Off Duty Saturdays only

    http://online.wsj.com/public/resources/documents/print/WSJ_-D001-20161224.pdf
    to
    http://online.wsj.com/public/resources/documents/print/WSJ_-D012-20161224.pdf

"""

# URL request library documented in https://docs.python.org/3/library/urllib.html
from urllib.request import urlretrieve
import urllib.error

# Option Parsing library documented in https://docs.python.org/3/library/optparse.html
from optparse import OptionParser

# Date strings library documented in https://docs.python.org/3/library/datetime.html
import datetime

#OS library for path manipulation
import os


#Globals
WSJ_URL_prefix = "http://online.wsj.com/public/resources/documents/print/WSJ_-"
WSJ_URL_format = "{0}{1:03}-{2}.pdf"
    #{0} = section [1 character]
    #{1} = page [3 digits, 0 padded]
    #{2} = date string [YYYYMMDD]
INCOMING_DATE_FORMAT = "%m/%d/%Y"

def main():
    """
    Main function run if this python program is run using the example run string:
        "python.exe wsj_utility.py <options>"

    This program supports three date modes, which may be used together:
        Range mode, using the -b and -e options
        Date mode, using the -d option
        Today Mode, [default], using the -t option

    This program will by default grab sections
    A, B, C (Saturdays), D (Saturdays), and M (Fridays)
    unless secitons are specified using the -s



    :return: 0 if success
    """

    # Option parsing
    usage = 'usage: python.exe %prog [-b "MM/DD/YYYY" -e "MM/DD/YYYY] [-d "MM/DD/YYYY"] [-o "C:\\WSJ"] [-v]'
    parser = OptionParser(usage=usage)

    #Range Mode
    parser.add_option("-b", "--begin", dest="start",
                      help="begin date for range", metavar="MM/DD/YYYY")
    parser.add_option("-e", "--end", dest="end",
                      help="end date for range", metavar="MM/DD/YYYY")

    #Date mode
    parser.add_option("-d", "--date", dest="date",
                      help="specify a date", metavar="MM/DD/YYYY")

    #Today mode
    parser.add_option("-t", "--today", dest="today", action="store_true",
                      help="Set date to today", default=False)

    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="print status messages to stdout")

    #Sections
    parser.add_option("-s", "--sections", dest="sections", default="ABCDM",
                      help="sections ", metavar="ABCDM")

    #Output
    parser.add_option("-o", "--output", dest="output", default="C:\\WSJ",
                      help="Output folder (default=C:\\WSJ)", metavar="C:\\WSJ")


    (options, args) = parser.parse_args()

    # Check that options are set sanely. Options not set will be "None".
    if options.start is not None and options.end is None:
        print("No end date specified for range")
        parser.print_help()
        exit(1)
    if options.start is None and options.end is not None:
        print("No start date specified for range")
        parser.print_help()
        exit(1)

    if options.start is None and options.date is None and not options.today:
        if options.verbose:
            print("No date mode selected, grabbing WSJ for today")
        options.today = True

    if len(options.sections) < 1:
        print("Please specify a valid section to grab")
        exit(1)



    #Download for any date range specified
    if options.start is not None:
        download_range(options.start, options.end, options.sections, options.output, options.verbose)

    if options.date is not None:
        download_date(options.date, options.sections, options.output, options.verbose)

    if options.today:
        download_date(datetime.date.today().strftime(INCOMING_DATE_FORMAT), options.sections, options.output, options.verbose)




def download_range(range_start, range_end, sections, output_folder, verbose):
    """
    Grab WSJ for all dates in range

    :param range_start:
    :param range_end:
    :param sections:
    :param verbose:
    :return:
    """

    #datetime format from http://strftime.org/
    try:
        cur_date = datetime.datetime.strptime(range_start, INCOMING_DATE_FORMAT)
        last_date = datetime.datetime.strptime(range_end, INCOMING_DATE_FORMAT)
    except ValueError:
        print("Incorrect date format, use MM/DD/YYYY")
        exit(1)

    # The datetime library makes it so you can increment the date and cycle
    # through a range of dates. Here we call the download_date function on each date
    while cur_date <= last_date:
        if verbose:
            print("Downloading date " + cur_date.isoformat())
        # Download_date expects a date string, so convert back.
        download_date(cur_date.strftime(INCOMING_DATE_FORMAT), sections, output_folder, verbose)
        cur_date += datetime.timedelta(days=1)


def download_date(date, sections, output_folder, verbose):
    """
    Grab WSJ for a single date

    :param date:
    :param section:
    :param output_folder:
    :param verbose:
    :return:
    """

    #convert date string format
    try:
        # this ugly line appears all over the place, but its just converting between time formats
        # INCOMING_DATE_FORMAT looks like "12/30/2016", and "%Y%m%d" looks like "20161230"
        date_str = datetime.datetime.strptime(date, INCOMING_DATE_FORMAT).strftime("%Y%m%d")
    except ValueError:
        print("Incorrect date format, use MM/DD/YYYY")
        exit(1)

    daily_output_folder = os.path.join(output_folder,datetime.datetime.strptime(date, INCOMING_DATE_FORMAT).strftime("%m-%d-%y"))

    for section in sections:
        success = False
        page_valid = True
        page = 1
        daily_section_output_folder = os.path.join(daily_output_folder,section)
        while page_valid:
            URL = WSJ_URL_prefix + WSJ_URL_format.format(section, page, date_str)
            output_file = os.path.join(daily_section_output_folder, "{0:03}.pdf".format(page))
            if verbose:
                print("\nDownloading  : " + URL + "\nto local file: " + output_file)
            size = download_file(URL, output_file)
            if verbose:
                print("Got {0} bytes".format(size))
            #if we reached a webpage containing no content, exit the loop
            if size is 0:
                page_valid = False
            else:
                success = True
            page = page + 1
        if not success:
            if verbose:
                print("no pages in section " + section)
            os.rmdir(daily_section_output_folder)



def download_file(download_url, output_file):
    """
    Downloads a webpage to a file

    :param download_url: URL to grab from
    :param output_file: File to write URL contents too
    :returns: webpage error code and bytes gotten
    """

    #Windows needs you to create any empty folders before opening a new file
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))

    #Do the page grab
    try:
        file, headers = urlretrieve(download_url,output_file)
    except urllib.error.HTTPError as err:
        return 0

    return int(headers.get("Content-Length"))

if __name__ == "__main__":
    main()