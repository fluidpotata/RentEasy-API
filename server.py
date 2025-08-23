from flask import render_template, request, redirect, url_for, flash, session, Blueprint

from database import *

server2 = Blueprint("server2", __name__, url_prefix="/")


@server2.route('/')
def index():
    return render_template('index.html')

@server2.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        adminStat = isAdmin(username, password)
        userStat = isAuthenticated(username, password)
        if adminStat:
            session['user'] = username
            session['role'] = 'admin'
            session['id'] = adminStat
            return redirect(url_for('server2.admin'))
        elif userStat:
            session['user'] = username
            session['role'] = 'user'
            session['id'] = userStat
            return redirect(url_for('server2.customer'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


@server2.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        if 'username' in session:
            if isAdmin(session['username']):
                return redirect(url_for('server2.admin'))
            return redirect(url_for('server2.dashboard'))
        else:
            return render_template('signup.html')
    elif request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        phone = request.form['phone']
        password = request.form['password']
        cpassword = request.form['confirm_password']
        room = request.form['room_type']
        if password != cpassword:
            return render_template('signup.html', error="Password doesn't match")   
        if ifUserExists(username):
            return render_template('signup.html', error="Username taken! Try another username.")
        joinReq(name, room, phone, username, password)
        return redirect(url_for('server2.login'))


@server2.route('/admin')
def admin():
    flash = session.get('flash')
    session['flash'] = None
    return render_template('admin.html', data={'tickets':getTickets(), 'count':getCountTickets(), 'flash': flash, 'joinreqs':getJoinReqsCount(), 'rent':getRentCount(), 'internet':getInternetCount(), 'utility':getUtilityCount()})


@server2.route('/customer')
def customer():
    userID = session['id']
    data = {'username': session['user'],'package':getPackage(userID),'bill': getBillStatus(userID),'internetbill':getInternetBillStatus(userID), 'utilitybill': getUtilityBillStatus(userID), 'ticketCount':getTicketCount(userID)}
    return render_template('customer.html', data=data)


@server2.route('/ticket', methods=['GET', 'POST'])
def ticket():
    if session['user']=='admin':
        return redirect(url_for('server2.ticketadmin'))
    if request.method == 'GET':
        return render_template('ticket.html', info=getTicketUser(session.get('user')))
    
    if request.method == 'POST':
        category = request.form['category']
        description = request.form['description']
        createTicket(getUserID(session.get('user')), category, description)
        return redirect(url_for('server2.ticket'))


@server2.route('/seeapps', methods=['GET', 'POST'])
def seeserver2s():
    if session['role']=='admin':
        if request.method == 'POST':
            req_id = request.form['req_id']
            room_id = request.form['room_id']
            name = request.form['name']
            phone = request.form['phone']
            username = request.form['username']
            password = request.form['password']
            allocateUser(username, password, req_id, phone, room_id, name)
            return redirect(url_for('server2.seeapps'))
        else:
            data = getJoinReqs()
            available_rooms = getAvailableRooms()
            return render_template('applications.html', data=data, available_rooms=available_rooms)
    else:
        return redirect(url_for('server2.customer'))


@server2.route('/ticketadmin', methods=['GET', 'POST'])
def ticketadmin():
    if session['user']=='admin':
        if request.method == 'POST':
            reportID = request.form['ticket_id']
            closeTicket(reportID)
            return redirect(url_for('server2.ticketadmin'))
        else:
            info = getTickets()
            return render_template('ticketadmin.html', tickets=info)
    else:
        return redirect(url_for('server2.ticket'))



@server2.route('/generatebill')
def generatebill():
    generateBill()
    return redirect(url_for('server2.admin'))


@server2.route('/paybill', methods=['GET', 'POST'])
def paybill():
    if request.method == 'POST':
        tenantid = request.form['tenantid']
        bill = request.form['bill']
        tid = request.form['tID']
        payBill(tenantid, bill, tid)
        return redirect(url_for('server2.paybill'))
    else:
        return render_template('billpay.html', data=getBills(session.get('id')))



@server2.route('/rooms', methods=['GET', 'POST'])
def rooms():
    if request.method == 'GET':
        return render_template('addroom.html')
    elif request.method == 'POST':
        roomName = request.form['roomName']
        roomtype = request.form['roomType']
        addRoom(roomtype, roomName)
        return redirect(url_for('server2.rooms'))


@server2.route('/tenants', methods=['GET', 'POST'])
def tenants():
    if request.method == 'POST':
        tenantid = request.form['tenantid']
        option = request.form['option']
        val = float(request.form['val'])
        updateTenant(tenantid,option, val)
        return redirect(url_for('server2.tenants'))
    elif request.method == 'GET':
        return render_template('tenants.html', tenants=getAllTenants())


@server2.route('/seebills/<string:billtype>')
def seebills(billtype):
    data = getUnpaidBills(billtype)
    return render_template('seeUnpaidBills.html', bills=data, getTenantName=getTenantName)


@server2.route('/unverifiedbills', methods=['GET', 'POST'])
def unverifiedbills():
    if request.method == 'POST':
        paymentid = request.form['paymentid']
        verifyBill(paymentid)
        return redirect(url_for('server2.unverifiedbills'))
    else:
        return render_template('verifybills.html', bills=getUnverifiedBills(), getTenantName=getTenantName)


@server2.route('/updateroom', methods=['GET', 'POST'])
def updateroom():
    if request.method == 'POST':
        tenantid = request.form['tenantid']
        roomid = request.form['roomid']
        updatePackage(tenantid, roomid)
        return redirect(url_for('server2.updateroom'))
    else:
        return render_template('updateroom.html', tenants=getAllTenants(), rooms=getAvailableRooms())


@server2.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('server2.index'))


if __name__ == '__main__':
    server2.run(debug=True)
