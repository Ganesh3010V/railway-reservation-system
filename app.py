"""
Railway Reservation System with Multi-Leg Journey Support
& Automated Waitlist Management
----------------------------------------------------------
DBMS Mini Project frontend (Streamlit)
Submitted by: Ganesh | B.Tech AIML | UVCE Bangalore

Run with:
    streamlit run app.py

Make sure Railway_DBMS_Full_Schema.sql has already been loaded into
MySQL/MariaDB (creates the railway_db database) before running this.
Update the DB_CONFIG block below with your own MySQL credentials.
"""

import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import date

# ----------------------------------------------------------------------
# DATABASE CONFIG  -- change these to match your own MySQL setup
# ----------------------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Ganesh@3018",
    "database": "railway_db",
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def run_query(query, params=None, fetch=True):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(query, params or ())
    result = cur.fetchall() if fetch else None
    conn.commit()
    cur.close()
    conn.close()
    return result


def call_procedure(proc_name, args):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.callproc(proc_name, args)
    results = []
    for result in cur.stored_results():
        results.extend(result.fetchall())
    conn.commit()
    cur.close()
    conn.close()
    return results


# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(page_title="Railway Reservation System", page_icon="🚆", layout="wide")

st.title("🚆 Railway Reservation System")
st.caption("Multi-Leg Journey Support & Automated Waitlist Management — DBMS Mini Project")

menu = st.sidebar.radio(
    "Menu",
    ["Trains & Routes", "Book a Ticket", "PNR Status / My Bookings", "Cancel Ticket", "Generate Bill"],
)

# ----------------------------------------------------------------------
# 1. TRAINS & ROUTES
# ----------------------------------------------------------------------
if menu == "Trains & Routes":
    st.header("Available Trains")
    try:
        trains = run_query("SELECT * FROM Train")
        st.dataframe(trains, use_container_width=True)

        st.subheader("Route for a Train")
        train_options = {f"{t['TrainNo']} - {t['TrainName']}": t["TrainNo"] for t in trains}
        if train_options:
            choice = st.selectbox("Select a train", list(train_options.keys()))
            tno = train_options[choice]
            route = run_query(
                """SELECT rs.SeqNo, rs.StationCode, s.StationName, s.City, rs.DistanceFromOrigin
                   FROM RouteStation rs JOIN Station s ON rs.StationCode = s.StationCode
                   WHERE rs.TrainNo = %s ORDER BY rs.SeqNo""",
                (tno,),
            )
            st.dataframe(route, use_container_width=True)

            st.subheader("Seat Classes & Availability")
            classes = run_query(
                """SELECT sc.ClassID, sc.ClassType, sc.FarePerKm, sc.TotalSeats,
                          SUM(CASE WHEN se.Status='Available' THEN 1 ELSE 0 END) AS SeatsAvailableNow
                   FROM SeatClass sc LEFT JOIN Seat se ON sc.ClassID = se.ClassID
                   WHERE sc.TrainNo = %s GROUP BY sc.ClassID""",
                (tno,),
            )
            st.dataframe(classes, use_container_width=True)
    except Error as e:
        st.error(f"Database error: {e}")

# ----------------------------------------------------------------------
# 2. BOOK A TICKET
# ----------------------------------------------------------------------
elif menu == "Book a Ticket":
    st.header("Book a Ticket")
    try:
        passengers = run_query("SELECT PassengerID, Name FROM Passenger")
        trains = run_query("SELECT TrainNo, TrainName FROM Train")

        if not passengers or not trains:
            st.warning("Add passengers/trains to the database first.")
        else:
            p_map = {f"{p['Name']} (ID {p['PassengerID']})": p["PassengerID"] for p in passengers}
            t_map = {f"{t['TrainNo']} - {t['TrainName']}": t["TrainNo"] for t in trains}

            passenger_choice = st.selectbox("Passenger", list(p_map.keys()))
            train_choice = st.selectbox("Train", list(t_map.keys()))
            tno = t_map[train_choice]

            stations = run_query(
                """SELECT s.StationCode, s.StationName, rs.SeqNo
                   FROM RouteStation rs JOIN Station s ON rs.StationCode = s.StationCode
                   WHERE rs.TrainNo = %s ORDER BY rs.SeqNo""",
                (tno,),
            )
            st_map = {f"{s['StationName']} ({s['StationCode']})": s["StationCode"] for s in stations}

            col1, col2 = st.columns(2)
            with col1:
                board_choice = st.selectbox("Boarding Station", list(st_map.keys()), key="board")
            with col2:
                exit_choice = st.selectbox("Exit Station", list(st_map.keys()), index=len(st_map) - 1, key="exit")

            classes = run_query("SELECT ClassID, ClassType, FarePerKm FROM SeatClass WHERE TrainNo = %s", (tno,))
            c_map = {f"{c['ClassType']} (₹{c['FarePerKm']}/km)": c["ClassID"] for c in classes}
            class_choice = st.selectbox("Seat Class", list(c_map.keys()))

            journey_date = st.date_input("Journey Date", value=date.today())

            if st.button("Check Fare & Book"):
                board_code = st_map[board_choice]
                exit_code = st_map[exit_choice]
                class_id = c_map[class_choice]

                if board_code == exit_code:
                    st.error("Boarding and exit stations can't be the same.")
                else:
                    # find an available seat in this class
                    avail_seat = run_query(
                        "SELECT SeatID FROM Seat WHERE ClassID=%s AND Status='Available' LIMIT 1",
                        (class_id,),
                    )
                    seat_id = avail_seat[0]["SeatID"] if avail_seat else None
                    status = "Confirmed" if seat_id else "Waitlisted"

                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        """INSERT INTO Booking (PassengerID, TrainNo, ClassID, BoardingStation,
                                                 ExitStation, SeatID, JourneyDate, Status)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (p_map[passenger_choice], tno, class_id, board_code, exit_code,
                         seat_id, journey_date, status),
                    )
                    pnr = cur.lastrowid
                    if seat_id:
                        cur.execute("UPDATE Seat SET Status='Occupied' WHERE SeatID=%s", (seat_id,))
                    conn.commit()
                    cur.close()
                    conn.close()

                    if status == "Confirmed":
                        st.success(f"Booking confirmed! PNR = {pnr}, Seat ID = {seat_id}")
                    else:
                        st.warning(f"No seat available right now — booking PNR {pnr} placed on the WAITLIST.")
    except Error as e:
        st.error(f"Database error: {e}")

# ----------------------------------------------------------------------
# 3. PNR STATUS / MY BOOKINGS
# ----------------------------------------------------------------------
elif menu == "PNR Status / My Bookings":
    st.header("PNR Status")
    try:
        bookings = run_query(
            """SELECT b.PNR, p.Name AS Passenger, b.TrainNo, b.BoardingStation, b.ExitStation,
                      b.JourneyDate, b.Status, b.SeatID
               FROM Booking b JOIN Passenger p ON b.PassengerID = p.PassengerID
               ORDER BY b.PNR"""
        )
        st.dataframe(bookings, use_container_width=True)

        pnr_lookup = st.number_input("Look up a specific PNR", min_value=1, step=1)
        if st.button("Check Status"):
            row = run_query(
                """SELECT b.*, p.Name FROM Booking b JOIN Passenger p ON b.PassengerID = p.PassengerID
                   WHERE b.PNR = %s""",
                (pnr_lookup,),
            )
            if row:
                st.json(row[0])
            else:
                st.error("PNR not found.")
    except Error as e:
        st.error(f"Database error: {e}")

# ----------------------------------------------------------------------
# 4. CANCEL TICKET  (demonstrates the trigger + CancelBooking procedure)
# ----------------------------------------------------------------------
elif menu == "Cancel Ticket":
    st.header("Cancel a Ticket")
    st.caption("Cancelling a confirmed seat automatically checks the waitlist for an overlapping "
               "segment and promotes the earliest matching passenger — live, via the "
               "CancelBooking stored procedure and the seat-release trigger.")
    try:
        active = run_query(
            """SELECT b.PNR, p.Name, b.BoardingStation, b.ExitStation, b.Status, b.SeatID
               FROM Booking b JOIN Passenger p ON b.PassengerID = p.PassengerID
               WHERE b.Status IN ('Confirmed','Waitlisted') ORDER BY b.PNR"""
        )
        st.dataframe(active, use_container_width=True)

        pnr_cancel = st.number_input("PNR to cancel", min_value=1, step=1)
        if st.button("Cancel Booking"):
            before = run_query(
                """SELECT b.PNR, p.Name, b.Status FROM Booking b
                   JOIN Passenger p ON b.PassengerID=p.PassengerID
                   WHERE b.TrainNo = (SELECT TrainNo FROM Booking WHERE PNR=%s)
                   AND b.Status='Waitlisted' ORDER BY b.BookingTime""",
                (pnr_cancel,),
            )
            call_procedure("CancelBooking", [int(pnr_cancel)])

            after = run_query(
                """SELECT b.PNR, p.Name, b.Status, b.SeatID FROM Booking b
                   JOIN Passenger p ON b.PassengerID=p.PassengerID ORDER BY b.PNR"""
            )
            st.success(f"PNR {pnr_cancel} cancelled.")
            promoted = [r for r in after if r["Status"] == "Confirmed" and
                        r["PNR"] in [b["PNR"] for b in before]]
            if promoted:
                st.balloons()
                st.info(f"Waitlist auto-promoted: PNR {promoted[0]['PNR']} ({promoted[0]['Name']}) "
                        f"is now CONFIRMED with Seat {promoted[0]['SeatID']}.")
            st.dataframe(after, use_container_width=True)
    except Error as e:
        st.error(f"Database error: {e}")

# ----------------------------------------------------------------------
# 5. GENERATE BILL  (demonstrates the GenerateBill stored procedure)
# ----------------------------------------------------------------------
elif menu == "Generate Bill":
    st.header("Generate Bill")
    try:
        confirmed = run_query(
            """SELECT b.PNR, p.Name, b.BoardingStation, b.ExitStation
               FROM Booking b JOIN Passenger p ON b.PassengerID=p.PassengerID
               WHERE b.Status='Confirmed'
               AND b.PNR NOT IN (SELECT PNR FROM Payment)"""
        )
        st.dataframe(confirmed, use_container_width=True)

        pnr_bill = st.number_input("PNR to bill", min_value=1, step=1)
        mode = st.selectbox("Payment Mode", ["UPI", "Card", "Cash"])
        if st.button("Generate Bill"):
            result = call_procedure("GenerateBill", [int(pnr_bill), mode])
            if result:
                st.success(f"Fare calculated: ₹{result[0]['CalculatedFare']}")
            payments = run_query("SELECT * FROM Payment WHERE PNR=%s", (pnr_bill,))
            st.dataframe(payments, use_container_width=True)
    except Error as e:
        st.error(f"Database error: {e}")

st.sidebar.markdown("---")
st.sidebar.caption("Ganesh | B.Tech AIML | UVCE Bangalore")
