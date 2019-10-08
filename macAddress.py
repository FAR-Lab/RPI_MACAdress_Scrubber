### WARNING use this script with caution. In the right configuration it could go through the network trying to turn off all avalible Raspberry pis

fileName = "./addresses.csv"
header =['mac','IxE']
raspberryPiName="Raspberry Pi Foundation"
username = "pi"
pw = "raspberry"
turnOffAfterRetrieved = True

import re
import csv
import nmap
from pathlib import Path
from pexpect import pxssh



#nm[nm.all_hosts()[0]]['addresses']['mac']
#nm.scan(hosts='192.168.2.*', ports=None, arguments='-n -e bridge100 -sP ', sudo=True)

def sudo(s,password):
    rootprompt = re.compile('.*[$#]')
    s.sendline('sudo -s')
    i = s.expect([rootprompt,'assword.*: '])
    if i==0:
        print("didnt need password!")
        pass
    elif i==1:
        print("sending password")
        s.sendline(password)
        j = s.expect([rootprompt,'Sorry, try again'])
        if j == 0:
            pass
        elif j == 1:
            raise Exception("bad password")
    else:
        raise Exception("unexpected output")
    s.set_unique_promp

def main():
    highestIXEID=100
    OutDictionary={}
    my_file = Path(fileName)
    if my_file.is_file():
        readingFile= open(fileName, mode='r')
        reader = csv.reader(readingFile)
        firstRow=True
        for row in reader:
            k, id = row
            OutDictionary[k] = id
            if not firstRow and (int(id)>highestIXEID):
                highestIXEID=int(id)
                print(highestIXEID)
            firstRow=False

    else:
        writingFile= open(fileName, mode='w+')
        writer = csv.DictWriter(writingFile, fieldnames = header)
        writer.writeheader()
    print("Highest Number was",highestIXEID)
    nm = nmap.PortScanner()
    writingFile= open(fileName, mode='a')
    writer = csv.DictWriter(writingFile, fieldnames = header)
    nm.scan(hosts='192.168.0.*', ports=None, arguments='-n -e en0 -sP ', sudo=True) ##These should probably become cmd line parameters
    for host in nm.all_hosts():
        en0Mac = nm[host]['addresses']['mac']
        vendor = nm[host]['vendor'][en0Mac]
        s = pxssh.pxssh()
        if vendor == raspberryPiName:
            var = s.login(host,username,pw)
            if not var:
                print("Error I thought I found a Pi but I can't login... Maybe its not in mint condition at ip: " +host)
                continue
            s.sendline('cat /sys/class/net/wlan0/address')
            s.prompt()
            mac = s.before.decode("utf-8").split('\r\n')[1]
            if mac in OutDictionary:
                print("nothing new to see here")
            else:
                #sudo(s,pw)
                highestIXEID+=1
                s.sendline('sudo sed -i -r \'s/ixe00/{}/\'  /etc/hostname'.format('ixe'+str(highestIXEID)))
                s.sendline('sudo sed -i -r \'s/ixe00/{}/\'  /etc/hosts'.format('ixe'+str(highestIXEID)))
                output=[]
                row_dictionary_temp={}
                row_dictionary_temp[header[0]] = mac
                row_dictionary_temp[header[1]] = highestIXEID
                output.append(row_dictionary_temp.copy())
                writer.writerows(output)
                print("Added new MAC Address Pi is shutting down")

            if turnOffAfterRetrieved:
                s.sendline('sudo shutdown -h now')
                print(s.before)
            s.logout()


if __name__ == '__main__':
    main()
