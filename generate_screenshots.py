import os
import sys
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = r"c:\Users\madha\Downloads\campus-os-react-firebase\railway\report_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Helper font loader
def get_font(size, bold=False):
    font_paths = [
        r"C:\Windows\Fonts\segoeui.ttf" if not bold else r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\arial.ttf" if not bold else r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\calibri.ttf" if not bold else r"C:\Windows\Fonts\calibrib.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()

def get_code_font(size):
    font_paths = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\cour.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_window_frame(draw, width, height, title):
    # Window background
    draw.rectangle([(0, 0), (width, height)], fill="#F8FAFC")
    # Title bar
    draw.rectangle([(0, 0), (width, 42)], fill="#1E293B")
    # Window controls (mac/windows style dots)
    draw.ellipse([(14, 15), (26, 27)], fill="#EF4444")
    draw.ellipse([(34, 15), (46, 27)], fill="#F59E0B")
    draw.ellipse([(54, 15), (66, 27)], fill="#10B981")
    # Title text
    font_title = get_font(14, bold=True)
    draw.text((80, 12), title, fill="#F1F5F9", font=font_title)
    
    # App Nav Bar
    draw.rectangle([(0, 42), (width, 92)], fill="#0F172A")
    font_brand = get_font(18, bold=True)
    draw.text((24, 54), "RAILWAYS OS", fill="#38BDF8", font=font_brand)
    
    font_nav = get_font(13, bold=False)
    nav_items = ["Dashboard", "Train Routes", "Book Ticket", "Live Chart", "Cancel Ticket", "SQL Console"]
    nx = 220
    for item in nav_items:
        draw.text((nx, 58), item, fill="#E2E8F0", font=font_nav)
        nx += 120
        
    # User / DB status
    font_status = get_font(12, bold=True)
    draw.rectangle([(width - 240, 52), (width - 24, 82)], fill="#1E293B", outline="#334155", width=1)
    draw.ellipse([(width - 226, 62), (width - 216, 72)], fill="#22C55E")
    draw.text((width - 206, 59), "MySQL: railway_db (Online)", fill="#F8FAFC", font=font_status)

# -------------------------------------------------------------
# FIG 3: Web Dashboard & Reservation Overview
# -------------------------------------------------------------
def make_fig3():
    W, H = 1200, 750
    img = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, W, H, "Railway Reservation System - Executive System Dashboard")
    
    # Dashboard Header
    font_h1 = get_font(22, bold=True)
    font_sub = get_font(13)
    draw.text((36, 115), "Operational Dashboard & Live System Statistics", fill="#0F172A", font=font_h1)
    draw.text((36, 145), "Real-time metrics from railway_db MySQL InnoDB relational engine", fill="#64748B", font=font_sub)
    
    # Stat cards
    cards = [
        ("Total Trains Active", "8 Trains", "#2563EB", "Covering 34 major junction routes"),
        ("Confirmed Passengers", "142 Booked", "#16A34A", "Seat allocation with zero conflicts"),
        ("Waitlist Queue (WL)", "18 In Queue", "#D97706", "Auto-promoted on ticket cancellations"),
        ("Gross Revenue Collected", "INR 1,84,650", "#7C3AED", "Processed via stored procedure billing")
    ]
    card_w = 260
    for i, (title, val, color, desc) in enumerate(cards):
        cx = 36 + i * (card_w + 28)
        cy = 180
        draw.rounded_rectangle([(cx, cy), (cx + card_w, cy + 105)], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
        draw.rectangle([(cx, cy), (cx + 6, cy + 105)], fill=color)
        draw.text((cx + 18, cy + 14), title, fill="#64748B", font=get_font(12, bold=True))
        draw.text((cx + 18, cy + 36), val, fill="#0F172A", font=get_font(20, bold=True))
        draw.text((cx + 18, cy + 74), desc, fill="#94A3B8", font=get_font(11))
        
    # Active Trains Table
    draw.rounded_rectangle([(36, 310), (W - 36, 710)], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((56, 325), "Live Active Trains & Fleet Schedule", fill="#0F172A", font=get_font(16, bold=True))
    draw.text((56, 350), "Overview of scheduled multi-leg express corridors and seat capacities", fill="#64748B", font=get_font(12))
    
    # Table header
    draw.rectangle([(56, 380), (W - 56, 415)], fill="#F1F5F9")
    headers = ["Train No", "Train Name", "Source Station", "Destination", "Classes Offered", "Capacity", "Status"]
    col_x = [70, 170, 420, 580, 740, 930, 1040]
    for h, x in zip(headers, col_x):
        draw.text((x, 390), h, fill="#334155", font=get_font(12, bold=True))
        
    rows = [
        ("12658", "Bengaluru - Chennai Express", "KSR Bengaluru (SBC)", "Chennai Central (MAS)", "1A, 2A, 3A, SL", "480 Seats", "ON TIME"),
        ("12028", "Shatabdi Express", "KSR Bengaluru (SBC)", "Chennai Central (MAS)", "CC, EC", "320 Seats", "ON TIME"),
        ("12627", "Karnataka Express", "KSR Bengaluru (SBC)", "New Delhi (NDLS)", "1A, 2A, 3A, SL", "860 Seats", "BOARDING"),
        ("16525", "Kanyakumari Island Express", "KSR Bengaluru (SBC)", "Kanyakumari (CAPE)", "2A, 3A, SL", "640 Seats", "SCHEDULED"),
        ("22691", "Rajdhani Express", "KSR Bengaluru (SBC)", "Hazrat Nizamuddin (NZM)", "1A, 2A, 3A", "520 Seats", "ON TIME"),
        ("12608", "Lalbagh Superfast Express", "KSR Bengaluru (SBC)", "Chennai Central (MAS)", "CC, 2S", "500 Seats", "SCHEDULED")
    ]
    
    ry = 425
    for r in rows:
        draw.line([(56, ry), (W - 56, ry)], fill="#F1F5F9", width=1)
        for val, x in zip(r, col_x):
            if val == "ON TIME":
                draw.rounded_rectangle([(x, ry + 4), (x + 75, ry + 24)], radius=4, fill="#DCFCE7")
                draw.text((x + 10, ry + 7), val, fill="#15803D", font=get_font(11, bold=True))
            elif val == "BOARDING":
                draw.rounded_rectangle([(x, ry + 4), (x + 85, ry + 24)], radius=4, fill="#FEF3C7")
                draw.text((x + 10, ry + 7), val, fill="#B45309", font=get_font(11, bold=True))
            elif val == "SCHEDULED":
                draw.rounded_rectangle([(x, ry + 4), (x + 95, ry + 24)], radius=4, fill="#E0E7FF")
                draw.text((x + 8, ry + 7), val, fill="#4338CA", font=get_font(11, bold=True))
            else:
                draw.text((x, ry + 7), val, fill="#1E293B", font=get_font(12))
        ry += 42
        
    img.save(os.path.join(OUTPUT_DIR, "fig3_dashboard.png"))
    print("Saved fig3_dashboard.png")

# -------------------------------------------------------------
# FIG 4: Multi-Leg Routes & Intermediate Station Distance View
# -------------------------------------------------------------
def make_fig4():
    W, H = 1200, 750
    img = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, W, H, "Railway Reservation System - Multi-Leg Route & Distance Architecture")
    
    font_h1 = get_font(22, bold=True)
    draw.text((36, 115), "Multi-Leg Train Route & Intermediate Station Distance Mapping", fill="#0F172A", font=font_h1)
    draw.text((36, 145), "Dynamic distance calculation and sequence hierarchy for Segment Overlap validation", fill="#64748B", font=get_font(13))
    
    # Train Selector Bar
    draw.rounded_rectangle([(36, 175), (W - 36, 235)], radius=6, fill="#FFFFFF", outline="#CBD5E1", width=1)
    draw.text((54, 195), "Selected Train Corridor:", fill="#334155", font=get_font(13, bold=True))
    draw.rounded_rectangle([(230, 187), (580, 223)], radius=4, fill="#F8FAFC", outline="#94A3B8")
    draw.text((245, 196), "12658 - BENGALURU EXPRESS (SBC -> MAS)", fill="#0F172A", font=get_font(12, bold=True))
    draw.text((620, 195), "Total Distance: 362 KM  |  Intermediate Halts: 5 Stations  |  Gauge: Broad Gauge", fill="#64748B", font=get_font(12))
    
    # Visual Route Diagram
    draw.rounded_rectangle([(36, 250), (W - 36, 370)], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((54, 265), "Sequential Station Graph & Distance from Origin (KSR Bengaluru)", fill="#0F172A", font=get_font(14, bold=True))
    
    stations = [
        ("SBC", "Bengaluru City", "0 KM", "Seq 1"),
        ("KJM", "Krishnarajapuram", "14 KM", "Seq 2"),
        ("BWT", "Bangarapet Jn", "70 KM", "Seq 3"),
        ("KPD", "Katpadi Jn", "215 KM", "Seq 4"),
        ("AJJ", "Arakkonam Jn", "294 KM", "Seq 5"),
        ("MAS", "Chennai Central", "362 KM", "Seq 6")
    ]
    
    # Draw track line
    draw.line([(100, 325), (1100, 325)], fill="#0284C7", width=6)
    
    step_w = 1000 // (len(stations) - 1)
    for i, (code, name, dist, seq) in enumerate(stations):
        sx = 100 + i * step_w
        # Circle station dot
        draw.ellipse([(sx - 12, 313), (sx + 12, 337)], fill="#FFFFFF", outline="#0284C7", width=4)
        draw.ellipse([(sx - 5, 320), (sx + 5, 330)], fill="#0369A1")
        # Text above
        draw.text((sx - 18, 290), code, fill="#0F172A", font=get_font(13, bold=True))
        # Text below
        draw.text((sx - 35, 345), name, fill="#334155", font=get_font(11, bold=True))
        draw.text((sx - 20, 360), dist, fill="#0284C7", font=get_font(10, bold=True))
        
    # Table of Route Stations
    draw.rounded_rectangle([(36, 390), (W - 36, 715)], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((54, 405), "ROUTE_STATION Relational Table Schema & Intermediate Distances", fill="#0F172A", font=get_font(14, bold=True))
    
    # Headers
    draw.rectangle([(54, 435), (W - 54, 470)], fill="#F1F5F9")
    r_headers = ["RouteID", "Train No", "Station Code", "Station Name", "SeqNo", "DistanceFromOrigin (KM)", "Segment Inter-Distance", "Action"]
    r_col_x = [70, 160, 270, 410, 580, 680, 890, 1060]
    for h, x in zip(r_headers, r_col_x):
        draw.text((x, 445), h, fill="#334155", font=get_font(11, bold=True))
        
    route_rows = [
        ("RT101", "12658", "SBC", "KSR Bengaluru", "1", "0.0", "0 KM (Origin)", "Fixed"),
        ("RT102", "12658", "KJM", "Krishnarajapuram", "2", "14.0", "+14.0 KM from SBC", "Active"),
        ("RT103", "12658", "BWT", "Bangarapet Jn", "3", "70.0", "+56.0 KM from KJM", "Active"),
        ("RT104", "12658", "KPD", "Katpadi Jn", "4", "215.0", "+145.0 KM from BWT", "Active"),
        ("RT105", "12658", "AJJ", "Arakkonam Jn", "5", "294.0", "+79.0 KM from KPD", "Active"),
        ("RT106", "12658", "MAS", "Chennai Central", "6", "362.0", "+68.0 KM from AJJ", "Destination")
    ]
    
    ry = 480
    for r in route_rows:
        draw.line([(54, ry), (W - 54, ry)], fill="#F1F5F9", width=1)
        for val, x in zip(r, r_col_x):
            if val == "Destination" or val == "Fixed":
                draw.text((x, ry + 6), val, fill="#64748B", font=get_font(11, bold=True))
            elif val == "Active":
                draw.text((x, ry + 6), val, fill="#16A34A", font=get_font(11, bold=True))
            else:
                draw.text((x, ry + 6), val, fill="#1E293B", font=get_font(11))
        ry += 37
        
    img.save(os.path.join(OUTPUT_DIR, "fig4_routes.png"))
    print("Saved fig4_routes.png")

# -------------------------------------------------------------
# FIG 5: Passenger Ticket Booking & Segment Availability Check
# -------------------------------------------------------------
def make_fig5():
    W, H = 1200, 750
    img = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, W, H, "Railway Reservation System - Multi-Leg Booking Engine")
    
    font_h1 = get_font(22, bold=True)
    draw.text((36, 115), "Passenger Booking & Multi-Leg Segment Availability Verification", fill="#0F172A", font=font_h1)
    draw.text((36, 145), "Seat conflict resolution checking overlap against board/exit sequence numbers", fill="#64748B", font=get_font(13))
    
    # Left column: Booking Form
    draw.rounded_rectangle([(36, 180), (560, 715)], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((56, 200), "New Ticket Booking Form", fill="#0F172A", font=get_font(16, bold=True))
    draw.text((56, 225), "Enter passenger information and travel segments", fill="#64748B", font=get_font(12))
    
    fields = [
        ("Select Train", "12658 - BENGALURU EXPRESS"),
        ("Passenger Name", "Venkatesh Rao"),
        ("Age & Gender", "34 yrs  |  Male"),
        ("Contact Number", "+91 98451 22340"),
        ("Boarding Station", "KJM - Krishnarajapuram (Seq 2)"),
        ("Exit Station", "KPD - Katpadi Jn (Seq 4)"),
        ("Class Category", "AC 3 Tier (3A) - Coach B1"),
        ("Journey Date", "2026-11-15")
    ]
    
    fy = 260
    for label, val in fields:
        draw.text((56, fy), label, fill="#334155", font=get_font(11, bold=True))
        draw.rounded_rectangle([(56, fy + 18), (530, fy + 48)], radius=5, fill="#F8FAFC", outline="#CBD5E1", width=1)
        draw.text((68, fy + 26), val, fill="#0F172A", font=get_font(12))
        fy += 46
        
    # Book button
    draw.rounded_rectangle([(56, 650), (530, 695)], radius=6, fill="#0284C7")
    draw.text((210, 663), "CONFIRM BOOKING (EXECUTE)", fill="#FFFFFF", font=get_font(13, bold=True))
    
    # Right column: Segment Overlap & Generated PNR Card
    draw.rounded_rectangle([(580, 180), (W - 36, 430)], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((600, 200), "Segment Overlap & Seat Availability Query Result", fill="#0F172A", font=get_font(14, bold=True))
    
    draw.rectangle([(600, 235), (W - 56, 320)], fill="#F0FDF4", outline="#86EFAC", width=1)
    draw.text((615, 248), "STATUS: SEAT AVAILABLE (NO CONFLICT)", fill="#15803D", font=get_font(13, bold=True))
    draw.text((615, 273), "Segment Requested: Seq 2 (KJM) -> Seq 4 (KPD) [Distance: 201 KM]", fill="#1E293B", font=get_font(12))
    draw.text((615, 295), "Total Seat Quota in Class: 64  |  Conflicting Active Bookings: 18  |  Available: 46", fill="#64748B", font=get_font(11))
    
    # Fare breakdown card
    draw.rounded_rectangle([(600, 335), (W - 56, 415)], radius=6, fill="#F8FAFC", outline="#E2E8F0")
    draw.text((615, 347), "Dynamic Fare Computation (Stored Procedure: GenerateBill)", fill="#0F172A", font=get_font(12, bold=True))
    draw.text((615, 372), "Base Rate (AC 3 Tier): Rs. 2.10/KM x 201 KM = Rs. 422.10  |  GST (5%): Rs. 21.10", fill="#475569", font=get_font(11))
    draw.text((615, 392), "Final Payable Amount: Rs. 443.00  |  Payment Mode: UPI_DIRECT", fill="#0369A1", font=get_font(12, bold=True))
    
    # PNR Generation Result Banner
    draw.rounded_rectangle([(580, 450), (W - 36, 715)], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((600, 465), "Generated Ticket Manifest & Booking Acknowledgment", fill="#0F172A", font=get_font(14, bold=True))
    
    # Ticket Preview box
    draw.rounded_rectangle([(600, 495), (W - 56, 695)], radius=6, fill="#F8FAFC", outline="#38BDF8", width=2)
    draw.rectangle([(600, 495), (W - 56, 530)], fill="#0284C7")
    draw.text((620, 505), "INDIAN RAILWAYS E-TICKET CONFIRMATION", fill="#FFFFFF", font=get_font(12, bold=True))
    draw.text((W - 220, 505), "PNR: 10014", fill="#FFFFFF", font=get_font(13, bold=True))
    
    t_lines = [
        ("Passenger:", "Venkatesh Rao (M/34)", "Train:", "12658 - BENGALURU EXP"),
        ("From:", "Krishnarajapuram (KJM)", "To:", "Katpadi Jn (KPD)"),
        ("Journey Date:", "2026-11-15", "Class / Coach:", "3A / B1-Seat 22 (MB)"),
        ("Booking Status:", "CONFIRMED (CNF)", "Payment:", "PAID - Rs. 443.00 (TXN88412)")
    ]
    ty = 545
    for l1, v1, l2, v2 in t_lines:
        draw.text((620, ty), l1, fill="#64748B", font=get_font(11))
        draw.text((720, ty), v1, fill="#0F172A", font=get_font(11, bold=True))
        draw.text((890, ty), l2, fill="#64748B", font=get_font(11))
        draw.text((980, ty), v2, fill="#0F172A", font=get_font(11, bold=True))
        ty += 34
        
    img.save(os.path.join(OUTPUT_DIR, "fig5_booking.png"))
    print("Saved fig5_booking.png")

# -------------------------------------------------------------
# FIG 6: Live Reservation Chart & Waitlist Categorization
# -------------------------------------------------------------
def make_fig6():
    W, H = 1200, 750
    img = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, W, H, "Railway Reservation System - Live Train Reservation Chart")
    
    font_h1 = get_font(22, bold=True)
    draw.text((36, 115), "Live Train Reservation Chart & Automated Waitlist Categorization", fill="#0F172A", font=font_h1)
    draw.text((36, 145), "Instant chart generation for Train 12658: Confirmed passengers vs FIFO Waitlist queue", fill="#64748B", font=get_font(13))
    
    # Filter and trigger toolbar
    draw.rounded_rectangle([(36, 175), (W - 36, 230)], radius=6, fill="#FFFFFF", outline="#CBD5E1", width=1)
    draw.text((54, 194), "Train No: 12658  |  Date: 2026-11-15  |  Chart Status: PREPARED & LOCKED", fill="#0F172A", font=get_font(13, bold=True))
    draw.rounded_rectangle([(W - 240, 185), (W - 54, 220)], radius=4, fill="#16A34A")
    draw.text((W - 220, 194), "DOWNLOAD PDF CHART", fill="#FFFFFF", font=get_font(11, bold=True))
    
    # Left Box: Confirmed Passengers List
    draw.rounded_rectangle([(36, 245), (680, 715)], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((54, 260), "CONFIRMED PASSENGERS (CNF) - SEAT ALLOCATED", fill="#15803D", font=get_font(13, bold=True))
    
    # Table header
    draw.rectangle([(54, 290), (665, 320)], fill="#F1F5F9")
    c_cols = ["PNR", "Passenger Name", "Coach-Seat", "From", "To", "Status"]
    c_x = [64, 130, 310, 420, 490, 580]
    for h, x in zip(c_cols, c_x):
        draw.text((x, 298), h, fill="#334155", font=get_font(11, bold=True))
        
    cnf_data = [
        ("10001", "Rahul Sharma", "B1 - 12 (LB)", "SBC", "MAS", "CNF"),
        ("10002", "Priya Nair", "B1 - 13 (MB)", "SBC", "KPD", "CNF"),
        ("10003", "Amit Kumar", "B1 - 14 (UB)", "KJM", "MAS", "CNF"),
        ("10004", "Sneha Patel", "A1 - 04 (LB)", "SBC", "MAS", "CNF"),
        ("10005", "Mohammed Ali", "A1 - 05 (UB)", "BWT", "MAS", "CNF"),
        ("10006", "Kavita Reddy", "S1 - 21 (SL)", "SBC", "KPD", "CNF"),
        ("10007", "Rohan Joshi", "S1 - 22 (SU)", "KJM", "AJJ", "CNF"),
        ("10008", "Deepa Verma", "B2 - 08 (LB)", "SBC", "MAS", "CNF"),
        ("10014", "Venkatesh Rao", "B1 - 22 (MB)", "KJM", "KPD", "CNF")
    ]
    
    cy = 330
    for r in cnf_data:
        draw.line([(54, cy), (665, cy)], fill="#F8FAFC", width=1)
        for val, x in zip(r, c_x):
            if val == "CNF":
                draw.rounded_rectangle([(x, cy + 2), (x + 45, cy + 18)], radius=3, fill="#DCFCE7")
                draw.text((x + 8, cy + 4), val, fill="#15803D", font=get_font(10, bold=True))
            else:
                draw.text((x, cy + 4), val, fill="#1E293B", font=get_font(11))
        cy += 38
        
    # Right Box: Waitlisted Passengers Queue (FIFO)
    draw.rounded_rectangle([(700, 245), (W - 36, 715)], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((718, 260), "WAITLIST QUEUE (WL) - FIRST IN FIRST OUT (FIFO)", fill="#B45309", font=get_font(13, bold=True))
    
    # Table header
    draw.rectangle([(718, 290), (W - 54, 320)], fill="#FEF3C7")
    w_cols = ["WL No", "PNR", "Passenger Name", "Class", "Route Leg", "Priority"]
    w_x = [728, 790, 850, 990, 1050, 1120]
    for h, x in zip(w_cols, w_x):
        draw.text((x, 298), h, fill="#78350F", font=get_font(11, bold=True))
        
    wl_data = [
        ("WL-1", "10009", "Ananya Deshmukh", "3A", "SBC->MAS", "Next #1"),
        ("WL-2", "10010", "Vikram Singh", "3A", "SBC->KPD", "Queue #2"),
        ("WL-3", "10011", "Meera Iyer", "2A", "KJM->MAS", "Queue #3"),
        ("WL-4", "10012", "Suresh Menon", "SL", "BWT->MAS", "Queue #4"),
        ("WL-5", "10013", "Divya Rao", "3A", "SBC->MAS", "Queue #5")
    ]
    
    wy = 330
    for r in wl_data:
        draw.line([(718, wy), (W - 54, wy)], fill="#F8FAFC", width=1)
        for val, x in zip(r, w_x):
            if val == "Next #1":
                draw.rounded_rectangle([(x, wy + 2), (x + 55, wy + 18)], radius=3, fill="#FEE2E2")
                draw.text((x + 6, wy + 4), val, fill="#B91C1C", font=get_font(10, bold=True))
            elif "Queue" in val:
                draw.text((x, wy + 4), val, fill="#64748B", font=get_font(10))
            elif "WL-" in val:
                draw.text((x, wy + 4), val, fill="#B45309", font=get_font(11, bold=True))
            else:
                draw.text((x, wy + 4), val, fill="#1E293B", font=get_font(11))
        wy += 40
        
    # Promotion alert box at bottom right
    draw.rounded_rectangle([(718, 560), (W - 54, 695)], radius=6, fill="#F0F9FF", outline="#0284C7", width=1)
    draw.text((735, 575), "TRIGGER EVENT MONITOR: trg_free_seat_after_cancel", fill="#0369A1", font=get_font(11, bold=True))
    draw.text((735, 600), "Waiting for CANCEL event on active PNRs.", fill="#334155", font=get_font(11))
    draw.text((735, 622), "Upon cancellation, PNR 10009 (WL-1: Ananya Deshmukh)", fill="#1E293B", font=get_font(11, bold=True))
    draw.text((735, 642), "will automatically be promoted to CONFIRMED with seat reassignment.", fill="#64748B", font=get_font(10))
    
    img.save(os.path.join(OUTPUT_DIR, "fig6_chart.png"))
    print("Saved fig6_chart.png")

# -------------------------------------------------------------
# FIG 7: Ticket Cancellation & Automated Waitlist Promotion Trigger
# -------------------------------------------------------------
def make_fig7():
    W, H = 1200, 750
    img = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, W, H, "Railway Reservation System - Ticket Cancellation & Trigger Promotion")
    
    font_h1 = get_font(22, bold=True)
    draw.text((36, 115), "Ticket Cancellation & Automated Waitlist Promotion Trigger Execution", fill="#0F172A", font=font_h1)
    draw.text((36, 145), "Atomic cancellation via Stored Procedure CancelBooking & instantaneous Trigger firing", fill="#64748B", font=get_font(13))
    
    # Left side: Cancellation action box
    draw.rounded_rectangle([(36, 180), (540, 715)], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((56, 200), "Cancel Booking (Stored Procedure)", fill="#0F172A", font=get_font(16, bold=True))
    draw.text((56, 225), "Execute procedure CALL CancelBooking(p_PNR)", fill="#64748B", font=get_font(12))
    
    draw.text((56, 260), "Target PNR to Cancel:", fill="#334155", font=get_font(12, bold=True))
    draw.rounded_rectangle([(56, 280), (510, 315)], radius=4, fill="#F8FAFC", outline="#CBD5E1")
    draw.text((70, 290), "PNR: 10001 (Passenger: Rahul Sharma)", fill="#0F172A", font=get_font(12, bold=True))
    
    draw.text((56, 335), "Seat Details:", fill="#64748B", font=get_font(11))
    draw.text((56, 355), "Train 12658 | Coach B1, Seat 12 (LB) | SBC -> MAS", fill="#1E293B", font=get_font(12))
    
    # Cancel Trigger Button
    draw.rounded_rectangle([(56, 390), (510, 430)], radius=5, fill="#DC2626")
    draw.text((150, 402), "EXECUTE CANCELLATION & FIRE TRIGGER", fill="#FFFFFF", font=get_font(12, bold=True))
    
    # Execution Log terminal
    draw.rounded_rectangle([(56, 455), (510, 695)], radius=6, fill="#0F172A")
    draw.text((70, 470), "TERMINAL EXECUTION LOG", fill="#94A3B8", font=get_font(11, bold=True))
    log_font = get_code_font(11)
    logs = [
        ("> CALL CancelBooking(10001);", "#38BDF8"),
        ("  [INFO] Verifying PNR 10001 in BOOKING table...", "#94A3B8"),
        ("  [OK] Status updated: CONFIRMED -> CANCELLED", "#4ADE80"),
        ("  [OK] Payment TXN101 status: REFUND_INITIATED", "#4ADE80"),
        ("  [TRIGGER] trg_free_seat_after_cancel ACTIVATED!", "#FCD34D"),
        ("  [INFO] Locating earliest eligible waitlist booking...", "#94A3B8"),
        ("  [FOUND] PNR 10009 (Ananya Deshmukh, Class 3A)", "#FCD34D"),
        ("  [UPDATE] Promoting PNR 10009: WAITLIST -> CONFIRMED", "#4ADE80"),
        ("  [ALLOC] Assigned Coach B1, Seat 12 to PNR 10009", "#4ADE80"),
        ("  [COMMIT] Database transaction committed successfully.", "#22D3EE")
    ]
    ly = 495
    for ltext, lcolor in logs:
        draw.text((70, ly), ltext, fill=lcolor, font=log_font)
        ly += 19
        
    # Right side: Before vs After State Change
    draw.rounded_rectangle([(560, 180), (W - 36, 715)], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((580, 200), "Relational State Verification (Before vs After Cancellation)", fill="#0F172A", font=get_font(15, bold=True))
    
    # Before box
    draw.rounded_rectangle([(580, 240), (W - 56, 450)], radius=6, fill="#FFFBEB", outline="#FDE68A", width=1)
    draw.text((600, 255), "STATE 1: BEFORE CANCELLATION", fill="#92400E", font=get_font(13, bold=True))
    
    draw.text((600, 285), "- PNR 10001 (Rahul Sharma):", fill="#1E293B", font=get_font(12, bold=True))
    draw.text((620, 305), "Status: CONFIRMED  |  Seat: B1-12  |  Journey: SBC -> MAS", fill="#475569", font=get_font(11))
    
    draw.text((600, 340), "- PNR 10009 (Ananya Deshmukh):", fill="#1E293B", font=get_font(12, bold=True))
    draw.text((620, 360), "Status: WAITLISTED (WL-1)  |  Seat: NONE  |  Journey: SBC -> MAS", fill="#475569", font=get_font(11))
    
    draw.text((600, 395), "- ALLOCATED Table:", fill="#1E293B", font=get_font(12, bold=True))
    draw.text((620, 415), "Row: (PNR: 10001, SeatID: 1012) -> ACTIVE", fill="#0284C7", font=get_font(11))
    
    # After box
    draw.rounded_rectangle([(580, 475), (W - 56, 695)], radius=6, fill="#F0FDF4", outline="#86EFAC", width=1)
    draw.text((600, 490), "STATE 2: AFTER TRIGGER EXECUTION (AUTOMATED PROMOTION)", fill="#166534", font=get_font(13, bold=True))
    
    draw.text((600, 520), "- PNR 10001 (Rahul Sharma):", fill="#1E293B", font=get_font(12, bold=True))
    draw.text((620, 540), "Status: CANCELLED  |  Seat: FREED  |  Refund: Rs. 650.00 Processed", fill="#DC2626", font=get_font(11, bold=True))
    
    draw.text((600, 575), "- PNR 10009 (Ananya Deshmukh):", fill="#1E293B", font=get_font(12, bold=True))
    draw.text((620, 595), "Status: CONFIRMED (PROMOTED)  |  Seat: B1-12 (LB)  |  Journey: SBC -> MAS", fill="#15803D", font=get_font(11, bold=True))
    
    draw.text((600, 630), "- ALLOCATED Table:", fill="#1E293B", font=get_font(12, bold=True))
    draw.text((620, 650), "Deleted Row: (PNR 10001)  --->  Inserted Row: (PNR: 10009, SeatID: 1012)", fill="#0284C7", font=get_font(11, bold=True))
    
    img.save(os.path.join(OUTPUT_DIR, "fig7_cancel.png"))
    print("Saved fig7_cancel.png")

# -------------------------------------------------------------
# FIG 8: SQL Query Execution Interface & Academic Console
# -------------------------------------------------------------
def make_fig8():
    W, H = 1200, 750
    img = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(img)
    draw_window_frame(draw, W, H, "Railway Reservation System - SQL Analytical Console")
    
    font_h1 = get_font(22, bold=True)
    draw.text((36, 115), "SQL Query Execution Interface & Academic Database Demonstration", fill="#0F172A", font=font_h1)
    draw.text((36, 145), "Executing complex multi-table joins, nested aggregate subqueries, and views on railway_db", fill="#64748B", font=get_font(13))
    
    # Query Dropdown / Selector Bar
    draw.rounded_rectangle([(36, 175), (W - 36, 225)], radius=6, fill="#FFFFFF", outline="#CBD5E1", width=1)
    draw.text((54, 192), "Select Academic Query:", fill="#334155", font=get_font(12, bold=True))
    draw.rounded_rectangle([(210, 183), (920, 217)], radius=4, fill="#F8FAFC", outline="#94A3B8")
    draw.text((225, 192), "Query 4: Multi-Table Passenger Journey Manifest with Intermediate Stations", fill="#0F172A", font=get_font(11, bold=True))
    
    draw.rounded_rectangle([(940, 183), (1050, 217)], radius=4, fill="#0284C7")
    draw.text((965, 192), "RUN QUERY", fill="#FFFFFF", font=get_font(11, bold=True))
    
    # Query Editor Box
    draw.rounded_rectangle([(36, 240), (W - 36, 420)], radius=8, fill="#0F172A")
    draw.text((54, 252), "SQL EDITOR - QUERY 4 DEFINITION", fill="#94A3B8", font=get_font(11, bold=True))
    
    cfont = get_code_font(11)
    sql_lines = [
        ("SELECT b.PNR, p.Name AS PassengerName, t.TrainNo, t.TrainName,", "#38BDF8"),
        ("       bs.StationName AS Boarding, es.StationName AS ExitStation,", "#38BDF8"),
        ("       sc.ClassType, b.Status, pay.Amount", "#38BDF8"),
        ("FROM BOOKING b", "#FCD34D"),
        ("JOIN PASSENGER p ON b.PassengerID = p.PassengerID", "#FCD34D"),
        ("JOIN TRAIN t ON b.TrainNo = t.TrainNo", "#FCD34D"),
        ("JOIN STATION bs ON b.BoardStationCode = bs.StationCode", "#FCD34D"),
        ("JOIN STATION es ON b.ExitStationCode = es.StationCode", "#FCD34D"),
        ("LEFT JOIN PAYMENT pay ON b.PNR = pay.PNR", "#FCD34D"),
        ("WHERE b.Status = 'Confirmed' ORDER BY b.PNR;", "#4ADE80")
    ]
    sy = 278
    for stext, scolor in sql_lines:
        draw.text((54, sy), stext, fill=scolor, font=cfont)
        sy += 14
        
    # Query Results Table
    draw.rounded_rectangle([(36, 435), (W - 36, 715)], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw.text((54, 450), "QUERY RESULT SET (12 ROWS RETURNED IN 0.003 SECONDS)", fill="#15803D", font=get_font(12, bold=True))
    
    # Table Header
    draw.rectangle([(54, 475), (W - 54, 505)], fill="#F1F5F9")
    t_headers = ["PNR", "PassengerName", "TrainNo", "TrainName", "Boarding", "ExitStation", "Class", "Status", "Amount (INR)"]
    t_x = [65, 140, 275, 360, 560, 720, 880, 960, 1060]
    for h, x in zip(t_headers, t_x):
        draw.text((x, 485), h, fill="#334155", font=get_font(11, bold=True))
        
    res_rows = [
        ("10001", "Rahul Sharma", "12658", "Bengaluru Express", "KSR Bengaluru", "Chennai Central", "3A", "Confirmed", "650.00"),
        ("10002", "Priya Nair", "12658", "Bengaluru Express", "KSR Bengaluru", "Katpadi Jn", "3A", "Confirmed", "440.00"),
        ("10003", "Amit Kumar", "12658", "Bengaluru Express", "Krishnarajapuram", "Chennai Central", "3A", "Confirmed", "620.00"),
        ("10004", "Sneha Patel", "12658", "Bengaluru Express", "KSR Bengaluru", "Chennai Central", "1A", "Confirmed", "1480.00"),
        ("10005", "Mohammed Ali", "12658", "Bengaluru Express", "Bangarapet Jn", "Chennai Central", "2A", "Confirmed", "780.00"),
        ("10006", "Kavita Reddy", "12658", "Bengaluru Express", "KSR Bengaluru", "Katpadi Jn", "SL", "Confirmed", "210.00"),
        ("10014", "Venkatesh Rao", "12658", "Bengaluru Express", "Krishnarajapuram", "Katpadi Jn", "3A", "Confirmed", "443.00")
    ]
    
    ry = 515
    for r in res_rows:
        draw.line([(54, ry), (W - 54, ry)], fill="#F1F5F9", width=1)
        for val, x in zip(r, t_x):
            if val == "Confirmed":
                draw.text((x, ry + 4), val, fill="#15803D", font=get_font(11, bold=True))
            else:
                draw.text((x, ry + 4), val, fill="#1E293B", font=get_font(11))
        ry += 27
        
    img.save(os.path.join(OUTPUT_DIR, "fig8_queries.png"))
    print("Saved fig8_queries.png")

if __name__ == "__main__":
    make_fig3()
    make_fig4()
    make_fig5()
    make_fig6()
    make_fig7()
    make_fig8()
    print("All 6 figures generated successfully!")
