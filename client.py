#!/usr/bin/python

from tkinter import *
import socket as sk
from tkinter import messagebox as mx
import netifaces
import sqlite3, csv
import os


class Client:

	def __init__(self, master):
		self.master = master
		self.mac = StringVar()
		self.ip = StringVar()

		self.ls = []
		self.db_name = 'sysinfo.db'

		self.ip.set(self.getip())
		self.mac.set(self.getmac())

		self.iplabel1 = Label(self.master, text="IP Address", bd=5, justify='left').place(x=50, y=80)
		self.iplabel2 = Label(self.master, textvariable=self.ip, bd=5, justify='left').place(x=200, y=80)
		self.maclabl1 = Label(self.master, text="MAC Address", bd=5, justify='left').place(x=50, y=150)
		self.maclabl2 = Label(self.master, textvariable=self.mac, bd=5, justify='left').place(x=200, y=150)
		self.inputlabel = Label(self.master, text="Enter 3 Digit Number", bd=5, justify='left').place(x=50, y=210)
		self.userinput = Entry(self.master, bd=5)
		self.userinput.place(x=200, y=210)
		self.subbutton = Button(self.master, text="Submit", bd=5, activeforeground='green', command=self.validate).place(x=150, y=280)

	def getip(self):
		hostname = sk.gethostname()
		self.ls.append(sk.gethostbyname(hostname + ".local"))
		return self.ls[0]

	def getmac(self):
		self.ls.append(netifaces.ifaddresses(netifaces.interfaces()[1])[netifaces.AF_LINK][0]['addr'])
		return self.ls[1]

	def validate(self):

		temp = self.userinput.get()

		if(temp.isdigit() and len(str(temp))==3):
			self.ls.append(temp)
			del temp
			self.transaction()

		else:
			mx.showinfo("Error","3 Digit Number only Allowed")
			self.userinput.delete(0,'end')

	def transaction(self):

		if os.path.isfile(self.db_name):
			conn = sqlite3.connect(self.db_name)

			cur = conn.cursor()
			cur.execute("SELECT * from systable  MAC = ?", (self.ls[1],))

			def close_ack(b):
				self.ls.pop()
				conn.commit()
				conn.close()
				if (b):
					mx.showinfo("Message", "Updated Successfully")
					self.export()
				else:
					mx.showinfo("Message", "Inserted Successfully")
					self.export()
			
			if(cur.fetchone()):
				cur.execute("UPDATE systable SET IP = ?, DIGIT = ? WHERE MAC = ?", (self.ls[0], self.ls[2], self.ls[1]))
				close_ack(True)

			else:
				cur.execute("INSERT INTO systable (IP,MAC,DIGIT) VALUES(?,?,?)", tuple(self.ls))
				close_ack(False)		
		else:
			mx.showinfo("","Database notfound")

	def export(self):

		if os.path.isfile(self.db_name):
			conn = sqlite3.connect(self.db_name)
			cur = conn.cursor()
			cur.execute("SELECT MAC,IP,DIGIT FROM systable")

			with open("data.csv", 'w') as csv_file:
				csv_var = csv.writer(csv_file, delimiter=',')
				csv_var.writerow([i[0] for i in cur.description])
				csv_var.writerows(cur)
			conn.close()
		else:
			mx.showinfo("", "DB Not Found")

def main():
	root = Tk()
	root.title("System Info")
	root.config(height = 480, width = 400)
	root.resizable(False, False)

	app = Client(root)
	root.mainloop()


if __name__ == '__main__':
	main()