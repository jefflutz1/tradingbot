from robinhood_crypto_api import RobinhoodCrypto
import getpass
import time
import pickle

def login():
    user, password = read_credentials_from_file('/home/pi/pass.txt')
    return RobinhoodCrypto(user,password)

def read_credentials_from_file(file_name):
    username, password = [x.strip() for x in open(file_name).readlines()]
    return username, password

class Account:
    startAmount = 10000
    firstBTCPrice = 0
    currentAmount = startAmount
    priceHistory = []
    r = ''
    buyFlag = True
    numberOfTrades = 0
    gain = 1
    lastBuy = 0

    def __init__(self, intervalAverage,buyThreshhold,sellThreshhold):
        self.intervalAverage = intervalAverage
        self.buyThreshhold = buyThreshhold
        self.sellThreshhold = sellThreshhold
        
    def read_credentials():
        username = input("Username: ")
        password = getpass.getpass()
        return username, password


    def read_credentials_from_file(file_name):
        username, password = [x.strip() for x in open(file_name).readlines()]
        return username, password
            
    def printOutput(self,printType, percentChange, price, BTCChange, gain = 0.00):
        
        localtime = time.asctime( time.localtime(time.time()))
        
        print (str(localtime) + ' ' + printType + ' ' + str(format(percentChange, '.2f')) + ' price: ' + str(format(price, '.2f')) 
            + ' BTC: ' + str(format(BTCChange, '.3f')) + ' gain: ' + str(format(gain, '.3f')) + ' nOt: ' + str(self.numberOfTrades))
              
    def priceChange(self):
        
        change = 0
        
        for i in range(self.intervalAverage):
            change += float(self.priceHistory[len(self.priceHistory)-2-i])
        
        return change / self.intervalAverage
    
    def threshholdTest(self, recentPrice):
        self.priceHistory.append(recentPrice)
        
        if(len(self.priceHistory) == 1):
            self.firstBTCPrice = float(self.priceHistory[0])        
        
        if(len(self.priceHistory) < self.intervalAverage):
            return 
        
        price = float(self.priceHistory[len(self.priceHistory) - 1])
        percentChange = price / Account.priceChange(self)
        #BTCChange = price / self.firstBTCPrice
        
        if len(self.priceHistory) > self.intervalAverage and percentChange > (1 + self.buyThreshhold) and self.buyFlag:
            self.lastBuy = price
            self.buyFlag = False
            self.numberOfTrades += 1
            #Account.printOutput(self,'buy',percentChange, price, BTCChange, self.gain)
        
        elif len(self.priceHistory) > self.intervalAverage and percentChange < (1 - self.sellThreshhold) and not self.buyFlag:
            self.currentAmount *= price / self.lastBuy
            self.gain = self.currentAmount / self.startAmount
            self.buyFlag = True
            self.numberOfTrades += 1
            #Account.printOutput(self,'sell',percentChange, price, BTCChange, self.gain)
        
        elif not self.buyFlag:
            #Account.printOutput(self,'holding',percentChange, price, BTCChange, self.gain)
            pass
            
        else:
           #Account.printOutput(self,'not holding',percentChange, price, BTCChange, self.gain)
           pass

def writeToFile(data):
    with open('simuldata.txt', 'wb') as fh:
        pickle.dump(data, fh)
        
def readFile(filename):
    pickle_off = open (filename, "rb")
    return pickle.load(pickle_off)

r = login()

try:
    simulationList = readFile('simuldata.txt')
except:
    simulationList = []
    
    for i in range(1,11):
        for j in range(1,111):
            for k in range(1,111):
                simulationList.append(Account(i,j/10000,k/10000))
          
count = 0
while(True):
    for i in range(len(simulationList)):
        tempPrice = r.quotes()['ask_price']
        simulationList[i].threshholdTest(tempPrice)
        writeToFile(simulationList)
        print(str(count) + " " + str(tempPrice) + " gain " + str(simulationList[0].gain))
        count += 1
        time.sleep(15)

