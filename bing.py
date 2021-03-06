


# -*- coding: utf-8 -*-

__author__ = 'Nop Phoomthaisong (aka @MaYaSeVeN)'
__version__ = 'reverseIP version 1.0 ( http://mayaseven.com )'

import urllib
import urllib2
import json
import sys
import optparse
import socket
import csv



def main():
    print "\n" + __version__

    usage = "Usage: python " + sys.argv[
        0] + " -k [Bing API Key] [IP_1] [IP_2] [IP_N] [Domain_1] [Domain_2] [Domain_N]\nUsage: python " + \
            sys.argv[
                0] + " -k [Bing API Key] -l [list file of IP address]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-k", "--key", dest="key", help="Bing API key")
    parser.add_option("-l", "--list", dest="file", metavar="FILE", help="list file of IP address")
    parser.add_option("-d", "--disable", action="store_false",
                      help="set this option to disable to recheck is that the domain is in IP address",
                      default=True)

    (options, args) = parser.parse_args()

    if not options.key or (not options.file and len(args) == 0):
        print parser.format_help()
        print """
you need to..
1.register or use microsoft account for get Bing API key -> https://datamarket.azure.com/
2.choose free plan 5,000 Transactions/month -> https://datamarket.azure.com/dataset/bing/search
        """
        exit(1)

    key = options.key
    recheck = options.disable
    file = options.file
    reverseIP = RevereIP(args, key, recheck)
    reverseIP.run()


def stdout(log):
    print log


class RevereIP:

    def __init__(self, args, key, recheck):
        self.domains = [0]
        self.domain_numbers = 0
        self.final_result = {}
        self.api_key = key
        self.count = 0
        self.log = stdout
        self.recheck = recheck
        self.http = "http://"
        self.https = "https://"
        self.mainFile = open("bing.txt",'a')
        self.mainFileRead = open("newListOfIP.txt", 'r').read().split('\n')
        self.mainFileRead.pop()
        self.results = [0]*len(self.mainFileRead)

        # self.convertDomainToIP('abc.txt')


    def run(self):

        self.file_opener()

        while self.results:
            self.domain_numbers = 0
            ip_or_domain = self.results.pop()
            host_name = self.mainFileRead.pop()
            self.mainFile.write(host_name+","+str(ip_or_domain)+",")
            self.reverse_ip(ip_or_domain)
            self.log("[*] You got " + str(self.domain_numbers) + " domains to hack.")
            if self.domain_numbers>0:
                self.mainFile.write(str(self.domain_numbers) + ",")
                # list(map(str, self.domains))
                for i in range(1, len(self.domains)):
                    self.mainFile.write(self.domains[i][1]+" + ")
                self.mainFile.write("\n")
            else:
                self.mainFile.write(str(self.domain_numbers) + "\n")
            # self.mainFile.write(str(self.domain_numbers) + ","+ str(self.domains)+"\n")


            self.domains = []

        self.mainFile.close()

    def file_opener(self):
        k=0
        try:
            file = open("newListOfIP.txt", "r")
            for i in file:
                i = i.replace('\n','')
                self.results[k] = socket.gethostbyname(i)
                k+=1
            return  self.results
        except IOError:
            self.log("[-] Error: File does not appear to exist.")
            exit(1)

    def convertDomainToIP(self, file):
            fileHandler = open(file, "r").read()
            fileHandler2 = open("abc3.txt", 'a+')
            temp = str.split(fileHandler,'\n')
            for i in temp:
                fileHandler2.write(i+','+socket.gethostbyname(i)+'\n')


    def reverse_ip(self, ip_or_domain):
        raw_domains_temp = []
        ip = ip_or_domain

        query = "IP:" + str(ip)
        self.log("\n[*] Host: " + str(ip))

        self.count = 0
        while 1:
            raw_domains = self.bing_call_api(query)
            if raw_domains == raw_domains_temp:
                break
            raw_domains_temp = raw_domains
            if raw_domains == -1:
                break
            self.count += 100
            if self.recheck:
                self.check_domain_name_in_ip(raw_domains, ip)
            else:
                for l in raw_domains:
                    if l[1] not in self.domains:
                        self.log("[+] " + ''.join(l).encode('utf8'))
                        self.domains.append(l)
                self.domain_numbers = len(self.domains)

    def bing_call_api(self, query):
        domains = []
        query = urllib.quote(query)
        user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
        credentials = (':%s' % self.api_key).encode('base64')[:-1]
        auth = 'Basic %s' % credentials
        url = 'https://api.cognitive.microsoft.com/bing/v5.0/search?q='+query+'&responseFilter=webpages'
        request = urllib2.Request(url)
        request.add_header('Authorization', auth)
        request.add_header('Host', 'api.cognitive.microsoft.com')
        request.add_header('Ocp-Apim-Subscription-Key', 'a7a778df2bc446a2880ff46173339d02')
        request.add_header('User-Agent', user_agent)
        request_opener = urllib2.build_opener()
        try:
            response = request_opener.open(request)
        except urllib2.HTTPError, e:
            if e.code == 401:
                self.log('[-] Wrong API Key or not sign up to use Bing Search API')
                self.log("""
    you need to..
    1.register or use microsoft account for get Bing API key -> https://datamarket.azure.com/
    2.choose free plan 5,000 Transactions/month -> https://datamarket.azure.com/dataset/bing/search
            """)
                exit(1)
            self.log("[-] Connection problem!!, Cannot connect to Bing API")
            exit(1)

        response_data = response.read()
        json_result = json.loads(response_data)
        result_list = json_result
        if not 'webPages' in result_list:
            return -1

        for i in range(len(result_list['webPages']['value'])):
            protocol_domain_port = []
            domain = result_list['webPages']['value'][i]['displayUrl']
            if self.https in domain:
                protocol_domain_port.append("https://")
                port = ':443'
            else:
                protocol_domain_port.append("http://")
                port = ':80'
            domain = domain.replace("http://", "").replace("https://", "")
            rest = domain.split('/', 1)[0]
            if ':' in rest:
                port = rest.split(':', 1)[1]
                rest = rest.split(':', 1)[0]
                port = ':' + port
            protocol_domain_port.append(rest)
            protocol_domain_port.append(port)
            domains.append(protocol_domain_port)
        raw_domains = list()
        map(lambda x: not x in raw_domains and raw_domains.append(x), domains)
        return raw_domains

    def check_domain_name_in_ip(self, raw_domains, ip):
        for l in raw_domains:
            if l[1] in self.domains:
                continue
            try:
                ipc = socket.gethostbyname(l[1].encode("idna"))
            except:
                self.log("[!] " + ''.join(l).encode(
                    'utf8') + " Cannot recheck bacause of hostname encoded, Please recheck it by hand.")
                continue
            if ipc == ip:
                self.log("[+] " + ''.join(l).encode('utf8'))

            else:
                self.log("[!] " + ''.join(l).encode('utf8') + " is on the other IP address, please recheck it by hand.")
                continue
            self.domains.append(l)
        self.final_result.update({ip: self.domains})
        self.domain_numbers = len(self.domains)

    def check_ip_in_cloudflare(self, ip):
        cloudflare_ips = ['199.27.128.0/21', '173.245.48.0/20', '103.21.244.0/22', '103.22.200.0/22', '103.31.4.0/22',
                          '141.101.64.0/18', '108.162.192.0/18', '190.93.240.0/20', '188.114.96.0/20',
                          '197.234.240.0/22', '198.41.128.0/17', '162.158.0.0/15', '104.16.0.0/12']
        ipaddr = int(''.join(['%02x' % int(x) for x in ip.split('.')]), 16)
        for net in cloudflare_ips:
            netstr, bits = net.split('/')
            netaddr = int(''.join(['%02x' % int(x) for x in netstr.split('.')]), 16)
            mask = (0xffffffff << (32 - int(bits))) & 0xffffffff
            if (ipaddr & mask) == (netaddr & mask):
                return True
        return False


if __name__ == "__main__":
    main()
