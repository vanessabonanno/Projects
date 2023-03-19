import csv
import re


def process_citations(citations_file_path):
    result = []
    with open(citations_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            result.append(row)
    return result


my_data = process_citations("citations_sample.csv")


def do_compute_impact_factor(data, dois, year):
    divisor = 0
    dividend = 0
    year = int(year)
    year_1 = int(year) - 1
    year_2 = int(year) - 2
    good_date = list()
    bad_date = list()
    cited_citations = list()

    for row in data:
        full_year = row["creation"]
        only_year = int(full_year[0:4])

        if row["cited"] in dois:
            cited_citations.append(row)
            if only_year == year:
                dividend += 1
        if row["citing"] in dois:
            # print(row["citing"])
            if only_year == year_1 or only_year == year_2:
                # print(year_1)
                if row["citing"] not in good_date:
                    divisor += 1
                    good_date.append(row["citing"])
            else:
                if row["citing"] not in bad_date:
                    bad_date.append(row["citing"])
    # print("divisor1: ", divisor)
    # print("dividend1: ", dividend)
    # print("good: ", good_date)
    # print("bad: ", bad_date)

    for doi in dois:
        if doi not in good_date and doi not in bad_date:
            #print(doi)
            for row in cited_citations:
                if row["cited"] == doi:
                    creation_year = row.get("creation")[0:4]
                    creation_year = int(creation_year)
                    creation_month = 0
                    creation_day = 0
                    if len(row["creation"]) > 4:
                        creation_month = int(row["creation"][5:7])
                    if len(row["creation"]) > 7:
                        creation_day = int(row["creation"][8:10])
                    timespan = re.split('P|Y|M|D', row["timespan"])
                    timespan_year = int(timespan[1])
                    timespan_month = 0
                    timespan_day = 0
                    if len(timespan) > 3:
                        timespan_month = int(timespan[2])
                    if len(timespan) > 4:
                        timespan_day = int(timespan[3])
                    if "-" in timespan:
                        if creation_day + timespan_day > 31:
                            timespan_month += 1
                        if creation_month + timespan_month > 12:
                            timespan_year += 1
                        cited_pub_year = creation_year + timespan_year
                        # print(creation_year)
                        # print(timespan_year)
                        # print(cited_pub_year)
                        # print(year_1)
                        if cited_pub_year == year_1 or cited_pub_year == year_2:
                            divisor += 1
                            if row["cited"] not in good_date:
                                good_date.append(row["cited"])
                        else:
                            if row["cited"] not in bad_date:
                                bad_date.append(row["cited"])
                    else:
                        if creation_day - timespan_day <= 0:
                            timespan_month += 1
                        if creation_month - timespan_month <= 0:
                            timespan_year += 1
                        cited_pub_year = creation_year - timespan_year

                        if cited_pub_year == year_1 or cited_pub_year == year_2:
                            divisor += 1
                            if row["cited"] not in good_date:
                                good_date.append(row["cited"])
                        else:
                            if row["cited"] not in bad_date:
                                bad_date.append(row["cited"])
    #print("divisor2: ", divisor)
    #print("dividend2: ", dividend)
    #print("good2: ", good_date)
    #print("bad2: ", bad_date)
    if divisor != 0:
        result = dividend/divisor
        result = str(result)
        return "The Impact Factor is: "+result
    elif divisor == 0:
        result = "No input DOIs published in "+str(year_1)+" or "+str(year_2)+""
        return result


my_data3 = [{'citing': 'doi1', 'cited': 'doiA', 'creation': '2015-30-09', 'timespan': 'P8Y0M10D'},
            {'citing': 'doi2', 'cited': 'doiB', 'creation': '2016-12', 'timespan': 'P16Y11M'},
            {'citing': 'doi3', 'cited': 'doiC', 'creation': '2019', 'timespan': 'P2Y'},
            {'citing': 'doi4', 'cited': 'doiC', 'creation': '2018', 'timespan': 'P1Y'},
            {'citing': 'doi4', 'cited': 'doiD', 'creation': '2018', 'timespan': 'P11Y'},
            {'citing': 'doi4', 'cited': 'doiE', 'creation': '2018', 'timespan': '-P1Y'},
            {'citing': 'doi5', 'cited': 'doiA', 'creation': '2020', 'timespan': 'P13Y'},
            {'citing': 'doi5', 'cited': 'doiB', 'creation': '2020', 'timespan': 'P20'},
            {'citing': 'doi6', 'cited': 'doiB', 'creation': '2005', 'timespan': 'P5Y'},
            {'citing': 'doiA', 'cited': 'doi6', 'creation': '2007', 'timespan': 'P2Y'},
            {'citing': 'doiC', 'cited': 'doi2', 'creation': '2017-04', 'timespan': 'P0Y4M'},
            {'citing': 'doiD', 'cited': 'doi6', 'creation': '2007', 'timespan': 'P2Y'},
            {'citing': 'doiD', 'cited': 'doiA', 'creation': '2007', 'timespan': 'P0Y0M'}]

my_set = {"10.31338/uw.9788323522157", "10.1097/nmd.0b013e3181636fd4", "10.1177/1533210109333771",
          "10.1007/s00134-019-05862-0", "10.3389/fenvs.2015.00036", "10.1016/s0140-6736(97)11096-0"}
set1 = {"doiE", "doiA", "doiD", "doiB", "doiC", "doi4"}
set2 = {"doiE", "doiA", "doiD", "doi1", "doi2", "doiB"}
# print(do_compute_impact_factor(my_data, my_set, "2016"))  # The Impact Factor is: 45.0

print(do_compute_impact_factor(my_data3, set1, "2020"))  # The Impact Factor is: 1.0

# print(do_compute_impact_factor(my_data3, set1, "2019"))  # The Impact Factor is: 0.5
#print(do_compute_impact_factor(my_data3, set2, "2016"))  # The Impact Factor is: 1.0
#print(do_compute_impact_factor(my_data3, set2, "2000"))  # The Impact Factor is: 0.0
#print(do_compute_impact_factor(my_data3, set2, "1000"))  # No input DOIs published in 999 or 998
