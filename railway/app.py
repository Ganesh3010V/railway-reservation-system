"""
Railway Reservation System – Flask Backend
-------------------------------------------
DBMS Mini Project
Submitted by: Ganesh | B.Tech AIML | UVCE Bangalore

Demonstrates: JOINs, Triggers, Stored Procedures, Foreign Keys,
              CHECK Constraints, Aggregates, Subqueries, GROUP BY
"""

from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error
from datetime import date, datetime
from decimal import Decimal
import json

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "railway_db",
}


# ── JSON encoder for date/Decimal (Flask 3.x compatible) ──────────────
from flask.json.provider import DefaultJSONProvider

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

app.json_provider_class = CustomJSONProvider
app.json = CustomJSONProvider(app)


# ── DB helpers ──────────────────────────────────────────────────────────
def get_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        # Fallback to secondary credentials if default fails
        if DB_CONFIG["password"] == "":
            try:
                fallback_config = dict(DB_CONFIG)
                fallback_config["password"] = "Ganesh@3018"
                return mysql.connector.connect(**fallback_config)
            except Error:
                pass
        raise e


def query(sql, params=None, fetch=True):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params or ())
        if fetch:
            result = cur.fetchall()
        else:
            result = {"affected_rows": cur.rowcount, "lastrowid": cur.lastrowid}
        conn.commit()
        return result
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def call_proc(name, args):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.callproc(name, args)
        results = []
        for r in cur.stored_results():
            results.extend(r.fetchall())
        conn.commit()
        return results
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


# ── Page ────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ── Dashboard ───────────────────────────────────────────────────────────
@app.route("/api/dashboard")
def dashboard():
    stats = {}
    stats["total_passengers"] = query("SELECT COUNT(*) AS c FROM Passenger")[0]["c"]
    stats["total_trains"]     = query("SELECT COUNT(*) AS c FROM Train")[0]["c"]
    stats["total_bookings"]   = query("SELECT COUNT(*) AS c FROM Booking")[0]["c"]
    stats["confirmed"]        = query("SELECT COUNT(*) AS c FROM Booking WHERE Status='Confirmed'")[0]["c"]
    stats["waitlisted"]       = query("SELECT COUNT(*) AS c FROM Booking WHERE Status='Waitlisted'")[0]["c"]
    stats["cancelled"]        = query("SELECT COUNT(*) AS c FROM Booking WHERE Status='Cancelled'")[0]["c"]
    stats["total_revenue"]    = query("SELECT COALESCE(SUM(Amount),0) AS t FROM Payment WHERE Status='Success'")[0]["t"]
    stats["total_stations"]   = query("SELECT COUNT(*) AS c FROM Station")[0]["c"]

    recent = query("""
        SELECT b.PNR, p.Name, t.TrainName, b.BoardingStation, b.ExitStation,
               b.Status, b.JourneyDate, b.BookingTime
        FROM Booking b
        JOIN Passenger p ON b.PassengerID = p.PassengerID
        JOIN Train t     ON b.TrainNo     = t.TrainNo
        ORDER BY b.BookingTime DESC LIMIT 5
    """)

    occupancy = query("""
        SELECT sc.ClassType, t.TrainName,
               sc.TotalSeats,
               SUM(CASE WHEN s.Status='Occupied'  THEN 1 ELSE 0 END) AS Occupied,
               SUM(CASE WHEN s.Status='Available' THEN 1 ELSE 0 END) AS Available
        FROM SeatClass sc
        JOIN Seat  s ON sc.ClassID = s.ClassID
        JOIN Train t ON sc.TrainNo = t.TrainNo
        GROUP BY sc.ClassID
    """)

    return jsonify({"stats": stats, "recent": recent, "occupancy": occupancy})


# ── Trains ──────────────────────────────────────────────────────────────
@app.route("/api/trains")
def get_trains():
    return jsonify(query("SELECT * FROM Train"))


@app.route("/api/trains", methods=["POST"])
def add_train():
    d = request.json
    try:
        query("INSERT INTO Train VALUES (%s,%s,%s,%s)",
              (d["TrainNo"], d["TrainName"], d["Source"], d["Destination"]), fetch=False)
        return jsonify({"success": True, "message": f"Train {d['TrainNo']} added"})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/api/trains/<int:tno>", methods=["DELETE"])
def delete_train(tno):
    try:
        query("DELETE FROM Train WHERE TrainNo=%s", (tno,), fetch=False)
        return jsonify({"success": True})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


# ── Stations ────────────────────────────────────────────────────────────
@app.route("/api/stations")
def get_stations():
    return jsonify(query("SELECT * FROM Station ORDER BY StationCode"))


@app.route("/api/stations", methods=["POST"])
def add_station():
    d = request.json
    try:
        query("INSERT INTO Station VALUES (%s,%s,%s)",
              (d["StationCode"], d["StationName"], d["City"]), fetch=False)
        return jsonify({"success": True, "message": f"Station {d['StationCode']} added"})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/api/stations/<code>", methods=["DELETE"])
def delete_station(code):
    try:
        query("DELETE FROM Station WHERE StationCode=%s", (code,), fetch=False)
        return jsonify({"success": True})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


# ── Routes ──────────────────────────────────────────────────────────────
@app.route("/api/routes/<int:tno>")
def get_route(tno):
    return jsonify(query("""
        SELECT rs.RouteID, rs.SeqNo, rs.StationCode,
               s.StationName, s.City, rs.DistanceFromOrigin
        FROM RouteStation rs
        JOIN Station s ON rs.StationCode = s.StationCode
        WHERE rs.TrainNo = %s ORDER BY rs.SeqNo
    """, (tno,)))


@app.route("/api/routes", methods=["POST"])
def add_route_station():
    d = request.json
    try:
        query("""INSERT INTO RouteStation (TrainNo,StationCode,SeqNo,DistanceFromOrigin)
                 VALUES (%s,%s,%s,%s)""",
              (d["TrainNo"], d["StationCode"], d["SeqNo"], d["DistanceFromOrigin"]), fetch=False)
        return jsonify({"success": True})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


# ── Seat Classes ────────────────────────────────────────────────────────
@app.route("/api/seat-classes/<int:tno>")
def get_seat_classes(tno):
    return jsonify(query("""
        SELECT sc.ClassID, sc.ClassType, sc.FarePerKm, sc.TotalSeats,
               SUM(CASE WHEN s.Status='Available' THEN 1 ELSE 0 END) AS Available,
               SUM(CASE WHEN s.Status='Occupied'  THEN 1 ELSE 0 END) AS Occupied
        FROM SeatClass sc LEFT JOIN Seat s ON sc.ClassID = s.ClassID
        WHERE sc.TrainNo = %s GROUP BY sc.ClassID
    """, (tno,)))


@app.route("/api/seat-classes", methods=["POST"])
def add_seat_class():
    d = request.json
    try:
        r = query("""INSERT INTO SeatClass (TrainNo,ClassType,FarePerKm,TotalSeats)
                     VALUES (%s,%s,%s,%s)""",
                  (d["TrainNo"], d["ClassType"], d["FarePerKm"], d["TotalSeats"]), fetch=False)
        return jsonify({"success": True, "classId": r["lastrowid"]})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


# ── Seats ───────────────────────────────────────────────────────────────
@app.route("/api/seats/<int:cid>")
def get_seats(cid):
    return jsonify(query("SELECT * FROM Seat WHERE ClassID=%s ORDER BY CoachNo,SeatNo", (cid,)))


@app.route("/api/seats", methods=["POST"])
def add_seat():
    d = request.json
    try:
        query("INSERT INTO Seat (ClassID,CoachNo,SeatNo) VALUES (%s,%s,%s)",
              (d["ClassID"], d["CoachNo"], d["SeatNo"]), fetch=False)
        return jsonify({"success": True})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


# ── Passengers ──────────────────────────────────────────────────────────
@app.route("/api/passengers")
def get_passengers():
    return jsonify(query("SELECT * FROM Passenger ORDER BY PassengerID"))


@app.route("/api/passengers", methods=["POST"])
def add_passenger():
    d = request.json
    try:
        r = query("INSERT INTO Passenger (Name,Age,Gender,Contact) VALUES (%s,%s,%s,%s)",
                  (d["Name"], d["Age"], d["Gender"], d["Contact"]), fetch=False)
        return jsonify({"success": True, "id": r["lastrowid"]})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/api/passengers/<int:pid>", methods=["PUT"])
def update_passenger(pid):
    d = request.json
    try:
        query("UPDATE Passenger SET Name=%s,Age=%s,Gender=%s,Contact=%s WHERE PassengerID=%s",
              (d["Name"], d["Age"], d["Gender"], d["Contact"], pid), fetch=False)
        return jsonify({"success": True})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/api/passengers/<int:pid>", methods=["DELETE"])
def delete_passenger(pid):
    try:
        query("DELETE FROM Passenger WHERE PassengerID=%s", (pid,), fetch=False)
        return jsonify({"success": True})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


# ── Search Trains (multi-table JOIN) ────────────────────────────────────
@app.route("/api/search")
def search_trains():
    src = request.args.get("from")
    dst = request.args.get("to")
    if not src or not dst:
        return jsonify([])
    return jsonify(query("""
        SELECT DISTINCT t.TrainNo, t.TrainName, t.Source, t.Destination,
               rs1.StationCode AS BoardStation, s1.StationName AS BoardName,
               rs2.StationCode AS ExitStation,  s2.StationName AS ExitName,
               (rs2.DistanceFromOrigin - rs1.DistanceFromOrigin) AS Distance
        FROM Train t
        JOIN RouteStation rs1 ON t.TrainNo = rs1.TrainNo
        JOIN RouteStation rs2 ON t.TrainNo = rs2.TrainNo
        JOIN Station s1       ON rs1.StationCode = s1.StationCode
        JOIN Station s2       ON rs2.StationCode = s2.StationCode
        WHERE rs1.StationCode = %s AND rs2.StationCode = %s
          AND rs1.SeqNo < rs2.SeqNo
    """, (src, dst)))


# ── Bookings ────────────────────────────────────────────────────────────
@app.route("/api/bookings")
def get_bookings():
    return jsonify(query("""
        SELECT b.PNR, p.Name, p.PassengerID, p.Age, p.Gender,
               t.TrainNo, t.TrainName,
               sc.ClassType, b.ClassID,
               b.BoardingStation, b.ExitStation,
               b.SeatID, s.CoachNo, s.SeatNo,
               b.JourneyDate, b.Status, b.BookingTime
        FROM Booking b
        JOIN Passenger p ON b.PassengerID = p.PassengerID
        JOIN Train t     ON b.TrainNo     = t.TrainNo
        JOIN SeatClass sc ON b.ClassID    = sc.ClassID
        LEFT JOIN Seat s ON b.SeatID      = s.SeatID
        ORDER BY b.PNR DESC
    """))


@app.route("/api/bookings/<int:pnr>", methods=["GET"])
def get_booking(pnr):
    rows = query("""
        SELECT b.PNR, p.Name, p.Age, p.Gender, p.Contact, p.PassengerID,
               t.TrainNo, t.TrainName, sc.ClassType, sc.ClassID, sc.FarePerKm,
               b.BoardingStation, s1.StationName AS BoardName,
               b.ExitStation,     s2.StationName AS ExitName,
               b.SeatID, s.CoachNo, s.SeatNo,
               b.JourneyDate, b.Status, b.BookingTime,
               (rs2.DistanceFromOrigin - rs1.DistanceFromOrigin) AS Distance
        FROM Booking b
        JOIN Passenger p    ON b.PassengerID    = p.PassengerID
        JOIN Train t        ON b.TrainNo        = t.TrainNo
        JOIN SeatClass sc   ON b.ClassID        = sc.ClassID
        JOIN Station s1     ON b.BoardingStation = s1.StationCode
        JOIN Station s2     ON b.ExitStation     = s2.StationCode
        JOIN RouteStation rs1 ON rs1.TrainNo = b.TrainNo AND rs1.StationCode = b.BoardingStation
        JOIN RouteStation rs2 ON rs2.TrainNo = b.TrainNo AND rs2.StationCode = b.ExitStation
        LEFT JOIN Seat s    ON b.SeatID = s.SeatID
        WHERE b.PNR = %s
    """, (pnr,))
    if not rows:
        return jsonify({"error": "PNR not found"}), 404
    row = rows[0]
    pay = query("SELECT * FROM Payment WHERE PNR=%s", (pnr,))
    row["payment"] = pay[0] if pay else None
    return jsonify(row)


@app.route("/api/bookings", methods=["POST"])
def create_booking():
    d = request.json
    try:
        avail = query("SELECT SeatID FROM Seat WHERE ClassID=%s AND Status='Available' LIMIT 1",
                      (d["ClassID"],))
        seat_id = avail[0]["SeatID"] if avail else None
        status = "Confirmed" if seat_id else "Waitlisted"

        r = query("""INSERT INTO Booking
                     (PassengerID,TrainNo,ClassID,BoardingStation,ExitStation,SeatID,JourneyDate,Status)
                     VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                  (d["PassengerID"], d["TrainNo"], d["ClassID"],
                   d["BoardingStation"], d["ExitStation"], seat_id,
                   d["JourneyDate"], status), fetch=False)
        pnr = r["lastrowid"]

        if seat_id:
            query("UPDATE Seat SET Status='Occupied' WHERE SeatID=%s", (seat_id,), fetch=False)

        return jsonify({"success": True, "pnr": pnr, "status": status, "seatId": seat_id,
                        "message": f"Booking {'confirmed' if status=='Confirmed' else 'waitlisted'}! PNR: {pnr}"})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/api/bookings/<int:pnr>", methods=["PUT"])
def update_booking(pnr):
    """Edit an existing booking (Passenger, Date, Stations, Status)."""
    d = request.json
    try:
        curr = query("SELECT * FROM Booking WHERE PNR=%s", (pnr,))
        if not curr:
            return jsonify({"success": False, "message": "Booking not found"}), 404

        curr_b = curr[0]
        new_passenger_id = d.get("PassengerID", curr_b["PassengerID"])
        new_journey_date = d.get("JourneyDate", curr_b["JourneyDate"])
        new_board = d.get("BoardingStation", curr_b["BoardingStation"])
        new_exit = d.get("ExitStation", curr_b["ExitStation"])
        new_status = d.get("Status", curr_b["Status"])

        old_seat_id = curr_b["SeatID"]
        new_seat_id = old_seat_id

        # If manually changing from Confirmed to Cancelled
        if new_status == "Cancelled" and curr_b["Status"] != "Cancelled":
            if old_seat_id:
                query("UPDATE Seat SET Status='Available' WHERE SeatID=%s", (old_seat_id,), fetch=False)
            new_seat_id = None
        # If manually changing from Waitlisted to Confirmed
        elif new_status == "Confirmed" and curr_b["Status"] != "Confirmed":
            avail = query("SELECT SeatID FROM Seat WHERE ClassID=%s AND Status='Available' LIMIT 1", (curr_b["ClassID"],))
            if avail:
                new_seat_id = avail[0]["SeatID"]
                query("UPDATE Seat SET Status='Occupied' WHERE SeatID=%s", (new_seat_id,), fetch=False)
            elif not old_seat_id:
                return jsonify({"success": False, "message": "Cannot confirm: No vacant seats available in this class."}), 400

        query("""
            UPDATE Booking
            SET PassengerID=%s, JourneyDate=%s, BoardingStation=%s, ExitStation=%s, Status=%s, SeatID=%s
            WHERE PNR=%s
        """, (new_passenger_id, new_journey_date, new_board, new_exit, new_status, new_seat_id, pnr), fetch=False)

        return jsonify({
            "success": True,
            "message": f"PNR {pnr} updated successfully!",
            "status": new_status,
            "seatId": new_seat_id
        })
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


@app.route("/api/bookings/<int:pnr>", methods=["DELETE"])
def delete_booking(pnr):
    """Delete a booking and free physical seat if occupied."""
    try:
        curr = query("SELECT SeatID, Status FROM Booking WHERE PNR=%s", (pnr,))
        if curr and curr[0]["SeatID"] and curr[0]["Status"] == "Confirmed":
            query("UPDATE Seat SET Status='Available' WHERE SeatID=%s", (curr[0]["SeatID"],), fetch=False)
        query("DELETE FROM Payment WHERE PNR=%s", (pnr,), fetch=False)
        query("DELETE FROM Booking WHERE PNR=%s", (pnr,), fetch=False)
        return jsonify({"success": True, "message": f"PNR {pnr} deleted successfully"})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


# ── Cancel (calls CancelBooking stored procedure + trigger) ─────────────
@app.route("/api/cancel/<int:pnr>", methods=["POST"])
def cancel_booking(pnr):
    try:
        before_wl = query("""
            SELECT b.PNR, p.Name
            FROM Booking b JOIN Passenger p ON b.PassengerID = p.PassengerID
            WHERE b.TrainNo = (SELECT TrainNo FROM Booking WHERE PNR=%s)
              AND b.Status = 'Waitlisted'
            ORDER BY b.BookingTime
        """, (pnr,))

        call_proc("CancelBooking", [pnr])

        promoted = []
        for wl in before_wl:
            after = query("SELECT Status, SeatID FROM Booking WHERE PNR=%s", (wl["PNR"],))
            if after and after[0]["Status"] == "Confirmed":
                promoted.append({"pnr": wl["PNR"], "name": wl["Name"], "seatId": after[0]["SeatID"]})

        return jsonify({"success": True, "message": f"PNR {pnr} cancelled", "promoted": promoted})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


# ── Bill (calls GenerateBill stored procedure) ──────────────────────────
@app.route("/api/bill/<int:pnr>", methods=["POST"])
def generate_bill(pnr):
    d = request.json
    try:
        result = call_proc("GenerateBill", [pnr, d.get("mode", "UPI")])
        fare = result[0]["CalculatedFare"] if result else 0
        pay = query("SELECT * FROM Payment WHERE PNR=%s ORDER BY PaymentID DESC LIMIT 1", (pnr,))
        return jsonify({"success": True, "fare": fare, "payment": pay[0] if pay else None,
                        "message": f"Bill generated: ₹{fare}"})
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


# ── Reports (aggregates, GROUP BY, HAVING) ──────────────────────────────
@app.route("/api/reports")
def get_reports():
    revenue_by_train = query("""
        SELECT t.TrainNo, t.TrainName,
               COUNT(DISTINCT b.PNR) AS TotalBookings,
               COALESCE(SUM(py.Amount),0) AS TotalRevenue
        FROM Train t
        LEFT JOIN Booking b ON t.TrainNo = b.TrainNo
        LEFT JOIN Payment py ON b.PNR = py.PNR AND py.Status='Success'
        GROUP BY t.TrainNo ORDER BY TotalRevenue DESC
    """)

    by_status = query("SELECT Status, COUNT(*) AS Count FROM Booking GROUP BY Status")

    by_mode = query("""
        SELECT Mode, COUNT(*) AS Count, SUM(Amount) AS Total
        FROM Payment WHERE Status='Success' GROUP BY Mode
    """)

    popular = query("""
        SELECT b.BoardingStation, s1.StationName AS FromStation,
               b.ExitStation,     s2.StationName AS ToStation,
               COUNT(*) AS BookingCount
        FROM Booking b
        JOIN Station s1 ON b.BoardingStation = s1.StationCode
        JOIN Station s2 ON b.ExitStation     = s2.StationCode
        GROUP BY b.BoardingStation, b.ExitStation
        HAVING COUNT(*) >= 1
        ORDER BY BookingCount DESC LIMIT 10
    """)

    return jsonify({"revenue_by_train": revenue_by_train, "by_status": by_status,
                    "by_mode": by_mode, "popular_routes": popular})


# ── Academic DBMS Queries Directory & Live Runner ───────────────────────
ACADEMIC_QUERIES = [
    {
        "id": "q1",
        "title": "Query 1: Senior Citizen Passengers",
        "category": "Selection & Sorting",
        "concept": "SELECT, WHERE, ORDER BY DESC",
        "description": "Retrieve all senior citizen passengers (Age >= 35) sorted by age descending.",
        "sql": "SELECT PassengerID, Name, Age, Gender, Contact FROM Passenger WHERE Age >= 35 ORDER BY Age DESC;"
    },
    {
        "id": "q2",
        "title": "Query 2: Passenger Name Pattern Matching",
        "category": "Pattern Matching",
        "concept": "LIKE operator with wildcards and OR logic",
        "description": "Find passengers whose name begins with 'S' or contains 'Kumar'.",
        "sql": "SELECT PassengerID, Name, Age, Gender, Contact FROM Passenger WHERE Name LIKE 'S%' OR Name LIKE '%Kumar%' ORDER BY Name ASC;"
    },
    {
        "id": "q3",
        "title": "Query 3: Train Route & Distance Breakdown",
        "category": "3-Table INNER JOIN",
        "concept": "Train + RouteStation + Station multi-table join",
        "description": "Display train stops in sequence with station names, cities, and distance from origin.",
        "sql": """SELECT t.TrainNo, t.TrainName, rs.SeqNo AS StopOrder, rs.StationCode, s.StationName, s.City, rs.DistanceFromOrigin AS KmFromOrigin
FROM Train t
JOIN RouteStation rs ON t.TrainNo = rs.TrainNo
JOIN Station s ON rs.StationCode = s.StationCode
ORDER BY t.TrainNo, rs.SeqNo ASC;"""
    },
    {
        "id": "q4",
        "title": "Query 4: Confirmed Passenger Reservation Manifest",
        "category": "5-Table Complex JOIN",
        "concept": "Booking + Passenger + Train + SeatClass + Seat",
        "description": "Official reservation manifest showing confirmed passengers with coach, seat, class, and journey route.",
        "sql": """SELECT b.PNR, p.Name AS PassengerName, CONCAT(p.Age, ' / ', p.Gender) AS Age_Sex, t.TrainName, sc.ClassType, s.CoachNo, s.SeatNo, CONCAT(b.BoardingStation, ' -> ', b.ExitStation) AS Route, b.Status
FROM Booking b
JOIN Passenger p ON b.PassengerID = p.PassengerID
JOIN Train t ON b.TrainNo = t.TrainNo
JOIN SeatClass sc ON b.ClassID = sc.ClassID
JOIN Seat s ON b.SeatID = s.SeatID
WHERE b.Status = 'Confirmed'
ORDER BY t.TrainNo, s.CoachNo, s.SeatNo;"""
    },
    {
        "id": "q5",
        "title": "Query 5: Financial Statistics from Payments",
        "category": "Aggregate Functions",
        "concept": "COUNT, SUM, AVG, MAX, MIN",
        "description": "Calculate total revenue, average fare paid, highest fare, and minimum fare from successful payments.",
        "sql": "SELECT COUNT(PaymentID) AS TotalPayments, SUM(Amount) AS TotalRevenue, ROUND(AVG(Amount), 2) AS AverageFare, MAX(Amount) AS MaxFare, MIN(Amount) AS MinFare FROM Payment WHERE Status = 'Success';"
    },
    {
        "id": "q6",
        "title": "Query 6: Revenue & Bookings per Train",
        "category": "GROUP BY with Aggregate",
        "concept": "LEFT JOIN, COUNT DISTINCT, SUM with COALESCE",
        "description": "Calculate total bookings and total revenue collected for each train in the system.",
        "sql": """SELECT t.TrainNo, t.TrainName, COUNT(DISTINCT b.PNR) AS TotalBookings, COALESCE(SUM(py.Amount), 0) AS TotalRevenue
FROM Train t
LEFT JOIN Booking b ON t.TrainNo = b.TrainNo
LEFT JOIN Payment py ON b.PNR = py.PNR AND py.Status = 'Success'
GROUP BY t.TrainNo, t.TrainName
ORDER BY TotalRevenue DESC;"""
    },
    {
        "id": "q7",
        "title": "Query 7: Trains with High Reservation Volume",
        "category": "GROUP BY + HAVING",
        "concept": "HAVING clause filtering on aggregate count",
        "description": "Find trains that have 2 or more confirmed reservations.",
        "sql": """SELECT t.TrainNo, t.TrainName, COUNT(b.PNR) AS ConfirmedCount
FROM Train t
JOIN Booking b ON t.TrainNo = b.TrainNo
WHERE b.Status = 'Confirmed'
GROUP BY t.TrainNo, t.TrainName
HAVING COUNT(b.PNR) >= 2;"""
    },
    {
        "id": "q8",
        "title": "Query 8: Waiting List Passengers",
        "category": "Nested Subquery (IN)",
        "concept": "Subquery using IN operator",
        "description": "Retrieve contact information for all passengers currently on the waiting list.",
        "sql": "SELECT PassengerID, Name, Age, Gender, Contact FROM Passenger WHERE PassengerID IN (SELECT PassengerID FROM Booking WHERE Status = 'Waitlisted');"
    },
    {
        "id": "q9",
        "title": "Query 9: Confirmed Bookings Awaiting Payment",
        "category": "Nested Subquery (NOT IN)",
        "concept": "Subquery using NOT IN",
        "description": "Find confirmed bookings that have not yet generated a successful payment receipt.",
        "sql": "SELECT b.PNR, p.Name AS PassengerName, b.TrainNo, b.BoardingStation, b.ExitStation FROM Booking b JOIN Passenger p ON b.PassengerID = p.PassengerID WHERE b.Status = 'Confirmed' AND b.PNR NOT IN (SELECT PNR FROM Payment WHERE Status = 'Success');"
    },
    {
        "id": "q10",
        "title": "Query 10: Reservation Breakdown Matrix",
        "category": "Conditional Aggregation",
        "concept": "CASE WHEN inside SUM() aggregation",
        "description": "Display count of Confirmed, Waitlisted, and Cancelled tickets for each train side-by-side.",
        "sql": """SELECT t.TrainNo, t.TrainName,
       SUM(CASE WHEN b.Status = 'Confirmed' THEN 1 ELSE 0 END) AS Confirmed,
       SUM(CASE WHEN b.Status = 'Waitlisted' THEN 1 ELSE 0 END) AS Waitlisted,
       SUM(CASE WHEN b.Status = 'Cancelled' THEN 1 ELSE 0 END) AS Cancelled,
       COUNT(b.PNR) AS Total
FROM Train t
LEFT JOIN Booking b ON t.TrainNo = b.TrainNo
GROUP BY t.TrainNo, t.TrainName;"""
    },
    {
        "id": "q11",
        "title": "Query 11: Coach Occupancy & Capacity Matrix",
        "category": "Capacity Aggregation",
        "concept": "Seat occupancy percentage calculation",
        "description": "Physical seat capacity, occupied seats, and occupancy rate grouped by coach.",
        "sql": """SELECT sc.TrainNo, sc.ClassType, s.CoachNo, COUNT(s.SeatID) AS TotalSeats,
       SUM(CASE WHEN s.Status = 'Occupied' THEN 1 ELSE 0 END) AS Occupied,
       SUM(CASE WHEN s.Status = 'Available' THEN 1 ELSE 0 END) AS Available,
       CONCAT(ROUND((SUM(CASE WHEN s.Status = 'Occupied' THEN 1 ELSE 0 END) / COUNT(s.SeatID)) * 100, 1), '%') AS OccupancyRate
FROM Seat s
JOIN SeatClass sc ON s.ClassID = sc.ClassID
GROUP BY sc.TrainNo, sc.ClassType, s.CoachNo;"""
    },
    {
        "id": "q12",
        "title": "Query 12: Conductor TTE Manifest View",
        "category": "Database View",
        "concept": "CREATE VIEW vw_PassengerManifest and SELECT from view",
        "description": "Query the created abstract database view summarizing all confirmed passenger journey data.",
        "sql": "SELECT * FROM vw_PassengerManifest WHERE BookingStatus = 'Confirmed' LIMIT 10;"
    }
]


@app.route("/api/sql-queries")
def get_sql_queries():
    return jsonify(ACADEMIC_QUERIES)


@app.route("/api/sql-queries/run", methods=["POST"])
def run_sql_query():
    data = request.json or {}
    sql = data.get("sql", "").strip()
    query_id = data.get("query_id")

    if query_id:
        match = next((q for q in ACADEMIC_QUERIES if q["id"] == query_id), None)
        if match:
            sql = match["sql"]

    if not sql:
        return jsonify({"success": False, "message": "No SQL query provided."}), 400

    # Ensure view exists if query 12 is run
    if "vw_passengermanifest" in sql.lower():
        try:
            query("""
                CREATE OR REPLACE VIEW vw_PassengerManifest AS
                SELECT b.PNR, p.Name AS PassengerName, p.Age, p.Gender, p.Contact,
                       t.TrainNo, t.TrainName, sc.ClassType, s.CoachNo, s.SeatNo,
                       b.BoardingStation, b.ExitStation, b.JourneyDate, b.Status AS BookingStatus
                FROM Booking b
                JOIN Passenger p  ON b.PassengerID = p.PassengerID
                JOIN Train t      ON b.TrainNo = t.TrainNo
                JOIN SeatClass sc ON b.ClassID = sc.ClassID
                LEFT JOIN Seat s  ON b.SeatID = s.SeatID;
            """, fetch=False)
        except Exception:
            pass

    import time
    start = time.time()
    try:
        clean_sql = sql.rstrip(";").strip()
        rows = query(clean_sql, fetch=True)
        exec_time = round((time.time() - start) * 1000, 2)
        columns = list(rows[0].keys()) if rows else []
        return jsonify({
            "success": True,
            "columns": columns,
            "rows": rows,
            "count": len(rows),
            "execution_time_ms": exec_time,
            "sql": sql
        })
    except Error as e:
        return jsonify({"success": False, "message": str(e), "sql": sql}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e), "sql": sql}), 400


# ── In-Memory Chart Preparation Store & Helpers ─────────────────────────
TRAIN_CHART_STATUS = {}


def get_berth_type(seat_no, class_type="Sleeper"):
    r = int(seat_no) % 8
    if r in (1, 4):
        return "Lower Berth (LB)"
    if r in (2, 5):
        return "Middle Berth (MB)"
    if r in (3, 6):
        return "Upper Berth (UB)"
    if r == 7:
        return "Side Lower (SL)"
    return "Side Upper (SU)"


# ── Booking Chart (Indian Railway style) ────────────────────────────────
@app.route("/api/chart")
def chart_summary():
    """Overall booking status across all trains."""
    status_counts = query("""
        SELECT Status, COUNT(*) AS Count
        FROM Booking GROUP BY Status
    """)

    train_summary = query("""
        SELECT t.TrainNo, t.TrainName, t.Source, t.Destination,
               SUM(CASE WHEN b.Status='Confirmed' THEN 1 ELSE 0 END) AS Confirmed,
               SUM(CASE WHEN b.Status='Waitlisted' THEN 1 ELSE 0 END) AS Waitlisted,
               SUM(CASE WHEN b.Status='Cancelled' THEN 1 ELSE 0 END) AS Cancelled,
               COUNT(b.PNR) AS Total
        FROM Train t LEFT JOIN Booking b ON t.TrainNo = b.TrainNo
        GROUP BY t.TrainNo
    """)

    trains = query("SELECT TrainNo, TrainName FROM Train ORDER BY TrainNo")

    return jsonify({
        "status_counts": status_counts,
        "train_summary": train_summary,
        "trains": trains
    })


@app.route("/api/chart/<int:tno>")
def chart_detail(tno):
    """Detailed seat-level chart for a specific train — like Indian Railway availability chart."""
    # Train info
    train = query("SELECT * FROM Train WHERE TrainNo=%s", (tno,))
    if not train:
        return jsonify({"error": "Train not found"}), 404

    # Route
    route = query("""
        SELECT rs.SeqNo, rs.StationCode, s.StationName, rs.DistanceFromOrigin
        FROM RouteStation rs JOIN Station s ON rs.StationCode = s.StationCode
        WHERE rs.TrainNo = %s ORDER BY rs.SeqNo
    """, (tno,))

    # Seat classes with seat-level detail
    classes = query("""
        SELECT sc.ClassID, sc.ClassType, sc.TotalSeats, sc.FarePerKm
        FROM SeatClass sc WHERE sc.TrainNo = %s
    """, (tno,))

    chart_data = []
    for cls in classes:
        cid = cls["ClassID"]
        # Get all seats with booking info
        seats = query("""
            SELECT s.SeatID, s.CoachNo, s.SeatNo, s.Status,
                   b.PNR, b.BoardingStation, b.ExitStation, b.Status AS BookingStatus,
                   p.Name AS PassengerName, p.Gender, p.Age
            FROM Seat s
            LEFT JOIN Booking b ON s.SeatID = b.SeatID AND b.Status = 'Confirmed'
            LEFT JOIN Passenger p ON b.PassengerID = p.PassengerID
            WHERE s.ClassID = %s
            ORDER BY s.CoachNo, s.SeatNo
        """, (cid,))

        # Get waitlisted passengers for this class
        waitlisted = query("""
            SELECT b.PNR, p.Name AS PassengerName, p.Gender, p.Age,
                   b.BoardingStation, b.ExitStation, b.BookingTime,
                   s1.StationName AS BoardName, s2.StationName AS ExitName
            FROM Booking b
            JOIN Passenger p ON b.PassengerID = p.PassengerID
            JOIN Station s1 ON b.BoardingStation = s1.StationCode
            JOIN Station s2 ON b.ExitStation = s2.StationCode
            WHERE b.TrainNo = %s AND b.ClassID = %s AND b.Status = 'Waitlisted'
            ORDER BY b.BookingTime ASC
        """, (tno, cid))

        chart_data.append({
            "classId": cid,
            "classType": cls["ClassType"],
            "totalSeats": cls["TotalSeats"],
            "farePerKm": float(cls["FarePerKm"]),
            "seats": seats,
            "waitlisted": waitlisted,
            "available": sum(1 for s in seats if s["Status"] == "Available"),
            "occupied": sum(1 for s in seats if s["Status"] == "Occupied"),
        })

    # Booking status breakdown for this train
    status = query("""
        SELECT Status, COUNT(*) AS Count
        FROM Booking WHERE TrainNo = %s GROUP BY Status
    """, (tno,))

    # Full Confirmed Passengers List (Manifest)
    confirmed_tickets = query("""
        SELECT b.PNR, p.Name AS PassengerName, p.Age, p.Gender, p.Contact,
               s.CoachNo, s.SeatNo, sc.ClassType,
               b.BoardingStation, s1.StationName AS BoardName,
               b.ExitStation, s2.StationName AS ExitName,
               b.BookingTime
        FROM Booking b
        JOIN Passenger p ON b.PassengerID = p.PassengerID
        JOIN Seat s ON b.SeatID = s.SeatID
        JOIN SeatClass sc ON b.ClassID = sc.ClassID
        JOIN Station s1 ON b.BoardingStation = s1.StationCode
        JOIN Station s2 ON b.ExitStation = s2.StationCode
        WHERE b.TrainNo = %s AND b.Status = 'Confirmed'
        ORDER BY s.CoachNo, s.SeatNo
    """, (tno,))

    for ct in confirmed_tickets:
        ct["BerthType"] = get_berth_type(ct["SeatNo"], ct["ClassType"])

    # Full Waiting List Passengers
    waiting_passengers = query("""
        SELECT b.PNR, p.Name AS PassengerName, p.Age, p.Gender, p.Contact,
               sc.ClassType,
               b.BoardingStation, s1.StationName AS BoardName,
               b.ExitStation, s2.StationName AS ExitName,
               b.BookingTime
        FROM Booking b
        JOIN Passenger p ON b.PassengerID = p.PassengerID
        JOIN SeatClass sc ON b.ClassID = sc.ClassID
        JOIN Station s1 ON b.BoardingStation = s1.StationCode
        JOIN Station s2 ON b.ExitStation = s2.StationCode
        WHERE b.TrainNo = %s AND b.Status = 'Waitlisted'
        ORDER BY b.BookingTime ASC
    """, (tno,))

    for idx, wl in enumerate(waiting_passengers):
        wl["WLNumber"] = f"WL{idx + 1}"

    chart_info = TRAIN_CHART_STATUS.get(tno, {"prepared": False, "prepared_at": None})

    return jsonify({
        "train": train[0],
        "route": route,
        "classes": chart_data,
        "status": status,
        "chart_status": chart_info,
        "confirmed_tickets": confirmed_tickets,
        "waiting_passengers": waiting_passengers
    })


# ── Prepare Chart Action (Auto Waitlist Promotion & Finalization) ────────
@app.route("/api/chart/prepare/<int:tno>", methods=["POST"])
def prepare_chart(tno):
    """
    Official Indian Railways Chart Preparation:
    1. Finds all unallocated available seats in each class for this train.
    2. Promotes waitlisted passengers (FIFO by BookingTime) to Confirmed status.
    3. Locks chart status as 'CHART PREPARED' with an official timestamp.
    """
    try:
        classes = query("SELECT ClassID, ClassType FROM SeatClass WHERE TrainNo=%s", (tno,))
        promoted = []

        for cls in classes:
            cid = cls["ClassID"]
            avail_seats = query("""
                SELECT SeatID, CoachNo, SeatNo
                FROM Seat WHERE ClassID=%s AND Status='Available'
                ORDER BY CoachNo, SeatNo
            """, (cid,))

            waitlist = query("""
                SELECT b.PNR, p.Name
                FROM Booking b
                JOIN Passenger p ON b.PassengerID=p.PassengerID
                WHERE b.TrainNo=%s AND b.ClassID=%s AND b.Status='Waitlisted'
                ORDER BY b.BookingTime ASC
            """, (tno, cid))

            for seat, wl in zip(avail_seats, waitlist):
                query("UPDATE Booking SET Status='Confirmed', SeatID=%s WHERE PNR=%s",
                      (seat["SeatID"], wl["PNR"]), fetch=False)
                query("UPDATE Seat SET Status='Occupied' WHERE SeatID=%s",
                      (seat["SeatID"],), fetch=False)
                promoted.append({
                    "pnr": wl["PNR"],
                    "name": wl["Name"],
                    "class": cls["ClassType"],
                    "coach": seat["CoachNo"],
                    "seatNo": seat["SeatNo"]
                })

        prepared_time = datetime.now().strftime("%d-%b-%Y %I:%M %p")
        TRAIN_CHART_STATUS[tno] = {
            "prepared": True,
            "prepared_at": prepared_time,
            "promoted_count": len(promoted)
        }

        return jsonify({
            "success": True,
            "message": f"Chart Prepared successfully for Train #{tno}!",
            "prepared_at": prepared_time,
            "promoted": promoted,
            "promoted_count": len(promoted)
        })
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 400


# ── Live Assistant / Chatbot for Railway Inquiries & Charting ───────────
@app.route("/api/chat", methods=["POST"])
def live_chat_assistant():
    """Live Chat preparation and reservation queries assistant."""
    data = request.json or {}
    msg = data.get("message", "").strip().lower()

    if not msg:
        return jsonify({"reply": "Please enter a question (e.g., 'confirmed tickets', 'waitlist', 'prepare chart 12658', 'pnr 1')."})

    import re
    # Check for PNR query
    pnr_match = re.search(r'\bpnr\s*#?\s*(\d+)\b', msg) or (re.search(r'^\d+$', msg) and {"val": msg})
    if pnr_match:
        pnr_val = pnr_match.group(1) if hasattr(pnr_match, 'group') else msg
        b = query("""
            SELECT b.PNR, p.Name, b.Status, b.TrainNo, t.TrainName, sc.ClassType,
                   b.BoardingStation, b.ExitStation, s.CoachNo, s.SeatNo
            FROM Booking b
            JOIN Passenger p ON b.PassengerID = p.PassengerID
            JOIN Train t ON b.TrainNo = t.TrainNo
            JOIN SeatClass sc ON b.ClassID = sc.ClassID
            LEFT JOIN Seat s ON b.SeatID = s.SeatID
            WHERE b.PNR = %s
        """, (pnr_val,))
        if b:
            item = b[0]
            seat_info = f"Coach {item['CoachNo']}, Seat {item['SeatNo']}" if item["SeatNo"] else "No seat assigned (Waitlisted)"
            return jsonify({
                "reply": f"🚆 **PNR {item['PNR']} Status**:\n• Passenger: **{item['Name']}**\n• Train: **{item['TrainName']} (#{item['TrainNo']})**\n• Status: **{item['Status']}**\n• Allocation: {seat_info}\n• Route: {item['BoardingStation']} → {item['ExitStation']}"
            })
        else:
            return jsonify({"reply": f"❌ PNR {pnr_val} not found in database."})

    # Prepare chart
    if "prepare" in msg and "chart" in msg:
        tno_match = re.search(r'\b(\d{4,5})\b', msg)
        tno = int(tno_match.group(1)) if tno_match else 12658
        return jsonify({
            "action": "prepare_chart",
            "trainNo": tno,
            "reply": f"⚙️ Initiating automated Chart Preparation for Train #{tno}..."
        })

    # Waitlist query
    if "waitlist" in msg or "waiting" in msg or "wl" in msg:
        wl_passengers = query("""
            SELECT b.PNR, p.Name, t.TrainNo, t.TrainName, sc.ClassType, b.BoardingStation, b.ExitStation
            FROM Booking b
            JOIN Passenger p ON b.PassengerID = p.PassengerID
            JOIN Train t ON b.TrainNo = t.TrainNo
            JOIN SeatClass sc ON b.ClassID = sc.ClassID
            WHERE b.Status = 'Waitlisted'
            ORDER BY b.TrainNo, b.BookingTime ASC
        """)
        if not wl_passengers:
            return jsonify({"reply": "✅ There are currently **no passengers on the waiting list**. All seats are confirmed!"})
        lines = [f"📋 **Current Waiting List ({len(wl_passengers)} passengers)**:"]
        for i, p in enumerate(wl_passengers[:8]):
            lines.append(f"{i+1}. **{p['Name']}** (PNR {p['PNR']}) - Train #{p['TrainNo']} ({p['ClassType']}: {p['BoardingStation']} → {p['ExitStation']})")
        if len(wl_passengers) > 8:
            lines.append(f"...and {len(wl_passengers)-8} more.")
        return jsonify({"reply": "\n".join(lines)})

    # Confirmed tickets query
    if "confirmed" in msg or "cnf" in msg:
        cnf = query("""
            SELECT b.PNR, p.Name, t.TrainNo, sc.ClassType, s.CoachNo, s.SeatNo
            FROM Booking b
            JOIN Passenger p ON b.PassengerID = p.PassengerID
            JOIN Train t ON b.TrainNo = t.TrainNo
            JOIN SeatClass sc ON b.ClassID = sc.ClassID
            JOIN Seat s ON b.SeatID = s.SeatID
            WHERE b.Status = 'Confirmed'
            ORDER BY b.TrainNo, s.CoachNo, s.SeatNo
            LIMIT 8
        """)
        lines = [f"🎟️ **Sample Confirmed Tickets ({len(cnf)} shown)**:"]
        for p in cnf:
            lines.append(f"• **{p['Name']}** (PNR {p['PNR']}) - Coach **{p['CoachNo']}**, Seat **{p['SeatNo']}** ({p['ClassType']} on #{p['TrainNo']})")
        return jsonify({"reply": "\n".join(lines)})

    # Trains list
    if "train" in msg:
        trains = query("SELECT TrainNo, TrainName, Source, Destination FROM Train ORDER BY TrainNo")
        lines = ["🚄 **Trains in Database**:"]
        for t in trains:
            lines.append(f"• **{t['TrainName']}** (#{t['TrainNo']}): {t['Source']} → {t['Destination']}")
        return jsonify({"reply": "\n".join(lines)})

    # Help
    return jsonify({
        "reply": "👋 **Railway Live Assistant**:\nTry asking:\n• `show waitlist` - View all waitlisted passengers\n• `confirmed tickets` - View confirmed passenger list\n• `prepare chart 12658` - Run live chart preparation\n• `pnr 1` - Track PNR status\n• `trains` - View list of trains"
    })


def open_browser():
    import webbrowser
    webbrowser.open_new("http://localhost:5000")


# ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    from threading import Timer
    # Automatically open the browser once the Flask server starts
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        Timer(1.2, open_browser).start()
    app.run(debug=True, port=5000)
