# server1.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)
from database import *
import json

server1 = Blueprint("server1", __name__, url_prefix="/api/v1")


@server1.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    adminStat = isAdmin(username, password)
    userStat = isAuthenticated(username, password)

    if adminStat:
        token = create_access_token(
            identity=json.dumps({"username": username, "role": "admin", "id": adminStat})
        )
        return jsonify({"message": "Login successful", "access_token": token, "role": "admin"})
    elif userStat:
        token = create_access_token(
            identity=json.dumps({"username": username, "role": "user", "id": userStat})
        )
        return jsonify({"message": "Login successful", "access_token": token, "role": "user"})
    else:
        return jsonify({"error": "Invalid username or password"}), 401



@server1.route("/signup", methods=["POST"])
def signup():
    data = request.json
    name = data.get("name")
    username = data.get("username")
    phone = data.get("phone")
    password = data.get("password")
    cpassword = data.get("confirm_password")
    room = data.get("room_type")

    if password != cpassword:
        return jsonify({"error": "Password doesn't match"}), 400
    if ifUserExists(username):
        return jsonify({"error": "Username taken! Try another username."}), 400

    joinReq(name, room, phone, username, password)
    return jsonify({"message": "Signup successful"})


def get_user():
    return json.loads(get_jwt_identity())


@server1.route("/admin")
@jwt_required()
def admin():
    user = get_user()
    if user["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = {
        "count": getCountTickets(),
        "joinreqs": getJoinReqsCount(),
        "rent": getRentCount(),
        "internet": getInternetCount(),
        "utility": getUtilityCount(),
    }
    return jsonify(data)


@server1.route("/customer")
@jwt_required()
def customer():
    user = get_user()
    if user["role"] != "user":
        return jsonify({"error": "Unauthorized"}), 403

    userID = user["id"]
    data = {
        "username": user["username"],
        "package": getPackage(userID),
        "bill": getBillStatus(userID),
        "internetbill": getInternetBillStatus(userID),
        "utilitybill": getUtilityBillStatus(userID),
        "ticketCount": getTicketCount(userID),
    }
    return jsonify(data)


@server1.route("/ticket", methods=["GET", "POST"])
@jwt_required()
def ticket():
    user = get_user()

    if user["role"] == "admin":
        return jsonify({"redirect": "/api/v1/ticketadmin"})

    if request.method == "GET":
        return jsonify({"tickets": getTicketUser(user["username"])})

    if request.method == "POST":
        data = request.json
        category = data.get("category")
        description = data.get("description")
        createTicket(getUserID(user["username"]), category, description)
        return jsonify({"message": "Ticket created"})


@server1.route("/seeapps", methods=["GET", "POST"])
@jwt_required()
def seeApps():
    user = get_user()
    if user["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == "POST":
        data = request.json
        allocateUser(
            data.get("username"),
            data.get("password"),
            data.get("req_id"),
            data.get("phone"),
            data.get("room_id"),
            data.get("name"),
        )
        return jsonify({"message": "User allocated"})
    else:
        return jsonify({"requests": getJoinReqs(), "available_rooms": getAvailableRooms()})


@server1.route("/ticketadmin", methods=["GET", "POST"])
@jwt_required()
def ticketadmin():
    user = get_user()
    if user["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == "POST":
        data = request.json
        closeTicket(data.get("ticket_id"))
        return jsonify({"message": "Ticket closed"})
    else:
        return jsonify({"tickets": getTickets()})


@server1.route("/generatebill")
@jwt_required()
def generatebill():
    user = get_user()
    if user["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    generateBill()
    return jsonify({"message": "Bills generated"})


@server1.route("/paybill", methods=["GET", "POST"])
@jwt_required()
def paybill():
    user = get_user()

    if request.method == "POST":
        data = request.json
        payBill(data.get("tenantid"), data.get("bill"), data.get("tID"))
        return jsonify({"message": "Bill paid"})
    else:
        return jsonify({"bills": getBills(user["id"])})


@server1.route("/rooms", methods=["GET", "POST"])
@jwt_required()
def rooms():
    if request.method == "GET":
        return jsonify({"rooms": getAvailableRooms()})
    else:
        data = request.json
        addRoom(data.get("roomType"), data.get("roomName"))
        return jsonify({"message": "Room added"})


@server1.route("/tenants", methods=["GET", "POST"])
@jwt_required()
def tenants():
    if request.method == "POST":
        data = request.json
        updateTenant(data.get("tenantid"), data.get("option"), float(data.get("val")))
        return jsonify({"message": "Tenant updated"})
    else:
        return jsonify({"tenants": getAllTenants()})


@server1.route("/seebills/<string:billtype>")
@jwt_required()
def seebills(billtype):
    return jsonify({"bills": getUnpaidBills(billtype)})


@server1.route("/unverifiedbills", methods=["GET", "POST"])
@jwt_required()
def unverifiedbills():
    user = get_user()
    if user["role"] != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == "POST":
        data = request.json
        verifyBill(data.get("paymentid"))
        return jsonify({"message": "Bill verified"})
    else:
        return jsonify({"bills": getUnverifiedBills()})


@server1.route("/updateroom", methods=["GET","POST"])
@jwt_required()
def updateroom():
    if request.method == 'POST':
        data = request.json
        updatePackage(data.get("tenantid"), data.get("roomid"))
        return jsonify({"message": "Room updated"})
    else:
        return jsonify({"tenants":getAllTenants(), "rooms":getAvailableRooms()})


