import os
import re
import json
import argparse
from collections import Counter
from collections import defaultdict


def parse_arguments():
    parser = argparse.ArgumentParser(description='Analysis access.log')
    parser.add_argument('-path', type=file_or_directory, action='store', help='Path to log file')
    return parser.parse_args().path


def file_or_directory(path):
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return path


def append_file_in_file_list(path):
    files = []
    if os.path.isfile(path):
        return [path]
    if os.path.isdir(path):
        for file in os.listdir(path):
            file = path + "/" + file
            files.append(file)
    return files


def collect_data_from_logs(log_files: list):
    for file in log_files:
        with open(file) as log_file:
            count_requests = 0
            top_3_ip = Counter()
            execute_time = defaultdict()
            get_queries = 0
            post_queries = 0
            head_queries = 0
            put_queries = 0
            delete_queries = 0

            for line in log_file:
                regex = r"(?P<ip>.*?) - - \[(?P<date>.*?)(?= ) (?P<timezone>.*?)\] \"(?P<request_method>.*?) (?P<path>.*?)(?P<request_version> HTTP\/.*)?\" (?P<response_status>\d\d\d) (?P<body_bytes_sent>\d*|-) \"(?P<http_referer>.*)\" \"(?P<http_header>.*)\" (?P<request_time>.*)"
                match = re.search(regex, line)
                try:
                    ip_match = match.group("ip")
                    count_requests += 1
                    method = match.group("request_method")
                    execution_time = match.group("request_time")
                    request_time = match.group("date")
                    url = match.group("path")
                    top_3_ip[ip_match] += 1
                    key_for_execute_time = method + " " + ip_match + " " + url + " " + request_time
                    execute_time[key_for_execute_time] = execution_time
                    if method == "GET":
                        get_queries += 1
                    if method == "POST":
                        post_queries += 1
                    if method == "HEAD":
                        head_queries += 1
                    if method == "PUT":
                        put_queries += 1
                    if method == "DELETE":
                        delete_queries += 1

                except AttributeError:
                    pass

            result = [{"count_requests": count_requests,
                       "top_3_ip": top_3_ip.most_common(3),
                       "get_requests_count": get_queries,
                       "post_requests_count": post_queries,
                       "head_requests_count": head_queries,
                       "put_requests_count": put_queries,
                       "delete_requests_count": delete_queries,
                       "top_3_longest_requests": dict(
                           sorted(execute_time.items(), key=lambda x: x[1], reverse=True)[:3])
                       }]

            with open(f"{file[:-4]}_result.json", "w") as result_file:
                result_file.write(json.dumps(result, indent=4))

            print(f'Requests count: {count_requests}')
            print(f'GET: {get_queries}')
            print(f'POST: {post_queries}')
            print(f'HEAD: {head_queries}')
            print(f'PUT: {put_queries}')
            print(f'DELETE: {delete_queries}')
            print(f'TOP 3 IP address: {top_3_ip.most_common(3)}')
            print(f'TOP 3 longest requests: {dict(sorted(execute_time.items(), key=lambda x: x[1], reverse=True)[:3])}')


if __name__ == "__main__":
    path_files = parse_arguments()
    selected_files = append_file_in_file_list(path_files)
    collect_data_from_logs(selected_files)
