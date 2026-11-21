USE railway_db;

-- =====================================================================
-- ADDITIONAL SAMPLE DATA for Railway Reservation System
-- Adds more trains, stations, routes to demonstrate a richer system
-- =====================================================================

-- Additional Stations
INSERT INTO Station VALUES
('MYS', 'Mysuru Junction', 'Mysuru'),
('HUB', 'Hubballi Junction', 'Hubballi'),
('SC',  'Secunderabad Junction', 'Hyderabad'),
('PUNE','Pune Junction', 'Pune'),
('BCT', 'Mumbai Central', 'Mumbai'),
('TVC', 'Thiruvananthapuram Central', 'Thiruvananthapuram'),
('ERS', 'Ernakulam Junction', 'Kochi'),
('MDU', 'Madurai Junction', 'Madurai');

-- Additional Trains
INSERT INTO Train VALUES
(12007, 'Shatabdi Express',  'SBC', 'MYS'),
(17301, 'Chalukya Express',  'SBC', 'BCT'),
(12626, 'Kerala Express',    'MAS', 'TVC');

-- Routes: Shatabdi Express (SBC -> MYS)
INSERT INTO RouteStation (TrainNo, StationCode, SeqNo, DistanceFromOrigin) VALUES
(12007, 'SBC', 1, 0),
(12007, 'MYS', 2, 139);

-- Routes: Chalukya Express (SBC -> HUB -> PUNE -> BCT)
INSERT INTO RouteStation (TrainNo, StationCode, SeqNo, DistanceFromOrigin) VALUES
(17301, 'SBC', 1, 0),
(17301, 'HUB', 2, 400),
(17301, 'PUNE',3, 840),
(17301, 'BCT', 4, 1000);

-- Routes: Kerala Express (MAS -> MDU -> ERS -> TVC)
INSERT INTO RouteStation (TrainNo, StationCode, SeqNo, DistanceFromOrigin) VALUES
(12626, 'MAS', 1, 0),
(12626, 'MDU', 2, 460),
(12626, 'ERS', 3, 600),
(12626, 'TVC', 4, 780);

-- Seat Classes: Shatabdi Express
INSERT INTO SeatClass (TrainNo, ClassType, FarePerKm, TotalSeats) VALUES
(12007, 'AC',      2.00, 4),
(12007, 'General', 0.30, 6);

-- Seat Classes: Chalukya Express
INSERT INTO SeatClass (TrainNo, ClassType, FarePerKm, TotalSeats) VALUES
(17301, 'Sleeper', 0.50, 6),
(17301, 'AC',      1.50, 4),
(17301, 'General', 0.25, 8);

-- Seat Classes: Kerala Express
INSERT INTO SeatClass (TrainNo, ClassType, FarePerKm, TotalSeats) VALUES
(12626, 'Sleeper', 0.45, 6),
(12626, 'AC',      1.40, 4);

-- Seats for Shatabdi AC (ClassID=3)
INSERT INTO Seat (ClassID, CoachNo, SeatNo) VALUES
(3,'C1',1),(3,'C1',2),(3,'C1',3),(3,'C1',4);
-- Seats for Shatabdi General (ClassID=4)
INSERT INTO Seat (ClassID, CoachNo, SeatNo) VALUES
(4,'G1',1),(4,'G1',2),(4,'G1',3),(4,'G1',4),(4,'G1',5),(4,'G1',6);
-- Seats for Chalukya Sleeper (ClassID=5)
INSERT INTO Seat (ClassID, CoachNo, SeatNo) VALUES
(5,'S1',1),(5,'S1',2),(5,'S1',3),(5,'S1',4),(5,'S1',5),(5,'S1',6);
-- Seats for Chalukya AC (ClassID=6)
INSERT INTO Seat (ClassID, CoachNo, SeatNo) VALUES
(6,'A1',1),(6,'A1',2),(6,'A1',3),(6,'A1',4);
-- Seats for Chalukya General (ClassID=7)
INSERT INTO Seat (ClassID, CoachNo, SeatNo) VALUES
(7,'G1',1),(7,'G1',2),(7,'G1',3),(7,'G1',4),(7,'G1',5),(7,'G1',6),(7,'G1',7),(7,'G1',8);
-- Seats for Kerala Sleeper (ClassID=8)
INSERT INTO Seat (ClassID, CoachNo, SeatNo) VALUES
(8,'S1',1),(8,'S1',2),(8,'S1',3),(8,'S1',4),(8,'S1',5),(8,'S1',6);
-- Seats for Kerala AC (ClassID=9)
INSERT INTO Seat (ClassID, CoachNo, SeatNo) VALUES
(9,'A1',1),(9,'A1',2),(9,'A1',3),(9,'A1',4);

-- Additional Passengers
INSERT INTO Passenger (Name, Age, Gender, Contact) VALUES
('Ravi Sharma',   45, 'M', '9900077777'),
('Meera Joshi',   32, 'F', '9900088888'),
('Anil Kumar',    55, 'M', '9900099999'),
('Lakshmi Devi',  48, 'F', '9900011100');
