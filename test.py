import random


class X:
    def __init__(self):
        self.last_ticket = 0
        self.tickets = []
    
    def add_tickets(self, amount):
        new_last_ticket = self.last_ticket+amount
        self.tickets += range(self.last_ticket, new_last_ticket)
        self.last_ticket = new_last_ticket

x = X()
x.add_tickets(10)
print(x.tickets)
print(x.last_ticket)
print()
x.add_tickets(5)
print(x.tickets)
print(len(x.tickets))
print(x.last_ticket)

win = 0
for i in range(2000):
    if random.randint(0,x.last_ticket) == 14:
        win += 1

print(win)
print((win/2000)*100)