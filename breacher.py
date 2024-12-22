import requests
import threading
import argparse
import re
from urllib.parse import urlparse

parser = argparse.ArgumentParser()

parser.add_argument("-u", help="target url", dest="target")
parser.add_argument("--path", help="custom path prefix", dest="prefix")
parser.add_argument("--type", help="set the type i.e. html, asp, php", dest="type")
parser.add_argument(
    "--fast", help="uses multithreading", dest="fast", action="store_true"
)
args = parser.parse_args()

target = args.target

print(f"""\t\t\033[1;34m\n\n______   ______ _______ _______ _______ _     _ _______  ______
|_____] |_____/ |______ |_____| |       |_____| |______ |_____/
|_____] |    \_ |______ |     | |_____  |     | |______ |    \_

                          \033[37mMade with \033[91m<3\033[37m By D3V\033[1;m""")

print("""\n  I am not responsible for your shit and if you get some error while
 running Breacher, there are good chances that target isn't responding.\n""")
print(
    "\033[1;31m--------------------------------------------------------------------------\033[1;m\n"
)

try:
    target = target.replace("https://", "")
except:
    print(
        "\033[1;31m[-]\033[1;m -u argument is not supplied. Enter python breacher -h for help"
    )
    quit()

target = target.replace("http://", "")
target = target.replace("/", "")
target = "http://" + target
if args.prefix != None:
    target = target + args.prefix
try:
    r = requests.get(target + "/robots.txt")
    if "<html>" in r.text:
        print("  \033[1;31m[-]\033[1;m Robots.txt not found\n")
    else:
        print(
            "  \033[1;32m[+]\033[0m Robots.txt found. Check for any interesting entry\n"
        )
        print(r.text)
except:
    print("  \033[1;31m[-]\033[1;m Robots.txt not found\n")
print(
    "\033[1;31m--------------------------------------------------------------------------\033[1;m\n"
)


def remove_tags(html):
    return re.sub(r"(?s)<.*?>", "", html)


def diff_map(body_1, body_2):
    sig = []
    lines_1, lines_2 = body_1.split("\n"), body_2.split("\n")
    for line_1, line_2 in zip(lines_1, lines_2):
        if line_1 == line_2:
            sig.append(line_1)
    return sig


def baseline(response_1, response_2):
    factors = {
        "same_code": None,
        "same_plaintext": None,
        "same_body": None,
        "lines_num": None,
        "lines_diff": None,
        "same_headers": None,
        "same_redirect": None,
    }
    if isinstance(response_1, requests.models.Response) and isinstance(
        response_2, requests.models.Response
    ):
        body_1, body_2 = response_1.text, response_2.text
        if response_1.status_code == response_2.status_code:
            factors["same_code"] = response_1.status_code
        if response_1.headers.keys() == response_2.headers.keys():
            factors["same_headers"] = list(response_1.headers.keys())
            factors["same_headers"].sort()
        if urlparse(response_1.url).path == urlparse(response_2.url).path:
            factors["same_redirect"] = urlparse(response_1.url).path
        else:
            factors["same_redirect"] = ""
        if response_1.text == response_2.text:
            factors["same_body"] = response_1.text
        elif response_1.text.count("\n") == response_2.text.count("\n"):
            factors["lines_num"] = response_1.text.count("\n")
        elif remove_tags(body_1) == remove_tags(body_2):
            factors["same_plaintext"] = remove_tags(body_1)
        elif body_1 and body_2 and body_1.count("\\n") == body_2.count("\\n"):
            factors["lines_diff"] = diff_map(body_1, body_2)
    return factors


def compare(response, factors):
    if not isinstance(response, requests.models.Response):
        return True
    these_headers = list(response.headers.keys())
    these_headers.sort()
    if (
        factors["same_code"] is not None
        and response.status_code != factors["same_code"]
    ):
        return False
    if (
        factors["same_plaintext"] is not None
        and remove_tags(response) != factors["same_plaintext"]
    ):
        return False
    if factors["same_body"] is not None and response.text != factors["same_body"]:
        return False
    if (
        factors["lines_num"] is not None
        and response.text.count("\n") != factors["lines_num"]
    ):
        return False
    if factors["lines_diff"] is not None:
        for line in factors["lines_diff"]:
            if line not in response.text:
                return False
    if (
        factors["same_redirect"] is not None
        and urlparse(response.url).path != factors["same_redirect"]
    ):
        return False
    if factors["same_headers"] is not None and these_headers != factors["same_headers"]:
        return False
    return True


def scan(links):
    res1 = requests.get(target + "/ganasdsjdf")
    res2 = requests.get(target + "/cheadkdldf")
    factors = baseline(res1, res2)
    for link in links:
        link = target + link
        r = requests.get(link)
        check = compare(r, factors)
        http = r.status_code
        if http == 200 and not check:
            res3 = requests.get(target + "/majsdnjkdsd")
            valid = compare(res3, factors)
            if valid:
                print("  \033[1;32m[+]\033[0m Admin panel found: %s" % link)
            else:
                print("  \033[1;31m[-]\033[1;m rate limited or something like that")
        elif http == 404:
            print("  \033[1;31m[-]\033[1;m %s" % link)
        elif http == 302:
            print("  \033[1;32m[+]\033[0m Potential EAR vulnerability found : " + link)
        else:
            print("  \033[1;31m[-]\033[1;m %s" % link)


paths = []


def get_paths(type):
    try:
        with open("paths.txt", "r") as wordlist:
            for path in wordlist:
                path = str(path.replace("\n", ""))
                try:
                    if "asp" in type:
                        if "html" in path or "php" in path:
                            pass
                        else:
                            paths.append(path)
                    if "php" in type:
                        if "asp" in path or "html" in path:
                            pass
                        else:
                            paths.append(path)
                    if "html" in type:
                        if "asp" in path or "php" in path:
                            pass
                        else:
                            paths.append(path)
                except:
                    paths.append(path)
    except IOError:
        print("\033[1;31m[-]\033[1;m Wordlist not found!")
        quit()


if args.fast == True:
    type = args.type
    get_paths(type)
    paths1 = paths[: len(paths) / 2]
    paths2 = paths[len(paths) / 2 :]

    def part1():
        links = paths1
        scan(links)

    def part2():
        links = paths2
        scan(links)

    t1 = threading.Thread(target=part1)
    t2 = threading.Thread(target=part2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
else:
    type = args.type
    get_paths(type)
    links = paths
    scan(links)
