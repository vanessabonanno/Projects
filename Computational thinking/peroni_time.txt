import csv
import re
import networkx as nx
import operator
import fnmatch


def process_citations(citations_file_path):
    result = []
    with open(citations_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            result.append(row)
    return result


def do_compute_impact_factor(data, dois, year):
    divisor = 0
    dividend = 0
    year_1 = str(int(year) - 1)
    year_2 = str(int(year) - 2)
    cited_citations = list()
    only_citing = list()
    cited_pub_year = 0
    result = 0
    for row in data:
        full_year = row["creation"]
        only_year = full_year[0:4]
        if row["cited"] in dois:
            cited_citations.append(row)
            if only_year == year:
                dividend += 1
        if row["citing"] in dois:
            if only_year == year_1 or only_year == year_2:
                divisor += 1
        if row["cited"] in cited_citations and row["cited"] not in row["citing"]:
            only_citing.update(row)

    for row in only_citing:
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

                if timespan_year >= 0:
                    cited_pub_year = creation_year + timespan_year
            else:
                if creation_day - timespan_day <= 0:
                    timespan_month += 1
                if creation_month - timespan_month <= 0:
                    timespan_year += 1
                cited_pub_year = creation_year - timespan_year
            if cited_pub_year == year_1 or cited_pub_year == year_2:
                divisor += 1
    if divisor != 0:
        result = dividend/divisor
        result = str(result)
        return "The Impact Factor is: "+result
    elif divisor == 0:
        result = "No input DOIs published in "+year_1+" or "+year_2+""
        return result
    return result


def do_get_co_citations(data, doi1, doi2):
    result1 = set()
    result2 = set()
    for row in data:
        if doi1 in row["cited"]:
            result1.add(row["citing"])
        if doi2 in row["cited"]:
            result2.add(row["citing"])
    result3 = set(result1).intersection(result2)
    return len(result3)


def do_get_bibliographic_coupling(data, doi1, doi2):
    result1 = set()
    result2 = set()
    for row in data:
        if doi1 in row["citing"]:
            result1.add(row["cited"])
        if doi2 in row["citing"]:
            result2.add(row["cited"])
    result3 = set(result1).intersection(result2)
    return len(result3)


def make_a_graph(graph_data):
    result = nx.MultiDiGraph()
    for row in graph_data:
        result.add_edge(row['citing'], row['cited'])
    return result


def do_get_citation_network(data, start, end):
    start = int(start)
    end = int(end)
    confirmed_dois = set()
    bad_dois = set()
    graph_data_final = []

    for row in data:
        creation_year = int(row["creation"][0:4])
        creation_day = 0
        creation_month = 0
        if end >= creation_year >= start:
            if row["citing"] not in confirmed_dois:
                confirmed_dois.add(row["citing"])
            if row["cited"] in confirmed_dois:
                graph_data_final.append(row)
            elif row["cited"] not in bad_dois:
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

                    if timespan_year >= 0:
                        cited_pub_year = creation_year + timespan_year
                else:
                    if creation_day - timespan_day <= 0:
                        timespan_month += 1
                    if creation_month - timespan_month <= 0:
                        timespan_year += 1
                    cited_pub_year = creation_year - timespan_year
                if end >= cited_pub_year >= start:
                    confirmed_dois.add(row["cited"])
                    graph_data_final.append(row)
                else:
                    bad_dois.add(row["cited"])
        else:
            bad_dois.add(row["citing"])
    return make_a_graph(graph_data_final)


def do_merge_graphs(g1, g2):
    if type(g1) == type(g2):
        combined_graph = nx.compose(g1, g2)
        return combined_graph


def do_search_by_prefix(data, prefix, is_citing):
    prefix_list = []
    if is_citing:
        for row in data:
            doi_prefix = row["citing"].split("/")[0]
            if doi_prefix == prefix:
                prefix_list.append(row)
    if not is_citing:
        for row in data:
            doi_prefix = row["cited"].split("/")[0]
            if doi_prefix == prefix:
                prefix_list.append(row)
    return prefix_list


def do_search(data, query, field):
    result = []
    query = query.lower()
    list_tokens = query.split()
    for row in data:
        boolean_result = []

        for item in list_tokens:

            if item == "and":
                boolean_result.append(" and ")

            elif item == "or":
                boolean_result.append(" or ")

            elif item == "not":
                boolean_result.append("not ")

            else:
                field_data = row[field].lower()
                match = str(fnmatch.fnmatch(field_data, item))
                boolean_result.append(match)

        boolean_string = ''.join(boolean_result)
        if eval(boolean_string):
            result.append(row)
    return result


def cmp1(arg1, op, arg2):
    ops = {
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne,
        '>=': operator.ge,
        '<': operator.lt,
        '>': operator.gt}
    operation = ops.get(op)
    return operation(arg1, arg2)


def do_filter_by_value(data, query, field):
    result = []
    query = query.lower()
    split_query = re.split('( and )|( or )|(not )| ', query)
    booleans = [" and ", " or ", "not "]
    try:
        while True:
            split_query.remove(None)
    except ValueError:
        pass
    try:
        while True:
            split_query.remove("")
    except ValueError:
        pass
    for row in data:
        boolean_result = []
        i = 0
        if field == "timespan":
            timespan = re.split('P|Y|M|D', row["timespan"])
            timespan_year = int(timespan[1])
            timespan_month = 0
            timespan_day = 0
            if len(timespan) > 3:
                timespan_month = int(timespan[2])
                if len(timespan) == 5:
                    timespan_day = int(timespan[3])
            if "-" in timespan:
                timespan_year = -timespan_year
                timespan_month = -timespan_month
                timespan_day = -timespan_day

        for item in split_query:
            if item in booleans:
                boolean_result.append(item)
            elif len(item) > 2 and split_query[i-1] in booleans or (len(item) > 2 and i == 0):
                boolean_result.append(str(row[field].lower() == item))
            else:
                if len(item) <= 2 and field != "timespan" or (field == "timespan" and (item == "==" or item == "!=")):
                    boolean_result.append(str(cmp1(row[field].lower(), item, split_query[i + 1])))
                elif len(item) <= 2 and field == "timespan":
                    query_timespan = re.split('p|y|m|d', split_query[i + 1])
                    q_year = int(query_timespan[1])
                    q_month = 0
                    q_day = 0

                    if len(query_timespan) > 3:
                        q_month = int(query_timespan[2])
                        if len(query_timespan) == 5:
                            q_day = int(query_timespan[3])
                    if "-" in query_timespan:
                        q_year = -q_year
                        q_month = -q_month
                        q_day = -q_day

                    if cmp1(timespan_year, item, q_year) and timespan_year != q_year:
                        boolean_result.append("True")
                    elif q_year != timespan_year:
                        boolean_result.append("False")
                    elif q_year == timespan_year:
                        if cmp1(timespan_month, item, q_month) and q_month != timespan_month:
                            boolean_result.append("True")
                        elif q_month == timespan_month:
                            if cmp1(timespan_day, item, q_day):
                                boolean_result.append("True")
                            else:
                                boolean_result.append("False")
                        else:
                            boolean_result.append("False")
            i += 1
        boolean_string = ''.join(boolean_result)
        if eval(boolean_string):
            result.append(row)
    return result
