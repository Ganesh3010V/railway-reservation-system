-- =====================================================================
--
-- =====================================================================

DROP DATABASE IF EXISTS railway_db;
CREATE DATABASE railway_db;
USE railway_db;

-- ---------------------------------------------------------------------
-- 1. PASSENGER
-- ---------------------------------------------------------------------
CREATE TABLE Passenger (
    PassengerID INT AUTO_INCREMENT PRIMARY KEY,
    Name        VARCHAR(80)  NOT NULL,
    Age         INT          NOT NULL CHECK (Age > 0 AND Age < 120),
    Gender      ENUM('M','F','O') NOT NULL,
    Contact     VARCHAR(15)  NOT NULL
);

-- ---------------------------------------------------------------------
-- 2. TRAIN
-- ---------------------------------------------------------------------
CREATE TABLE Train (
    TrainNo     INT PRIMARY KEY,
    TrainName   VARCHAR(80) NOT NULL,
    Source      VARCHAR(60) NOT NULL,
    Destination VARCHAR(60) NOT NULL
);

-- ---------------------------------------------------------------------
-- 3. STATION
-- ---------------------------------------------------------------------
CREATE TABLE Station (
    StationCode VARCHAR(10) PRIMARY KEY,
    StationName VARCHAR(80) NOT NULL,
    City        VARCHAR(60) NOT NULL
);

-- ---------------------------------------------------------------------
-- 4. ROUTESTATION (weak entity - depends on Train)
--    Ordered stops for a train; SeqNo + TrainNo together identify a
--    stop uniquely within a train's route.
-- ---------------------------------------------------------------------
CREATE TABLE RouteStation (
    RouteID             INT AUTO_INCREMENT PRIMARY KEY,
    TrainNo             INT NOT NULL,
    StationCode         VARCHAR(10) NOT NULL,
    SeqNo               INT NOT NULL,
    DistanceFromOrigin  INT NOT NULL,
    FOREIGN KEY (TrainNo) REFERENCES Train(TrainNo) ON DELETE CASCADE,
    FOREIGN KEY (StationCode) REFERENCES Station(StationCode),
    UNIQUE (TrainNo, SeqNo),
    UNIQUE (TrainNo, StationCode)
);

-- ---------------------------------------------------------------------
-- 5. SEATCLASS
-- ---------------------------------------------------------------------
CREATE TABLE SeatClass (
    ClassID     INT AUTO_INCREMENT PRIMARY KEY,
    TrainNo     INT NOT NULL,
    ClassType   ENUM('Sleeper','AC','General') NOT NULL,
    FarePerKm   DECIMAL(6,2) NOT NULL,
    TotalSeats  INT NOT NULL,
    FOREIGN KEY (TrainNo) REFERENCES Train(TrainNo) ON DELETE CASCADE,
    UNIQUE (TrainNo, ClassType)
);

-- ---------------------------------------------------------------------
-- 6. SEAT  (physical seat inventory per class)
-- ---------------------------------------------------------------------
CREATE TABLE Seat (
    SeatID   INT AUTO_INCREMENT PRIMARY KEY,
    ClassID  INT NOT NULL,
    CoachNo  VARCHAR(10) NOT NULL,
    SeatNo   INT NOT NULL,
    Status   ENUM('Available','Occupied') NOT NULL DEFAULT 'Available',
    FOREIGN KEY (ClassID) REFERENCES SeatClass(ClassID) ON DELETE CASCADE,
    UNIQUE (ClassID, CoachNo, SeatNo)
);

-- ---------------------------------------------------------------------
-- 7. BOOKING  (PNR level; boarding/exit stations give multi-leg support)
-- ---------------------------------------------------------------------
CREATE TABLE Booking (
    PNR             INT AUTO_INCREMENT PRIMARY KEY,
    PassengerID     INT NOT NULL,
    TrainNo         INT NOT NULL,
    ClassID         INT NOT NULL,
    BoardingStation VARCHAR(10) NOT NULL,
    ExitStation     VARCHAR(10) NOT NULL,
    SeatID          INT NULL,
    JourneyDate     DATE NOT NULL,
    Status          ENUM('Confirmed','Waitlisted','Cancelled') NOT NULL DEFAULT 'Waitlisted',
    BookingTime     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PassengerID) REFERENCES Passenger(PassengerID),
    FOREIGN KEY (TrainNo) REFERENCES Train(TrainNo),
    FOREIGN KEY (ClassID) REFERENCES SeatClass(ClassID),
    FOREIGN KEY (BoardingStation) REFERENCES Station(StationCode),
    FOREIGN KEY (ExitStation) REFERENCES Station(StationCode),
    FOREIGN KEY (SeatID) REFERENCES Seat(SeatID),
    CHECK (BoardingStation <> ExitStation)
);

-- ---------------------------------------------------------------------
-- 8. PAYMENT
-- ---------------------------------------------------------------------
CREATE TABLE Payment (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    PNR       INT NOT NULL,
    Amount    DECIMAL(8,2) NOT NULL,
    Mode      ENUM('UPI','Card','Cash') NOT NULL,
    Status    ENUM('Success','Pending','Failed') NOT NULL DEFAULT 'Pending',
    PaidOn    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PNR) REFERENCES Booking(PNR) ON DELETE CASCADE
);
USE railway_db;

-- ---------------- STATION ----------------
INSERT INTO Station VALUES
('SBC', 'KSR Bengaluru', 'Bangalore'),
('JTJ', 'Jolarpettai',   'Jolarpettai'),
('KPD', 'Katpadi',       'Vellore'),
('MAS', 'Chennai Central','Chennai');

-- ---------------- TRAIN ----------------
INSERT INTO Train VALUES
(12658, 'Bengaluru Mail', 'SBC', 'MAS');

-- ---------------- ROUTESTATION ----------------
-- Order: SBC(0) -> JTJ(200) -> KPD(250) -> MAS(350)
INSERT INTO RouteStation (TrainNo, StationCode, SeqNo, DistanceFromOrigin) VALUES
(12658, 'SBC', 1, 0),
(12658, 'JTJ', 2, 200),
(12658, 'KPD', 3, 250),
(12658, 'MAS', 4, 350);

-- ---------------- SEATCLASS ----------------
INSERT INTO SeatClass (TrainNo, ClassType, FarePerKm, TotalSeats) VALUES
(12658, 'Sleeper', 0.50, 6),
(12658, 'AC',      1.50, 4);

-- ---------------- SEAT (physical inventory, small set for demo) ----------------
-- ClassID 1 = Sleeper, ClassID 2 = AC (per AUTO_INCREMENT order above)
INSERT INTO Seat (ClassID, CoachNo, SeatNo) VALUES
(1, 'S1', 1), (1, 'S1', 2), (1, 'S1', 3), (1, 'S1', 4), (1, 'S1', 5), (1, 'S1', 6),
(2, 'A1', 1), (2, 'A1', 2), (2, 'A1', 3), (2, 'A1', 4);

-- ---------------- PASSENGER ----------------
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

-- ---------------- BOOKING (Sample Confirmed & Waitlisted) ----------------
-- [SLEEPER CLASS - S1-1 to S1-6] -> All 6 Seats Occupied
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES 
(1, 1, 12658, 1, 'SBC', 'KPD', 1, '2026-11-10', 'Confirmed', '2026-11-01 08:00:00'),
(2, 2, 12658, 1, 'JTJ', 'MAS', 2, '2026-11-10', 'Confirmed', '2026-11-01 08:05:00'),
(3, 3, 12658, 1, 'SBC', 'MAS', 3, '2026-11-10', 'Confirmed', '2026-11-01 08:10:00'),
(4, 4, 12658, 1, 'SBC', 'JTJ', 4, '2026-11-10', 'Confirmed', '2026-11-01 08:15:00'),
(5, 5, 12658, 1, 'JTJ', 'KPD', 5, '2026-11-10', 'Confirmed', '2026-11-01 08:20:00'),
(6, 6, 12658, 1, 'SBC', 'MAS', 6, '2026-11-10', 'Confirmed', '2026-11-01 08:25:00');

UPDATE Seat SET Status='Occupied' WHERE SeatID IN (1, 2, 3, 4, 5, 6);

-- [AC CLASS - A1-1 and A1-2 Confirmed, A1-3 and A1-4 Available]
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES 
(7, 10, 12658, 2, 'SBC', 'MAS', 7, '2026-11-10', 'Confirmed', '2026-11-01 08:30:00'),
(8, 11, 12658, 2, 'SBC', 'MAS', 8, '2026-11-10', 'Confirmed', '2026-11-01 08:35:00');

UPDATE Seat SET Status='Occupied' WHERE SeatID IN (7, 8);

-- [WAITING LIST - Sleeper is Full, so these passengers are Waitlisted]
INSERT INTO Booking (PNR, PassengerID, TrainNo, ClassID, BoardingStation, ExitStation, SeatID, JourneyDate, Status, BookingTime)
VALUES 
(9,  7, 12658, 1, 'SBC', 'KPD', NULL, '2026-11-10', 'Waitlisted', '2026-11-01 09:00:00'),
(10, 8, 12658, 1, 'SBC', 'JTJ', NULL, '2026-11-10', 'Waitlisted', '2026-11-01 09:15:00'),
(11, 9, 12658, 1, 'SBC', 'MAS', NULL, '2026-11-10', 'Waitlisted', '2026-11-01 09:30:00'),
(12, 12, 12658, 2, 'SBC', 'MAS', NULL, '2026-11-10', 'Waitlisted', '2026-11-01 09:45:00');

-- ---------------- PAYMENT (for confirmed bookings) ----------------
INSERT INTO Payment (PNR, Amount, Mode, Status) VALUES
(1, 125.00, 'UPI',  'Success'),
(2, 75.00,  'Card', 'Success'),
(3, 175.00, 'UPI',  'Success'),
(4, 100.00, 'Cash', 'Success'),
(5, 25.00,  'UPI',  'Success'),
(6, 175.00, 'Card', 'Success'),
(7, 525.00, 'UPI',  'Success'),
(8, 525.00, 'Card', 'Success');
USE railway_db;

-- =====================================================================
-- TRIGGER: trg_free_seat_after_cancel
-- Fires when a Booking's status changes to 'Cancelled'.
-- Frees up the physical seat in the Seat table.
--
-- Note: MySQL/MariaDB does not allow a trigger to UPDATE the same table
-- that fired it (Booking), so this trigger only touches the Seat table.
-- The waitlist PROMOTION logic (which needs to update other rows in
-- Booking) is handled by the CancelBooking stored procedure below —
-- this is the correct, standard way to structure this in MySQL.
-- =====================================================================
DELIMITER $$

CREATE TRIGGER trg_free_seat_after_cancel
AFTER UPDATE ON Booking
FOR EACH ROW
BEGIN
    IF NEW.Status = 'Cancelled' AND OLD.Status <> 'Cancelled' AND OLD.SeatID IS NOT NULL THEN
        UPDATE Seat SET Status = 'Available' WHERE SeatID = OLD.SeatID;
    END IF;
END$$

DELIMITER ;


-- =====================================================================
-- STORED PROCEDURE 1: GenerateBill
-- Calculates fare = distance(boarding -> exit) x FarePerKm for the
-- booking's class, and inserts a Payment row for it.
-- =====================================================================
DELIMITER $$

CREATE PROCEDURE GenerateBill(IN p_pnr INT, IN p_mode VARCHAR(10))
BEGIN
    DECLARE v_trainno INT;
    DECLARE v_classid INT;
    DECLARE v_board VARCHAR(10);
    DECLARE v_exit VARCHAR(10);
    DECLARE v_dist_board INT;
    DECLARE v_dist_exit INT;
    DECLARE v_fareperkm DECIMAL(6,2);
    DECLARE v_fare DECIMAL(8,2);

    SELECT TrainNo, ClassID, BoardingStation, ExitStation
      INTO v_trainno, v_classid, v_board, v_exit
      FROM Booking WHERE PNR = p_pnr;

    SELECT DistanceFromOrigin INTO v_dist_board
      FROM RouteStation WHERE TrainNo = v_trainno AND StationCode = v_board;

    SELECT DistanceFromOrigin INTO v_dist_exit
      FROM RouteStation WHERE TrainNo = v_trainno AND StationCode = v_exit;

    SELECT FarePerKm INTO v_fareperkm
      FROM SeatClass WHERE ClassID = v_classid;

    SET v_fare = (v_dist_exit - v_dist_board) * v_fareperkm;

    INSERT INTO Payment (PNR, Amount, Mode, Status)
    VALUES (p_pnr, v_fare, p_mode, 'Success');

    SELECT v_fare AS CalculatedFare;
END$$

DELIMITER ;


-- =====================================================================
-- STORED PROCEDURE 2: CancelBooking
-- Cancels a booking, then finds the EARLIEST waitlisted booking on the
-- same train/class whose travel segment OVERLAPS the segment just freed,
-- and auto-promotes it to Confirmed with the freed seat.
--
-- Segment overlap between (b1,e1) and (b2,e2), using RouteStation
-- SeqNo, is: b1 < e2 AND b2 < e1
-- =====================================================================
DELIMITER $$

CREATE PROCEDURE CancelBooking(IN p_pnr INT)
BEGIN
    DECLARE v_trainno INT;
    DECLARE v_classid INT;
    DECLARE v_seatid INT;
    DECLARE v_freed_board_seq INT;
    DECLARE v_freed_exit_seq INT;

    DECLARE v_wait_pnr INT;
    DECLARE v_wait_board_seq INT;
    DECLARE v_wait_exit_seq INT;

    DECLARE done INT DEFAULT 0;

    -- cursor over waitlisted bookings for same train & class, earliest first
    DECLARE wl_cursor CURSOR FOR
        SELECT b.PNR,
               rs1.SeqNo AS BoardSeq,
               rs2.SeqNo AS ExitSeq
          FROM Booking b
          JOIN RouteStation rs1 ON rs1.TrainNo = b.TrainNo AND rs1.StationCode = b.BoardingStation
          JOIN RouteStation rs2 ON rs2.TrainNo = b.TrainNo AND rs2.StationCode = b.ExitStation
         WHERE b.TrainNo = v_trainno
           AND b.ClassID = v_classid
           AND b.Status = 'Waitlisted'
         ORDER BY b.BookingTime ASC;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    -- get details of the booking being cancelled
    SELECT TrainNo, ClassID, SeatID INTO v_trainno, v_classid, v_seatid
      FROM Booking WHERE PNR = p_pnr;

    SELECT rs1.SeqNo, rs2.SeqNo INTO v_freed_board_seq, v_freed_exit_seq
      FROM Booking b
      JOIN RouteStation rs1 ON rs1.TrainNo = b.TrainNo AND rs1.StationCode = b.BoardingStation
      JOIN RouteStation rs2 ON rs2.TrainNo = b.TrainNo AND rs2.StationCode = b.ExitStation
     WHERE b.PNR = p_pnr;

    -- cancel it (this fires trg_free_seat_after_cancel, which frees the Seat row)
    UPDATE Booking SET Status = 'Cancelled' WHERE PNR = p_pnr;

    -- only look for a replacement if a seat was actually freed
    IF v_seatid IS NOT NULL THEN
        OPEN wl_cursor;

        promote_loop: LOOP
            FETCH wl_cursor INTO v_wait_pnr, v_wait_board_seq, v_wait_exit_seq;
            IF done = 1 THEN
                LEAVE promote_loop;
            END IF;

            -- overlap check: freed segment [board,exit) intersects waitlisted segment
            IF v_wait_board_seq < v_freed_exit_seq AND v_freed_board_seq < v_wait_exit_seq THEN
                UPDATE Booking
                   SET Status = 'Confirmed', SeatID = v_seatid
                 WHERE PNR = v_wait_pnr;

                UPDATE Seat SET Status = 'Occupied' WHERE SeatID = v_seatid;

                LEAVE promote_loop;  -- only promote the first match
            END IF;
        END LOOP;

        CLOSE wl_cursor;
    END IF;
END$$

