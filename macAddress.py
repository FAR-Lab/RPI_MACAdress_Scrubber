### WARNING use this script with caution. In the right configuration it could go through the network trying to turn off all avalible Raspberry pis

fileName = "./addresses.csv"
header =['mac','vendor']
raspberryPiName="Raspberry Pi Foundation"
username = "pi"
pw = "raspberry"
turnOffAfterRetrieved = True


import csv
import nmap
from pathlib import Path
from pexpect import pxssh



#nm[nm.all_hosts()[0]]['addresses']['mac']
#nm.scan(hosts='192.168.2.*', ports=None, arguments='-n -e bridge100 -sP ', sudo=True)


def main():
    d={}
    my_file = Path(fileName)
    if my_file.is_file():
        readingFile= open(fileName, mode='r')
        reader = csv.reader(readingFile)
        for row in reader:
            k, v = row
            d[k] = v
    else:
        writingFile= open(fileName, mode='w+')
        writer = csv.DictWriter(writingFile, fieldnames = header)
        writer.writeheader()

    nm = nmap.PortScanner()
    writingFile= open(fileName, mode='a')
    writer = csv.DictWriter(writingFile, fieldnames = header)
    nm.scan(hosts='192.168.2.*', ports=None, arguments='-n -e bridge100 -sP ', sudo=True) ##These should probably become cmd line parameters
    s = pxssh.pxssh()
    for host in nm.all_hosts():
        en0Mac = nm[host]['addresses']['mac']
        vendor = nm[host]['vendor'][en0Mac]
        if vendor == raspberryPiName:
            var = s.login(host,username,pw)
            if not var:
                print("Error I thought I found a Pi but I can't login... Maybe its not in mint condition at ip" +host)
                continue
            s.sendline('cat /sys/class/net/wlan0/address')
            s.prompt()
            mac = s.before.decode("utf-8").split('\r\n')[1]
            if turnOffAfterRetrieved:
                s.sendline('sudo shutdown -h now')
                print(s.before)
            s.logout()
            if mac in d:
                print("nothing new to see here")
            else:
                output=[]
                row_dictionary_temp={}
                row_dictionary_temp[header[0]] = mac
                row_dictionary_temp[header[1]] = vendor
                output.append(row_dictionary_temp.copy())
                writer.writerows(output)
                print("Added new MAC Address Pi is shutting down")



if __name__ == '__main__':
    main()
