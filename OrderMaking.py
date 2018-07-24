#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

class MarkingPositionMonitor:
    def __init__(self):
        #self.D["ID"] = [q in hand, q needed, order status, cancel status, symbol]
        #order status: 0: set, 1:ack, 2:reject
        #cancel status: 0: none, 1:ack, 2:reject, 3:asking cancel
        self.D = {}
        self.currSym = ""
        
    
    def on_event(self, message):
        data = json.loads(message)
        TYPE = data['type']
        ID = data['order_id']
        if TYPE == 'NEW':
            self.currSym = data['symbol']
            self.placeOrder(data, ID)
        elif TYPE == 'FILL':
            self.fill(data, ID)
        elif TYPE == 'ORDER_ACK':
            self.order_ack(data, ID)
        elif TYPE == 'ORDER_REJECT':
            self.order_reject(data, ID)
        elif TYPE == 'CANCEL':
            self.cancel(data, ID)
        elif TYPE == 'CANCEL_ACK':
            self.cancel_ack(data, ID)
        elif TYPE == 'CANCEL_REJECT':
            self.cancel_reject(data, ID)
        symbol = self.D[ID][-1]
        result = 0
        for key in self.D.keys():
            if self.D[key][-1] == symbol:
                result += self.D[key][0]
        #print("###Holding:",result)
        return result
            
    def placeOrder(self, data, ID):
        #print("placeOrder  ",end=" ")
        side = data['side']
        quantity = data['quantity']
        if side == 'BUY':
            self.D[ID] = [0, quantity, 0, 0, self.currSym]
        elif side == 'SELL':
            self.D[ID] = [-quantity, -quantity, 0, 0, self.currSym]
        
    def fill(self, data, ID):
        #print("fill        ",end=" ")
        #if ID not in self.D.keys():
        #    print("warning: ORDER ID not exist")
        
        #Check Order Status
        #if self.D[ID][2] != 1:
        #    print("order not yet ack",end=" ")
        #Check Cancel Status
        #if self.D[ID][3] in [1,2,3]:
        #    print("order has been cencelled",end=" ")
            
        filled = data["filled_quantity"]
        remaining = data["remaining_quantity"]
        if filled+remaining != abs(self.D[ID][1]):
            print("warning: filled and remaining not match order",end=" ")
        else:
            if self.D[ID][1] < 0: #sell order
                self.D[ID][1] += filled
            else: #buy order
                self.D[ID][1] -= filled
                self.D[ID][0] += filled
    
    def order_ack(self, data, ID):
        #print("order ack   ",end=" ")
        #if ID not in self.D.keys():
        #    print("warning: ORDER ID not exist",end=" ")            
        #Check Order Status
        #if self.D[ID][2] != 0:
        #    print("order status is not set, order status:", self.D[ID][2],end=" ")
        #Check Cancel Status
        #if self.D[ID][3] == 1:
        #    print("order has been cencelled",end=" ")
        self.D[ID][2] = 1
        
    def order_reject(self, data, ID):
        #print("order reject",end=" ")
        #if ID not in self.D.keys():
        #    print("warning: ORDER ID not exist",end=" ")
        #Check Order Status
        #if self.D[ID][2] != 0:
        #    print("order status is not set, order status:", self.D[ID][2],end=" ")
        #Check Cancel Status
        #if self.D[ID][3] == 1:
        #    print("order has been cencelled",end=" ")
        #reset the order
        symbol = self.D[ID][-1] 
        self.D[ID] = [0, 0, 2, 0, symbol]
            
    def cancel(self, data, ID):
        #print("cancel      ",end=" ")
        #if ID not in self.D.keys():
        #    print("warning: ORDER ID not exist",end=" ")
        #Check Order Status
        #if self.D[ID][2] != 1:
        #    print("order status is not ack, order status:", self.D[ID][2],end=" ")
        #Check Cancel Status
        #if self.D[ID][3] != 0:
        #    print("cancel status should be NONE before cancel, cancel status", self.D[ID][3],end=" ")
        self.D[ID][3] = 3
            
    def cancel_ack(self, data, ID):
        #print("cancel ack  ",end=" ")
        #if ID not in self.D.keys():
        #    print("warning: ORDER ID not exist",end=" ")
        #Check Order Status
        #if self.D[ID][2] != 1:
        #    print("order status is not ack, order status:", self.D[ID][2],end=" ")
        #Check Cancel Status
        #if self.D[ID][3] != 3:
        #    print("cancel status should be waiting before ack, cancel status", self.D[ID][3],end=" ")
        self.D[ID][3] = 1
        #process the order
        if self.D[ID][1] < 0: #sell order
            self.D[ID][0] += abs(self.D[ID][1])
            self.D[ID][1] = 0
        else: #buy order
            self.D[ID][1] = 0
            
    def cancel_reject(self, data, ID):
        #print("cancel rejec",end=" ")
        #if ID not in self.D.keys():
        #    print("warning: ORDER ID not exist",end=" ")
        #Check Order Status
        #if self.D[ID][2] != 1:
        #    print("order status is not ack, order status:", self.D[ID][2],end=" ")
        #Check Cancel Status
        #if self.D[ID][3] != 3:
        #    print("cancel status should be waiting before ack, cancel status", self.D[ID][3],end=" ")
        self.D[ID][3] = 2
        
        
        
        
with open('input.json', 'r+') as f:
    line = f.readlines()

m = MarkingPositionMonitor()
for l in line:
    print(m.on_event(l))