-- =====================================================================
-- RAILWAY RESERVATION SYSTEM: DEMO & EVALUATION SAMPLE DATA
-- Submitted by: Ganesh | B.Tech AIML | UVCE Bangalore
--
-- PURPOSE:
-- Run this script in MySQL Workbench or via command line whenever you want
-- to reset the database to a clean, impressive demonstration state for
-- your evaluation/presentation to faculty.
--
-- DEMO SCENARIO FOR TRAIN 12658 (Bengaluru Mail: SBC -> MAS):
-- • Sleeper Class (6 seats): 100% FULL (All 6 seats CONFIRMED)
--   - 3 Passengers in WAITING LIST (WL1: Arjun, WL2: Kiran, WL3: Pooja)
-- • AC Class (4 seats): 2 CONFIRMED (Priya, Vikram), 2 AVAILABLE
--   - 1 Passenger in WAITING LIST (WL1: Rajesh)
-- =====================================================================

USE railway_db;

-- 1. CLEAN EXISTING DEMO BOOKINGS & PAYMENTS
DELETE FROM Payment;
DELETE FROM Booking;
DELETE FROM Passenger;

-- Reset Auto-Increment IDs
ALTER TABLE Passenger AUTO_INCREMENT = 1;
ALTER TABLE Booking AUTO_INCREMENT = 1;
ALTER TABLE Payment AUTO_INCREMENT = 1;

-- Reset all physical seats to Available
UPDATE Seat SET Status = 'Available';

-- ---------------------------------------------------------------------
-- 2. INSERT 12 SAMPLE PASSENGERS
-- ---------------------------------------------------------------------
INSERT INTO Passenger (PassengerID, Name, Age, Gender, Contact) VALUES
(1,  'Ganesh Kumar',    21, 'M', '9845011111'),
(2,  'Divya Rao',       24, 'F', '9845022222'),
(3,  'Rahul Verma',     29, 'M', '9845033333'),
(4,  'Sunita Patel',    52, 'F', '9845044444'),
(5,  'Amit Shah',       36, 'M', '9845055555'),
(6,  'Sneha Reddy',     27, 'F', '9845066666'),
(7,  'Arjun Mehta',     31, 'M', '9845077777'),
(8,  'Kiran Shetty',    35, 'M', '9845088888'),
(9,  'Pooja Hegde',     23, 'F', '9845099999'),
(10, 'Priya Nair',      22, 'F', '9845012345'),
(11, 'Vikram Malhotra', 46, 'M', '9845054321'),
(12, 'Rajesh Khanna',   59, 'M', '9845098765');


-- ---------------------------------------------------------------------
-- 3. INSERT CONFIRMED TICKETS (TRAIN 12658: BENGALURU MAIL)
-- ---------------------------------------------------------------------

-- [SLEEPER CLASS - ClassID 1: S1-1 to S1-6] -> All 6 Seats Filled!
-- PNR 1: Ganesh Kumar -> S1-1 (Lower Berth)
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES (1, 1, 12658, 1, 'SBC', 'KPD', 1, '2026-11-10', 'Confirmed', '2026-11-01 08:00:00');
UPDATE Seat SET Status = 'Occupied' WHERE SeatID = 1;

-- PNR 2: Divya Rao -> S1-2 (Middle Berth)
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES (2, 2, 12658, 1, 'JTJ', 'MAS', 2, '2026-11-10', 'Confirmed', '2026-11-01 08:05:00');
UPDATE Seat SET Status = 'Occupied' WHERE SeatID = 2;

-- PNR 3: Rahul Verma -> S1-3 (Upper Berth)
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES (3, 3, 12658, 1, 'SBC', 'MAS', 3, '2026-11-10', 'Confirmed', '2026-11-01 08:10:00');
UPDATE Seat SET Status = 'Occupied' WHERE SeatID = 3;

-- PNR 4: Sunita Patel -> S1-4 (Lower Berth)
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES (4, 4, 12658, 1, 'SBC', 'JTJ', 4, '2026-11-10', 'Confirmed', '2026-11-01 08:15:00');
UPDATE Seat SET Status = 'Occupied' WHERE SeatID = 4;

-- PNR 5: Amit Shah -> S1-5 (Middle Berth)
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES (5, 5, 12658, 1, 'JTJ', 'KPD', 5, '2026-11-10', 'Confirmed', '2026-11-01 08:20:00');
UPDATE Seat SET Status = 'Occupied' WHERE SeatID = 5;

-- PNR 6: Sneha Reddy -> S1-6 (Upper Berth)
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES (6, 6, 12658, 1, 'SBC', 'MAS', 6, '2026-11-10', 'Confirmed', '2026-11-01 08:25:00');
UPDATE Seat SET Status = 'Occupied' WHERE SeatID = 6;


-- [AC CLASS - ClassID 2: A1-1 and A1-2 Confirmed, A1-3 and A1-4 Available]
-- PNR 7: Priya Nair -> A1-1 (SeatID 7)
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES (7, 10, 12658, 2, 'SBC', 'MAS', 7, '2026-11-10', 'Confirmed', '2026-11-01 08:30:00');
UPDATE Seat SET Status = 'Occupied' WHERE SeatID = 7;

-- PNR 8: Vikram Malhotra -> A1-2 (SeatID 8)
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES (8, 11, 12658, 2, 'SBC', 'MAS', 8, '2026-11-10', 'Confirmed', '2026-11-01 08:35:00');
UPDATE Seat SET Status = 'Occupied' WHERE SeatID = 8;


-- ---------------------------------------------------------------------
-- 4. INSERT WAITING LIST PASSENGERS (Sleeper is Full -> Auto-Waitlisted)
-- ---------------------------------------------------------------------

-- WL 1 (Sleeper): Arjun Mehta (PNR 9)
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES (9, 7, 12658, 1, 'SBC', 'KPD', NULL, '2026-11-10', 'Waitlisted', '2026-11-01 09:00:00');

-- WL 2 (Sleeper): Kiran Shetty (PNR 10)
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES (10, 8, 12658, 1, 'SBC', 'JTJ', NULL, '2026-11-10', 'Waitlisted', '2026-11-01 09:15:00');

-- WL 3 (Sleeper): Pooja Hegde (PNR 11)
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES (11, 9, 12658, 1, 'SBC', 'MAS', NULL, '2026-11-10', 'Waitlisted', '2026-11-01 09:30:00');

-- WL 1 (AC Class): Rajesh Khanna (PNR 12)
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES (12, 12, 12658, 2, 'SBC', 'MAS', NULL, '2026-11-10', 'Waitlisted', '2026-11-01 09:45:00');


-- ---------------------------------------------------------------------
-- 5. INSERT PAYMENTS FOR CONFIRMED BOOKINGS
-- ---------------------------------------------------------------------
INSERT INTO Payment (PNR, Amount, Mode, Status) VALUES
(1, 125.00, 'UPI',  'Success'),
(2, 75.00,  'Card', 'Success'),
(3, 175.00, 'UPI',  'Success'),
(4, 100.00, 'Cash', 'Success'),
(5, 25.00,  'UPI',  'Success'),
(6, 175.00, 'Card', 'Success'),
(7, 525.00, 'UPI',  'Success'),
(8, 525.00, 'Card', 'Success');


-- =====================================================================
-- 6. SQL QUERIES TO SHOW MA'AM IN MYSQL WORKBENCH
-- =====================================================================

-- QUERY A: SHOW ALL CONFIRMED PASSENGERS (IRCTC Reservation Chart)
-- Shows: PNR, Name, Age, Gender, Coach, Seat, Class, Route, Status
SELECT 
    b.PNR,
    p.Name AS PassengerName,
    CONCAT(p.Age, ' / ', p.Gender) AS Age_Sex,
    sc.ClassType,
    s.CoachNo,
    s.SeatNo,
    CONCAT(b.BoardingStation, ' -> ', b.ExitStation) AS Route,
    b.Status,
    b.BookingTime
FROM Booking b
JOIN Passenger p  ON b.PassengerID = p.PassengerID
JOIN Seat s       ON b.SeatID = s.SeatID
JOIN SeatClass sc ON b.ClassID = sc.ClassID
WHERE b.Status = 'Confirmed' AND b.TrainNo = 12658
ORDER BY sc.ClassType DESC, s.CoachNo, s.SeatNo;


-- QUERY B: SHOW ALL WAITING LIST PASSENGERS IN FIFO PRIORITY ORDER
-- Shows: WL Priority Number, PNR, Name, Class, Route, Booking Time
SELECT 
    ROW_NUMBER() OVER (PARTITION BY b.ClassID ORDER BY b.BookingTime ASC) AS WL_Position,
    b.PNR,
    p.Name AS PassengerName,
    sc.ClassType,
    CONCAT(b.BoardingStation, ' -> ', b.ExitStation) AS Route,
    b.BookingTime,
    b.Status
FROM Booking b
JOIN Passenger p  ON b.PassengerID = p.PassengerID
JOIN SeatClass sc ON b.ClassID = sc.ClassID
WHERE b.Status = 'Waitlisted' AND b.TrainNo = 12658
ORDER BY b.ClassID, b.BookingTime ASC;


-- QUERY C: SHOW TOTAL SEAT STATUS PER CLASS (PHYSICAL INVENTORY)
SELECT 
    sc.ClassType,
    s.CoachNo,
    COUNT(s.SeatID) AS TotalSeats,
    SUM(CASE WHEN s.Status = 'Occupied' THEN 1 ELSE 0 END) AS OccupiedSeats,
    SUM(CASE WHEN s.Status = 'Available' THEN 1 ELSE 0 END) AS AvailableSeats
FROM Seat s
JOIN SeatClass sc ON s.ClassID = sc.ClassID
WHERE sc.TrainNo = 12658
GROUP BY sc.ClassType, s.CoachNo;

