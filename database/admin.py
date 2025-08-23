import sqlite3
import os
from time import strftime


def dbConnect():
    # return sqlite3.connect(os.getenv('DATABASE'))
    return sqlite3.connect('database/main.db')   

def pushToDB(query):
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    connection.close()


def pullFromDB(query):
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    connection.close()
    return result


def getTickets():
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(f"SELECT Tickets.*, Tenants.name FROM Tickets JOIN Tenants ON Tickets.tenantID = Tenants.tenantID ORDER BY status DESC")
    result = cursor.fetchall()
    connection.close()
    return result

def getCountTickets():
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM Tickets")
    result = cursor.fetchall()
    connection.close()
    return result


def closeTicket(ticketID):
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(f"UPDATE Tickets SET status='Closed' WHERE reportID='{ticketID}'")
    connection.commit()
    connection.close()


def allocateUser(username, password, req_id, phone, room_id, name):
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO Users(username, password, role) VALUES('{username}', '{password}', 'user')")
    cursor.execute(f"SELECT userID FROM Users WHERE username='{username}'")
    userID = cursor.fetchone()[0]
    cursor.execute(f"INSERT INTO Tenants(name, phone, roomID, userID) VALUES('{name}', '{phone}', '{room_id}', '{userID}')")
    cursor.execute(f"UPDATE Rooms SET status='Occupied' WHERE roomID='{room_id}'")
    cursor.execute(f"DELETE FROM joinReqs WHERE requestID='{req_id}'")
    cursor.execute(f"SELECT type FROM Rooms WHERE roomID='{room_id}'")
    room_type = cursor.fetchone()[0]
    cursor.execute(f"SELECT what, amount FROM defaultBills WHERE type='{room_type}'")
    default_bills = cursor.fetchall()
    for bill in default_bills:
        cursor.execute(f"INSERT INTO Bills(userID, type, amount) VALUES('{userID}', '{bill[0]}', '{bill[1]}')")
    connection.commit()
    generateBill()
    connection.close()


def getJoinReqs():
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM joinReqs")
    result = cursor.fetchall()
    connection.close()
    return result


def getAvailableRooms():
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM Rooms WHERE status='Available'")
    result = cursor.fetchall()
    connection.close()
    return result


def generateBill():
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute("SELECT userID, tenantID FROM Tenants")
    tenant_ids = cursor.fetchall()
    
    for tenant_id in tenant_ids:
        cursor.execute(f"SELECT * FROM Bills WHERE userID='{tenant_id[0]}'")
        bills = cursor.fetchall()
        
        for bill in bills:
            cursor.execute(f"SELECT * FROM Payments WHERE tenantID='{tenant_id[1]}' AND month='{strftime('%Y-%m')}' AND payment='{bill[0]}'")
            existing_payment = cursor.fetchone()
            if not existing_payment:
                cursor.execute(f"INSERT INTO Payments(payment, tenantID, amount, month, status, transactionID, type) VALUES('{bill[0]}', '{tenant_id[1]}', '{bill[3]}', '{strftime('%Y-%m')}', 'unpaid', 'unpaid', '{bill[2]}')")
    
    connection.commit()
    connection.close()


def getAllTenants():
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Tenants")
    result = cursor.fetchall()
    connection.close()
    return result


def updateTenant(tebantid, option, value):
    connecton = dbConnect()
    cursor = connecton.cursor()
    cursor.execute(f"SELECT userID FROM Tenants WHERE tenantID='{tebantid}'")
    user_id = cursor.fetchone()[0]
    cursor.execute(f"UPDATE Bills SET amount='{value}' WHERE userID='{user_id}' AND type='{option}'")
    connecton.commit()
    connecton.close()


def addRoom(roomtype, roomname):
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO Rooms(type, roomName, status) VALUES('{roomtype}', '{roomname}', 'Available')")
    connection.commit()
    connection.close()


def getRentCount():
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Payments WHERE status='unpaid' AND type='rent'")
    result = cursor.fetchall()[0][0]
    connection.close()
    return result


def getInternetCount():
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Payments WHERE status='unpaid' AND type='internet'")
    result = cursor.fetchall()[0][0]
    connection.close()
    return result


def getUtilityCount():
    connection = dbConnect()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM Payments WHERE status='unpaid' AND type='utility'")
    result = cursor.fetchall()[0][0]
    connection.close()
    return result


def getUnpaidBills(type):
    result = pullFromDB(f"SELECT * FROM Payments WHERE (status='unpaid' OR status='unverified') AND type='{type}'")
    return result


def getUnverifiedBills():
    result = pullFromDB("SELECT * FROM Payments WHERE status='unverified'")
    return result

def verifyBill(paymentID):
    pushToDB(f"UPDATE Payments SET status='paid' WHERE paymentID='{paymentID}'")
    return

def getUnverifiedBills():
    result = pullFromDB("SELECT * FROM Payments WHERE status='unverified'")
    return result


def getFreeRooms():
    result = pullFromDB("SELECT * FROM Rooms WHERE status='Available'")
    return result