/* ═══════════════════════════════════════════════════════════════
   Railway Reservation System — Frontend Logic
   DBMS Mini Project | Ganesh | UVCE Bangalore
   ═══════════════════════════════════════════════════════════════ */

const API = '';

/* ── Navigation ─────────────────────────────────────────────── */
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => navigateTo(item.dataset.page));
});

function navigateTo(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const el = document.getElementById('page-' + page);
    if (el) el.classList.add('active');
    const nav = document.querySelector('[data-page="' + page + '"]');
    if (nav) nav.classList.add('active');
    loadPage(page);
}

function loadPage(page) {
    const loaders = {
        dashboard: loadDashboard,
        trains: loadTrains,
        stations: loadStations,
        passengers: loadPassengers,
        search: loadSearchDropdowns,
        book: async () => { await loadBookingForm(); await loadBookingsInBookingPage(); },
        pnr: loadAllBookings,
        cancel: loadCancelPage,
        chart: loadChartPage,
        bill: loadBillPage,
        reports: loadReports,
        queries: loadQueriesPage
    };
    if (loaders[page]) loaders[page]();
}

/* ── Utility ────────────────────────────────────────────────── */
async function api(url, opts) {
    try {
        const res = await fetch(API + url, opts);
        return await res.json();
    } catch (e) {
        toast('Connection error', 'error');
        return null;
    }
}
async function apiPost(url, body) {
    return api(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
}

function toast(msg, type = 'info') {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.className = 'toast ' + type + ' show';
    setTimeout(() => t.classList.remove('show'), 3000);
}

function toggleForm(id) {
    document.getElementById(id).classList.toggle('hidden');
}

function statusBadge(s) {
    if (!s) return '';
    const cls = s.toLowerCase();
    return '<span class="status status-' + cls + '">' + s + '</span>';
}

function makeTable(data, cols) {
    if (!data || !data.length) return '<p style="color:var(--text-light);font-size:.82rem;padding:.5rem">No data found.</p>';
    let h = '<table><thead><tr>';
    cols.forEach(c => h += '<th>' + (c.label || c.key) + '</th>');
    h += '</tr></thead><tbody>';
    data.forEach(row => {
        h += '<tr>';
        cols.forEach(c => {
            let v = row[c.key];
            if (c.render) v = c.render(v, row);
            else if (v === null || v === undefined) v = '—';
            h += '<td>' + v + '</td>';
        });
        h += '</tr>';
    });
    return h + '</tbody></table>';
}

function formatDate(d) {
    if (!d) return '—';
    return new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}
function formatMoney(v) {
    if (v === null || v === undefined) return '—';
    return '₹' + Number(v).toLocaleString('en-IN', { minimumFractionDigits: 2 });
}

/* ── DASHBOARD ──────────────────────────────────────────────── */
async function loadDashboard() {
    const d = await api('/api/dashboard');
    if (!d) return;
    const s = d.stats;
    const icons = [
        { icon: 'fa-users', color: 'blue', label: 'Passengers', val: s.total_passengers },
        { icon: 'fa-train', color: 'green', label: 'Trains', val: s.total_trains },
        { icon: 'fa-ticket-alt', color: 'orange', label: 'Total Bookings', val: s.total_bookings },
        { icon: 'fa-check-circle', color: 'green', label: 'Confirmed', val: s.confirmed },
        { icon: 'fa-clock', color: 'purple', label: 'Waitlisted', val: s.waitlisted },
        { icon: 'fa-times-circle', color: 'red', label: 'Cancelled', val: s.cancelled },
        { icon: 'fa-rupee-sign', color: 'cyan', label: 'Revenue', val: formatMoney(s.total_revenue) },
        { icon: 'fa-map-marker-alt', color: 'blue', label: 'Stations', val: s.total_stations },
    ];
    document.getElementById('statsGrid').innerHTML = icons.map(i =>
        '<div class="stat-card"><div class="stat-icon ' + i.color + '"><i class="fas ' + i.icon + '"></i></div>' +
        '<div class="stat-info"><h4>' + i.val + '</h4><p>' + i.label + '</p></div></div>'
    ).join('');

    document.getElementById('recentBookings').innerHTML = makeTable(d.recent, [
        { key: 'PNR', label: 'PNR' },
        { key: 'Name', label: 'Passenger' },
        { key: 'TrainName', label: 'Train' },
        { key: 'BoardingStation', label: 'From' },
        { key: 'ExitStation', label: 'To' },
        { key: 'Status', label: 'Status', render: statusBadge },
        { key: 'JourneyDate', label: 'Date', render: formatDate },
    ]);

    let occHtml = '';
    d.occupancy.forEach(o => {
        const total = (o.Occupied || 0) + (o.Available || 0);
        const occPct = total ? ((o.Occupied / total) * 100) : 0;
        const avPct = 100 - occPct;
        occHtml += '<div class="occ-row"><span class="occ-label">' + o.TrainName + ' (' + o.ClassType + ')</span>' +
            '<div class="occ-bar"><div class="occ-filled" style="width:' + occPct + '%"></div>' +
            '<div class="occ-avail" style="width:' + avPct + '%"></div></div>' +
            '<span class="occ-nums">' + (o.Occupied || 0) + '/' + total + '</span></div>';
    });
    document.getElementById('occupancyData').innerHTML = occHtml || '<p style="color:var(--text-light)">No data</p>';
}

/* ── TRAINS ─────────────────────────────────────────────────── */
async function loadTrains() {
    const data = await api('/api/trains');
    if (!data) return;
    document.getElementById('trainsTable').innerHTML = makeTable(data, [
        { key: 'TrainNo', label: 'No' },
        { key: 'TrainName', label: 'Train Name' },
        { key: 'Source', label: 'Source' },
        { key: 'Destination', label: 'Dest' },
        { key: '_actions', label: 'Actions', render: (_, r) =>
            '<button class="btn btn-outline btn-sm" onclick="viewRoute(' + r.TrainNo + ',\'' + r.TrainName.replace(/'/g,"\\'") + '\')"><i class="fas fa-route"></i> Route</button> ' +
            '<button class="btn btn-danger btn-sm" onclick="deleteTrain(' + r.TrainNo + ')"><i class="fas fa-trash"></i></button>'
        },
    ]);
}
async function addTrain() {
    const d = { TrainNo: +document.getElementById('trainNo').value, TrainName: document.getElementById('trainName').value,
        Source: document.getElementById('trainSrc').value.toUpperCase(), Destination: document.getElementById('trainDst').value.toUpperCase() };
    const r = await apiPost('/api/trains', d);
    if (r && r.success) { toast(r.message, 'success'); loadTrains(); toggleForm('addTrainForm'); }
    else toast(r ? r.message : 'Error', 'error');
}
async function deleteTrain(no) {
    if (!confirm('Delete train ' + no + '? This cascades to routes, classes, seats, bookings.')) return;
    const r = await api('/api/trains/' + no, { method: 'DELETE' });
    if (r && r.success) { toast('Train deleted', 'success'); loadTrains(); }
    else toast(r ? r.message : 'Error', 'error');
}
async function viewRoute(tno, name) {
    document.getElementById('routeCard').style.display = 'block';
    document.getElementById('routeTitle').textContent = 'Route: ' + name + ' (' + tno + ')';
    const route = await api('/api/routes/' + tno);
    if (!route) return;
    // Timeline
    let tl = '';
    route.forEach((s, i) => {
        tl += '<div class="timeline-stop"><div class="timeline-dot"></div>' +
            '<div class="timeline-label">' + s.StationCode + '<div class="timeline-sub">' + s.StationName + '</div>' +
            '<div class="timeline-sub">' + s.DistanceFromOrigin + ' km</div></div></div>';
        if (i < route.length - 1) tl += '<div class="timeline-line"></div>';
    });
    document.getElementById('routeTimeline').innerHTML = tl;
    document.getElementById('routeTable').innerHTML = makeTable(route, [
        { key: 'SeqNo', label: '#' }, { key: 'StationCode', label: 'Code' },
        { key: 'StationName', label: 'Station' }, { key: 'City', label: 'City' },
        { key: 'DistanceFromOrigin', label: 'Distance (km)' },
    ]);
    const cls = await api('/api/seat-classes/' + tno);
    document.getElementById('seatClassesTable').innerHTML = makeTable(cls, [
        { key: 'ClassType', label: 'Class' }, { key: 'FarePerKm', label: '₹/km', render: v => '₹' + v },
        { key: 'TotalSeats', label: 'Total' }, { key: 'Available', label: 'Available', render: v => '<span style="color:var(--ir-green);font-weight:700">' + (v||0) + '</span>' },
        { key: 'Occupied', label: 'Occupied', render: v => '<span style="color:var(--ir-red);font-weight:700">' + (v||0) + '</span>' },
    ]);
}

/* ── STATIONS ───────────────────────────────────────────────── */
async function loadStations() {
    const data = await api('/api/stations');
    if (!data) return;
    document.getElementById('stationsTable').innerHTML = makeTable(data, [
        { key: 'StationCode', label: 'Code' }, { key: 'StationName', label: 'Name' }, { key: 'City', label: 'City' },
        { key: '_', label: '', render: (_, r) => '<button class="btn btn-danger btn-sm" onclick="deleteStation(\'' + r.StationCode + '\')"><i class="fas fa-trash"></i></button>' },
    ]);
}
async function addStation() {
    const d = { StationCode: document.getElementById('stCode').value.toUpperCase(), StationName: document.getElementById('stName').value, City: document.getElementById('stCity').value };
    const r = await apiPost('/api/stations', d);
    if (r && r.success) { toast(r.message, 'success'); loadStations(); toggleForm('addStationForm'); }
    else toast(r ? r.message : 'Error', 'error');
}
async function deleteStation(code) {
    if (!confirm('Delete station ' + code + '?')) return;
    const r = await api('/api/stations/' + code, { method: 'DELETE' });
    if (r && r.success) { toast('Station deleted', 'success'); loadStations(); }
    else toast(r ? r.message : 'Error', 'error');
}

/* ── PASSENGERS ─────────────────────────────────────────────── */
async function loadPassengers() {
    const data = await api('/api/passengers');
    if (!data) return;
    document.getElementById('passengersTable').innerHTML = makeTable(data, [
        { key: 'PassengerID', label: 'ID' }, { key: 'Name', label: 'Name' },
        { key: 'Age', label: 'Age' },
        { key: 'Gender', label: 'Gender', render: v => v === 'M' ? 'Male' : v === 'F' ? 'Female' : 'Other' },
        { key: 'Contact', label: 'Phone' },
        { key: '_', label: '', render: (_, r) => '<button class="btn btn-danger btn-sm" onclick="deletePassenger(' + r.PassengerID + ')"><i class="fas fa-trash"></i></button>' },
    ]);
}
async function addPassenger() {
    const d = { Name: document.getElementById('pName').value, Age: +document.getElementById('pAge').value,
        Gender: document.getElementById('pGender').value, Contact: document.getElementById('pContact').value };
    const r = await apiPost('/api/passengers', d);
    if (r && r.success) { toast('Passenger added (ID: ' + r.id + ')', 'success'); loadPassengers(); toggleForm('addPassengerForm'); }
    else toast(r ? r.message : 'Error', 'error');
}
async function deletePassenger(id) {
    if (!confirm('Delete passenger ' + id + '?')) return;
    const r = await api('/api/passengers/' + id, { method: 'DELETE' });
    if (r && r.success) { toast('Deleted', 'success'); loadPassengers(); }
    else toast(r ? r.message : 'Error', 'error');
}

/* ── SEARCH TRAINS ──────────────────────────────────────────── */
async function loadSearchDropdowns() {
    const stations = await api('/api/stations');
    if (!stations) return;
    const opts = stations.map(s => '<option value="' + s.StationCode + '">' + s.StationName + ' (' + s.StationCode + ')</option>').join('');
    document.getElementById('searchFrom').innerHTML = '<option value="">Select Station</option>' + opts;
    document.getElementById('searchTo').innerHTML = '<option value="">Select Station</option>' + opts;
}
function swapStations() {
    const f = document.getElementById('searchFrom'), t = document.getElementById('searchTo');
    const tmp = f.value; f.value = t.value; t.value = tmp;
}
async function searchTrains() {
    const from = document.getElementById('searchFrom').value;
    const to = document.getElementById('searchTo').value;
    if (!from || !to) { toast('Select both stations', 'error'); return; }
    if (from === to) { toast('Stations must be different', 'error'); return; }
    const data = await api('/api/search?from=' + from + '&to=' + to);
    if (!data || !data.length) {
        document.getElementById('searchResults').innerHTML = '<div class="result-card warning"><i class="fas fa-exclamation-triangle"></i><div class="result-text"><h4>No Trains Found</h4><p>No direct trains between these stations.</p></div></div>';
        return;
    }
    let html = '';
    data.forEach(t => {
        html += '<div class="card" style="margin-top:1rem">' +
            '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5rem">' +
            '<div><h3 style="margin:0">' + t.TrainName + ' <span style="color:var(--text-light);font-weight:400">#' + t.TrainNo + '</span></h3>' +
            '<p style="font-size:.78rem;color:var(--text-light);margin-top:4px">' + t.BoardName + ' → ' + t.ExitName + ' &bull; ' + t.Distance + ' km</p></div>' +
            '<button class="btn btn-primary" onclick="navigateTo(\'book\')"><i class="fas fa-ticket-alt"></i> Book</button></div></div>';
    });
    document.getElementById('searchResults').innerHTML = html;
}

/* ── BOOK TICKET ────────────────────────────────────────────── */
async function loadBookingForm() {
    const [passengers, trains] = await Promise.all([api('/api/passengers'), api('/api/trains')]);
    if (!passengers || !trains) return;
    document.getElementById('bookPassenger').innerHTML = passengers.map(p => '<option value="' + p.PassengerID + '">' + p.Name + ' (ID: ' + p.PassengerID + ')</option>').join('');
    document.getElementById('bookTrain').innerHTML = trains.map(t => '<option value="' + t.TrainNo + '">' + t.TrainName + ' #' + t.TrainNo + '</option>').join('');
    document.getElementById('bookDate').value = new Date().toISOString().split('T')[0];
    onBookTrainChange();
}
async function onBookTrainChange() {
    const tno = document.getElementById('bookTrain').value;
    if (!tno) return;
    const [route, classes] = await Promise.all([api('/api/routes/' + tno), api('/api/seat-classes/' + tno)]);
    if (route) {
        const opts = route.map(s => '<option value="' + s.StationCode + '">' + s.StationName + ' (' + s.StationCode + ')</option>').join('');
        document.getElementById('bookFrom').innerHTML = opts;
        document.getElementById('bookTo').innerHTML = opts;
        if (route.length > 1) document.getElementById('bookTo').selectedIndex = route.length - 1;
    }
    if (classes) {
        document.getElementById('bookClass').innerHTML = classes.map(c =>
            '<option value="' + c.ClassID + '">' + c.ClassType + ' (₹' + c.FarePerKm + '/km) — ' + (c.Available || 0) + ' seats available</option>'
        ).join('');
    }
}
async function bookTicket() {
    const d = {
        PassengerID: +document.getElementById('bookPassenger').value,
        TrainNo: +document.getElementById('bookTrain').value,
        ClassID: +document.getElementById('bookClass').value,
        BoardingStation: document.getElementById('bookFrom').value,
        ExitStation: document.getElementById('bookTo').value,
        JourneyDate: document.getElementById('bookDate').value,
    };
    if (d.BoardingStation === d.ExitStation) { toast('Boarding and exit stations cannot be same', 'error'); return; }
    const r = await apiPost('/api/bookings', d);
    if (r && r.success) {
        const cls = r.status === 'Confirmed' ? 'success' : 'warning';
        const icon = r.status === 'Confirmed' ? 'fa-check-circle' : 'fa-clock';
        document.getElementById('bookingResult').innerHTML =
            '<div class="result-card ' + cls + '"><i class="fas ' + icon + '"></i>' +
            '<div class="result-text"><h4>' + r.status + '! PNR: ' + r.pnr + '</h4>' +
            '<p>' + (r.seatId ? 'Seat ID: ' + r.seatId : 'You are on the waitlist. Seat will be assigned upon availability.') + '</p></div></div>';
        toast(r.message, cls === 'success' ? 'success' : 'info');

        // Immediately update bookings table and booking chart!
        await loadBookingsInBookingPage();
        if (typeof loadTrainChart === 'function') await loadTrainChart();
        if (typeof loadChartPage === 'function') await loadChartPage();
        if (typeof loadDashboard === 'function') await loadDashboard();
    } else {
        document.getElementById('bookingResult').innerHTML = '<div class="result-card error"><i class="fas fa-times-circle"></i><div class="result-text"><h4>Booking Failed</h4><p>' + (r ? r.message : 'Error') + '</p></div></div>';
        toast('Booking failed', 'error');
    }
}

/* ── All Current Bookings Table (on Book Ticket page) ────────── */
let _allBookingsCache = [];

async function loadBookingsInBookingPage() {
    const data = await api('/api/bookings');
    if (!data) return;
    _allBookingsCache = data;
    renderSplitBookingTables(data);
}

function renderSplitBookingTables(list) {
    const confirmed  = (list || []).filter(b => b.Status === 'Confirmed');
    const waitlisted = (list || []).filter(b => b.Status === 'Waitlisted');
    const cancelled  = (list || []).filter(b => b.Status === 'Cancelled');

    const cnfBadge = document.getElementById('bookingCountBadge');
    const wlBadge  = document.getElementById('wlBadge');
    const canBadge = document.getElementById('canBadge');
    if (cnfBadge) cnfBadge.innerText = confirmed.length;
    if (wlBadge)  wlBadge.innerText  = waitlisted.length;
    if (canBadge) canBadge.innerText  = cancelled.length;

    const cnfCount = document.getElementById('cnfCountBadge');
    const wlCount  = document.getElementById('wlCountBadge');
    const canCount = document.getElementById('canCountBadge');
    if (cnfCount) cnfCount.innerHTML = '<i class="fas fa-check-circle"></i> Confirmed: ' + confirmed.length;
    if (wlCount)  wlCount.innerHTML  = '<i class="fas fa-clock"></i> Waitlisted: ' + waitlisted.length;
    if (canCount) canCount.innerHTML = '<i class="fas fa-times-circle"></i> Cancelled: ' + cancelled.length;

    renderBookingSection('confirmedBookingsTable',  confirmed,  'confirmed');
    renderBookingSection('waitlistedBookingsTable', waitlisted, 'waitlisted');
    renderBookingSection('cancelledBookingsTable',  cancelled,  'cancelled');
}

function renderBookingSection(containerId, list, type) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!list || !list.length) {
        const emptyMsgs = {
            confirmed:  '<i class="fas fa-check-circle" style="color:#2e7d32"></i> No confirmed bookings.',
            waitlisted: '<i class="fas fa-clock" style="color:#e65100"></i> No passengers on waitlist.',
            cancelled:  '<i class="fas fa-times-circle" style="color:#c62828"></i> No cancelled bookings.'
        };
        container.innerHTML = '<div style="text-align:center;padding:1.2rem;color:var(--text-light);font-size:.88rem">' + (emptyMsgs[type] || 'No data.') + '</div>';
        return;
    }

    let html = '<table class="table"><thead><tr>' +
        '<th>PNR</th><th>Passenger</th><th>Train</th><th>Class</th><th>Seat / Position</th><th>Route</th><th>Journey Date</th><th>Actions</th>' +
        '</tr></thead><tbody>';

    list.forEach(function(b, idx) {
        const gIcon = b.Gender === 'M' ? 'fa-male' : b.Gender === 'F' ? 'fa-female' : 'fa-user';
        let seatStr;
        if (type === 'confirmed') {
            seatStr = b.SeatNo
                ? '<strong>Coach ' + b.CoachNo + '</strong>, Seat ' + b.SeatNo
                : '<span style="color:#888">—</span>';
        } else if (type === 'waitlisted') {
            seatStr = '<span style="background:#fff3e0;color:#e65100;padding:3px 8px;border-radius:10px;font-weight:700;font-size:.82rem">WL-' + (idx + 1) + ' (Queue)</span>';
        } else {
            seatStr = '<span style="color:#aaa;font-style:italic">Seat Released</span>';
        }

        const rowBg = type === 'confirmed'  ? 'rgba(46,125,50,.04)' :
                      type === 'waitlisted' ? 'rgba(230,81,0,.04)'  :
                                             'rgba(198,40,40,.04)';

        html += '<tr style="background:' + rowBg + '">' +
            '<td><strong>' + b.PNR + '</strong></td>' +
            '<td><i class="fas ' + gIcon + '" style="margin-right:4px;color:var(--ir-blue)"></i><strong>' + b.Name + '</strong> <small style="color:var(--text-light)">(' + (b.Age || '—') + ')</small></td>' +
            '<td>' + b.TrainName + ' <small style="color:var(--text-light)">#' + b.TrainNo + '</small></td>' +
            '<td><span class="badge" style="background:rgba(0,53,128,.1);color:var(--ir-blue)">' + b.ClassType + '</span></td>' +
            '<td>' + seatStr + '</td>' +
            '<td>' + b.BoardingStation + ' → ' + b.ExitStation + '</td>' +
            '<td>' + (b.JourneyDate || '—') + '</td>' +
            '<td style="white-space:nowrap">' +
                '<button class="btn btn-sm btn-outline" style="margin-right:4px" onclick="openEditBookingModal(' + b.PNR + ')"><i class="fas fa-edit"></i> Edit</button>' +
                (b.Status !== 'Cancelled' ? '<button class="btn btn-sm btn-danger" style="margin-right:4px" onclick="cancelBookingDirect(' + b.PNR + ')"><i class="fas fa-times"></i> Cancel</button>' : '') +
                '<button class="btn btn-sm btn-outline" style="color:var(--ir-red);border-color:var(--border)" onclick="deleteBookingDirect(' + b.PNR + ')" title="Delete"><i class="fas fa-trash"></i></button>' +
            '</td>' +
        '</tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

function renderBookingsListTable(list) {
    renderSplitBookingTables(list);
}

function filterBookingsTable() {
    const q = (document.getElementById('bookingSearchInput')?.value || '').toLowerCase().trim();
    if (!q) {
        renderSplitBookingTables(_allBookingsCache);
        return;
    }
    const filtered = _allBookingsCache.filter(b =>
        String(b.PNR).includes(q) ||
        (b.Name && b.Name.toLowerCase().includes(q)) ||
        (b.TrainName && b.TrainName.toLowerCase().includes(q)) ||
        (b.Status && b.Status.toLowerCase().includes(q)) ||
        (b.BoardingStation && b.BoardingStation.toLowerCase().includes(q)) ||
        (b.ExitStation && b.ExitStation.toLowerCase().includes(q))
    );
    renderSplitBookingTables(filtered);
}

/* ── Edit Booking Modal Handlers ────────────────────────────── */
async function openEditBookingModal(pnr) {
    const [booking, passengers] = await Promise.all([
        api('/api/bookings/' + pnr),
        api('/api/passengers')
    ]);
    if (!booking || booking.error) {
        toast('Could not load booking details', 'error');
        return;
    }

    document.getElementById('editPNR').value = booking.PNR;
    document.getElementById('editTrainNo').value = booking.TrainNo;
    document.getElementById('editBookingPNRBadge').innerText = 'PNR #' + booking.PNR;

    // Populate passengers
    const passSelect = document.getElementById('editPassenger');
    passSelect.innerHTML = passengers.map(p => 
        '<option value="' + p.PassengerID + '" ' + (p.PassengerID === booking.PassengerID ? 'selected' : '') + '>' +
        p.Name + ' (ID: ' + p.PassengerID + ')</option>'
    ).join('');

    // Journey date
    document.getElementById('editJourneyDate').value = booking.JourneyDate ? booking.JourneyDate.split('T')[0] : '';

    // Route stations for this train
    const route = await api('/api/routes/' + booking.TrainNo);
    if (route) {
        const boardOpts = route.map(s => '<option value="' + s.StationCode + '" ' + (s.StationCode === booking.BoardingStation ? 'selected' : '') + '>' + s.StationName + ' (' + s.StationCode + ')</option>').join('');
        const exitOpts = route.map(s => '<option value="' + s.StationCode + '" ' + (s.StationCode === booking.ExitStation ? 'selected' : '') + '>' + s.StationName + ' (' + s.StationCode + ')</option>').join('');
        document.getElementById('editBoarding').innerHTML = boardOpts;
        document.getElementById('editExit').innerHTML = exitOpts;
    }

    // Status
    document.getElementById('editStatus').value = booking.Status;

    // Show modal
    document.getElementById('editBookingModal').style.display = 'flex';
}

function closeEditBookingModal() {
    document.getElementById('editBookingModal').style.display = 'none';
}

async function submitEditBooking() {
    const pnr = document.getElementById('editPNR').value;
    const payload = {
        PassengerID: +document.getElementById('editPassenger').value,
        JourneyDate: document.getElementById('editJourneyDate').value,
        BoardingStation: document.getElementById('editBoarding').value,
        ExitStation: document.getElementById('editExit').value,
        Status: document.getElementById('editStatus').value
    };

    if (payload.BoardingStation === payload.ExitStation) {
        toast('Boarding and Exit station cannot be the same', 'error');
        return;
    }

    const res = await api('/api/bookings/' + pnr, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res && res.success) {
        toast(res.message, 'success');
        closeEditBookingModal();
        await loadBookingsInBookingPage();
        if (typeof loadTrainChart === 'function') await loadTrainChart();
        if (typeof loadChartPage === 'function') await loadChartPage();
        if (typeof loadDashboard === 'function') await loadDashboard();
    } else {
        toast((res && res.message) || 'Update failed', 'error');
    }
}

async function cancelBookingDirect(pnr) {
    if (!confirm('Are you sure you want to cancel PNR ' + pnr + '? This will run CancelBooking procedure!')) return;
    const res = await apiPost('/api/cancel/' + pnr);
    if (res && res.success) {
        toast(res.message, 'success');
        await loadBookingsInBookingPage();
        if (typeof loadTrainChart === 'function') await loadTrainChart();
        if (typeof loadChartPage === 'function') await loadChartPage();
        if (typeof loadDashboard === 'function') await loadDashboard();
    } else {
        toast((res && res.message) || 'Cancellation failed', 'error');
    }
}

async function deleteBookingDirect(pnr) {
    if (!confirm('Permanently delete PNR ' + pnr + ' from database?')) return;
    const res = await api('/api/bookings/' + pnr, { method: 'DELETE' });
    if (res && res.success) {
        toast(res.message, 'success');
        await loadBookingsInBookingPage();
        if (typeof loadTrainChart === 'function') await loadTrainChart();
        if (typeof loadChartPage === 'function') await loadChartPage();
        if (typeof loadDashboard === 'function') await loadDashboard();
    } else {
        toast((res && res.message) || 'Delete failed', 'error');
    }
}

/* ── PNR STATUS ─────────────────────────────────────────────── */
async function lookupPNR() {
    const pnr = document.getElementById('pnrInput').value;
    if (!pnr) { toast('Enter a PNR number', 'error'); return; }
    const d = await api('/api/bookings/' + pnr);
    if (!d || d.error) {
        document.getElementById('pnrResult').innerHTML = '<div class="result-card error"><i class="fas fa-times-circle"></i><div class="result-text"><h4>PNR Not Found</h4><p>No booking with PNR ' + pnr + '</p></div></div>';
        return;
    }
    let payHtml = '';
    if (d.payment) {
        payHtml = '<div class="pnr-field"><label>Amount Paid</label><span>' + formatMoney(d.payment.Amount) + '</span></div>' +
            '<div class="pnr-field"><label>Payment Mode</label><span>' + d.payment.Mode + '</span></div>';
    }
    document.getElementById('pnrResult').innerHTML =
        '<div class="pnr-card"><div class="pnr-header"><h3>PNR: ' + d.PNR + '</h3>' + statusBadge(d.Status) + '</div>' +
        '<div class="pnr-body">' +
        '<div class="pnr-field"><label>Passenger</label><span>' + d.Name + '</span></div>' +
        '<div class="pnr-field"><label>Age / Gender</label><span>' + d.Age + ' / ' + (d.Gender === 'M' ? 'Male' : d.Gender === 'F' ? 'Female' : 'Other') + '</span></div>' +
        '<div class="pnr-field"><label>Train</label><span>' + d.TrainName + ' #' + d.TrainNo + '</span></div>' +
        '<div class="pnr-field"><label>Class</label><span>' + d.ClassType + ' (₹' + d.FarePerKm + '/km)</span></div>' +
        '<div class="pnr-field"><label>Seat ID</label><span>' + (d.SeatID || 'Not assigned') + '</span></div>' +
        '<div class="pnr-field"><label>Journey Date</label><span>' + formatDate(d.JourneyDate) + '</span></div>' +
        '<div class="pnr-field"><label>Distance</label><span>' + d.Distance + ' km</span></div>' +
        '<div class="pnr-field"><label>Estimated Fare</label><span>' + formatMoney(d.Distance * d.FarePerKm) + '</span></div>' +
        payHtml +
        '<div class="pnr-journey">' +
        '<div class="pnr-station"><div class="code">' + d.BoardingStation + '</div><div class="name">' + d.BoardName + '</div></div>' +
        '<div class="pnr-arrow"><i class="fas fa-long-arrow-alt-right"></i></div>' +
        '<div class="pnr-station"><div class="code">' + d.ExitStation + '</div><div class="name">' + d.ExitName + '</div></div>' +
        '</div></div></div>';
}

async function loadAllBookings() {
    const data = await api('/api/bookings');
    if (!data) return;
    document.getElementById('allBookingsTable').innerHTML = makeTable(data, [
        { key: 'PNR', label: 'PNR' }, { key: 'Name', label: 'Passenger' },
        { key: 'TrainName', label: 'Train' }, { key: 'ClassType', label: 'Class' },
        { key: 'BoardingStation', label: 'From' }, { key: 'ExitStation', label: 'To' },
        { key: 'SeatID', label: 'Seat' }, { key: 'JourneyDate', label: 'Date', render: formatDate },
        { key: 'Status', label: 'Status', render: statusBadge },
    ]);
}

/* ── CANCEL TICKET ──────────────────────────────────────────── */
async function loadCancelPage() {
    const data = await api('/api/bookings');
    if (!data) return;
    const active = data.filter(b => b.Status === 'Confirmed' || b.Status === 'Waitlisted');
    document.getElementById('cancelBookingsTable').innerHTML = makeTable(active, [
        { key: 'PNR', label: 'PNR' }, { key: 'Name', label: 'Passenger' },
        { key: 'TrainName', label: 'Train' }, { key: 'BoardingStation', label: 'From' },
        { key: 'ExitStation', label: 'To' }, { key: 'SeatID', label: 'Seat' },
        { key: 'Status', label: 'Status', render: statusBadge },
    ]);
}
async function cancelTicket() {
    const pnr = document.getElementById('cancelPNR').value;
    if (!pnr) { toast('Enter PNR', 'error'); return; }
    if (!confirm('Cancel booking PNR ' + pnr + '?')) return;
    const r = await apiPost('/api/cancel/' + pnr, {});
    if (r && r.success) {
        let html = '<div class="result-card success"><i class="fas fa-check-circle"></i><div class="result-text"><h4>' + r.message + '</h4>' +
            '<p>Trigger <strong>trg_free_seat_after_cancel</strong> fired to free the seat.</p></div></div>';
        if (r.promoted && r.promoted.length) {
            r.promoted.forEach(p => {
                html += '<div class="result-card info"><i class="fas fa-arrow-up"></i><div class="result-text">' +
                    '<h4>Waitlist Auto-Promoted!</h4>' +
                    '<p>' + p.name + ' (PNR: ' + p.pnr + ') moved to CONFIRMED with Seat ' + p.seatId +
                    ' via <strong>CancelBooking</strong> stored procedure.</p></div></div>';
            });
        }
        document.getElementById('cancelResult').innerHTML = html;
        toast('Booking cancelled', 'success');
        loadCancelPage();
    } else {
        document.getElementById('cancelResult').innerHTML = '<div class="result-card error"><i class="fas fa-times-circle"></i><div class="result-text"><h4>Cancellation Failed</h4><p>' + (r ? r.message : 'Error') + '</p></div></div>';
        toast('Failed', 'error');
    }
}

/* ── GENERATE BILL ──────────────────────────────────────────── */
async function loadBillPage() {
    const data = await api('/api/bookings');
    if (!data) return;
    const unpaid = data.filter(b => b.Status === 'Confirmed');
    document.getElementById('billBookingsTable').innerHTML = makeTable(unpaid, [
        { key: 'PNR', label: 'PNR' }, { key: 'Name', label: 'Passenger' },
        { key: 'TrainName', label: 'Train' }, { key: 'ClassType', label: 'Class' },
        { key: 'BoardingStation', label: 'From' }, { key: 'ExitStation', label: 'To' },
    ]);
}
async function generateBill() {
    const pnr = document.getElementById('billPNR').value;
    const mode = document.getElementById('billMode').value;
    if (!pnr) { toast('Enter PNR', 'error'); return; }
    const r = await apiPost('/api/bill/' + pnr, { mode });
    if (r && r.success) {
        document.getElementById('billResult').innerHTML =
            '<div class="result-card success"><i class="fas fa-receipt"></i><div class="result-text">' +
            '<h4>Bill Generated — ' + formatMoney(r.fare) + '</h4>' +
            '<p>Payment via ' + mode + ' recorded. Computed by <strong>GenerateBill</strong> stored procedure ' +
            '(fare = distance × FarePerKm).</p></div></div>';
        toast('Bill generated: ' + formatMoney(r.fare), 'success');
        loadBillPage();
    } else {
        document.getElementById('billResult').innerHTML = '<div class="result-card error"><i class="fas fa-times-circle"></i><div class="result-text"><h4>Bill Failed</h4><p>' + (r ? r.message : 'Error') + '</p></div></div>';
        toast('Failed', 'error');
    }
}

/* ── REPORTS ─────────────────────────────────────────────────── */
async function loadReports() {
    const d = await api('/api/reports');
    if (!d) return;

    document.getElementById('revenueByTrain').innerHTML = makeTable(d.revenue_by_train, [
        { key: 'TrainNo', label: 'No' }, { key: 'TrainName', label: 'Train' },
        { key: 'TotalBookings', label: 'Bookings' },
        { key: 'TotalRevenue', label: 'Revenue', render: formatMoney },
    ]);

    // Status bar chart
    const total = d.by_status.reduce((s, r) => s + r.Count, 0) || 1;
    const colors = { Confirmed: 'green', Waitlisted: 'orange', Cancelled: 'red' };
    let barsHtml = '<div class="status-bars">';
    d.by_status.forEach(r => {
        const pct = Math.max(5, (r.Count / total) * 100);
        barsHtml += '<div class="bar-row"><span class="bar-label">' + r.Status + '</span>' +
            '<div class="bar-track"><div class="bar-fill ' + (colors[r.Status] || 'green') + '" style="width:' + pct + '%">' + r.Count + '</div></div></div>';
    });
    barsHtml += '</div>';
    document.getElementById('bookingsByStatus').innerHTML = barsHtml;

    document.getElementById('revenueByMode').innerHTML = makeTable(d.by_mode, [
        { key: 'Mode', label: 'Mode' }, { key: 'Count', label: 'Transactions' },
        { key: 'Total', label: 'Total', render: formatMoney },
    ]);

    document.getElementById('popularRoutes').innerHTML = makeTable(d.popular_routes, [
        { key: 'FromStation', label: 'From' }, { key: 'ToStation', label: 'To' },
        { key: 'BookingCount', label: 'Bookings' },
    ]);
}


/* ═══════════════════════════════════════════════════════════════
   BOOKING CHART — Indian Railway Style
   ═══════════════════════════════════════════════════════════════ */

const CHART_COLORS = {
    Confirmed:  { bg: '#2e7d32', light: 'rgba(46,125,50,.1)'  },
    Waitlisted: { bg: '#f57c00', light: 'rgba(245,124,0,.1)'  },
    Cancelled:  { bg: '#D32F2F', light: 'rgba(211,47,47,.1)'  },
};

async function loadChartPage() {
    const d = await api('/api/chart');
    if (!d) return;

    // ── Donut Chart ──
    const counts = {};
    (d.status_counts || []).forEach(r => counts[r.Status] = r.Count);
    const confirmed  = counts.Confirmed  || 0;
    const waitlisted = counts.Waitlisted || 0;
    const cancelled  = counts.Cancelled  || 0;
    const totalBookings = confirmed + waitlisted + cancelled;

    drawDonutChart('donutChart', [
        { label: 'Confirmed',  value: confirmed,  color: CHART_COLORS.Confirmed.bg },
        { label: 'Waitlisted', value: waitlisted, color: CHART_COLORS.Waitlisted.bg },
        { label: 'Cancelled',  value: cancelled,  color: CHART_COLORS.Cancelled.bg },
    ]);

    document.getElementById('donutCenter').innerHTML = totalBookings + '<br><small>Total Bookings</small>';

    // Legend
    document.getElementById('donutLegend').innerHTML =
        '<div class="legend-item"><div class="legend-dot" style="background:#2e7d32"></div>Confirmed<span class="legend-count">' + confirmed + '</span></div>' +
        '<div class="legend-item"><div class="legend-dot" style="background:#f57c00"></div>Waitlisted<span class="legend-count">' + waitlisted + '</span></div>' +
        '<div class="legend-item"><div class="legend-dot" style="background:#D32F2F"></div>Cancelled<span class="legend-count">' + cancelled + '</span></div>';

    // ── Train Summary Cards ──
    let cardsHtml = '';
    (d.train_summary || []).forEach(t => {
        const tot = (t.Confirmed || 0) + (t.Waitlisted || 0) + (t.Cancelled || 0);
        const cPct = tot ? ((t.Confirmed || 0) / tot * 100) : 0;
        const wPct = tot ? ((t.Waitlisted || 0) / tot * 100) : 0;
        const xPct = tot ? ((t.Cancelled || 0) / tot * 100) : 0;
        cardsHtml += '<div class="chart-train-card" onclick="document.getElementById(\'chartTrainSelect\').value=' + t.TrainNo + ';loadTrainChart()">' +
            '<h4>' + t.TrainName + ' <span style="font-weight:400;color:var(--text-light)">#' + t.TrainNo + '</span></h4>' +
            '<div class="train-route"><i class="fas fa-map-marker-alt"></i> ' + t.Source + ' → ' + t.Destination + '</div>' +
            '<div class="chart-train-bars">' +
                '<div class="bar-seg" style="width:' + cPct + '%;background:#2e7d32"></div>' +
                '<div class="bar-seg" style="width:' + wPct + '%;background:#f57c00"></div>' +
                '<div class="bar-seg" style="width:' + xPct + '%;background:#D32F2F"></div>' +
            '</div>' +
            '<div class="chart-train-nums">' +
                '<span><span class="dot" style="background:#2e7d32"></span>' + (t.Confirmed || 0) + ' CNF</span>' +
                '<span><span class="dot" style="background:#f57c00"></span>' + (t.Waitlisted || 0) + ' WL</span>' +
                '<span><span class="dot" style="background:#D32F2F"></span>' + (t.Cancelled || 0) + ' CAN</span>' +
            '</div></div>';
    });
    document.getElementById('chartSummaryCards').innerHTML = cardsHtml;

    // ── Train selector dropdown ──
    const select = document.getElementById('chartTrainSelect');
    if (d.trains && d.trains.length) {
        select.innerHTML = d.trains.map(t =>
            '<option value="' + t.TrainNo + '">' + t.TrainName + ' #' + t.TrainNo + '</option>'
        ).join('');
        loadTrainChart();
    }
}


/* ── Canvas Donut Chart ─────────────────────────────────────── */
function drawDonutChart(canvasId, segments) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width, H = canvas.height;
    const cx = W / 2, cy = H / 2;
    const outerR = Math.min(W, H) / 2 - 8;
    const innerR = outerR * 0.62;

    ctx.clearRect(0, 0, W, H);

    const total = segments.reduce((s, seg) => s + seg.value, 0);
    if (total === 0) {
        // draw empty ring
        ctx.beginPath();
        ctx.arc(cx, cy, outerR, 0, Math.PI * 2);
        ctx.arc(cx, cy, innerR, 0, Math.PI * 2, true);
        ctx.fillStyle = '#e0e0e0';
        ctx.fill();
        return;
    }

    let startAngle = -Math.PI / 2;
    segments.forEach((seg, i) => {
        if (seg.value <= 0) return;
        const sliceAngle = (seg.value / total) * Math.PI * 2;
        const endAngle = startAngle + sliceAngle;

        // Animated draw — slight gap between segments
        const gap = segments.filter(s => s.value > 0).length > 1 ? 0.02 : 0;

        ctx.beginPath();
        ctx.arc(cx, cy, outerR, startAngle + gap, endAngle - gap);
        ctx.arc(cx, cy, innerR, endAngle - gap, startAngle + gap, true);
        ctx.closePath();

        ctx.fillStyle = seg.color;
        ctx.fill();

        // Subtle shadow
        ctx.shadowColor = seg.color;
        ctx.shadowBlur = 8;
        ctx.fill();
        ctx.shadowBlur = 0;

        startAngle = endAngle;
    });

    // Inner circle (white center)
    ctx.beginPath();
    ctx.arc(cx, cy, innerR - 1, 0, Math.PI * 2);
    ctx.fillStyle = '#fff';
    ctx.fill();
}


/* ── Chart Tabs Switching ────────────────────────────────────── */
function switchChartTab(tab) {
    ['confirmed', 'waitlist', 'coach'].forEach(t => {
        const content = document.getElementById('chartTab' + t.charAt(0).toUpperCase() + t.slice(1));
        const btn = document.getElementById('tabBtn' + t.charAt(0).toUpperCase() + t.slice(1));
        if (content) content.style.display = (t === tab) ? 'block' : 'none';
        if (btn) btn.classList.toggle('active', t === tab);
    });
}


/* ── Trigger Official Chart Preparation ──────────────────────── */
async function triggerChartPreparation() {
    const tno = document.getElementById('chartTrainSelect').value;
    if (!tno) {
        showToast('Please select a train first!', 'error');
        return;
    }

    showToast('Preparing chart and allocating waitlisted seats...', 'info');
    const res = await api('/api/chart/prepare/' + tno, { method: 'POST' });

    if (res && res.success) {
        showToast(res.message + ' (Promoted: ' + res.promoted_count + ' passengers)', 'success');
        await loadChartPage();
        await loadTrainChart();
    } else {
        showToast((res && res.message) || 'Failed to prepare chart', 'error');
    }
}


/* ── Train Detail Chart (Manifest + Waitlist + Seat Map) ─────── */
async function loadTrainChart() {
    const tno = document.getElementById('chartTrainSelect').value;
    if (!tno) return;

    const d = await api('/api/chart/' + tno);
    if (!d || d.error) {
        document.getElementById('trainChartArea').innerHTML =
            '<div class="result-card error"><i class="fas fa-times-circle"></i><div class="result-text"><h4>Error</h4><p>Could not load chart data.</p></div></div>';
        return;
    }

    // Update Chart Status Badge
    const badge = document.getElementById('chartStatusBadge');
    if (badge) {
        if (d.chart_status && d.chart_status.prepared) {
            badge.className = 'badge';
            badge.style.background = '#2e7d32';
            badge.style.color = '#fff';
            badge.innerHTML = '<i class="fas fa-check-circle"></i> CHART PREPARED (' + d.chart_status.prepared_at + ')';
        } else {
            badge.className = 'badge badge-red';
            badge.style.background = 'var(--ir-red)';
            badge.style.color = '#fff';
            badge.innerHTML = '<i class="fas fa-clock"></i> CHART NOT PREPARED (Bookings Open)';
        }
    }

    // Update Counts
    const cnfList = d.confirmed_tickets || [];
    const wlList = d.waiting_passengers || [];
    const cnfBadge = document.getElementById('cnfCountBadge');
    const wlBadge = document.getElementById('wlCountBadge');
    if (cnfBadge) cnfBadge.innerText = cnfList.length;
    if (wlBadge) wlBadge.innerText = wlList.length;

    // 1. Render Confirmed Passenger Manifest Table
    const cnfBody = document.getElementById('confirmedPassengerBody');
    if (cnfBody) {
        if (!cnfList.length) {
            cnfBody.innerHTML = '<tr><td colspan="9" style="text-align:center;padding:1.5rem;color:var(--text-light)">No confirmed passengers for this train yet.</td></tr>';
        } else {
            cnfBody.innerHTML = cnfList.map(c => {
                const gIcon = c.Gender === 'M' ? 'fa-male' : c.Gender === 'F' ? 'fa-female' : 'fa-user';
                return '<tr>' +
                    '<td><strong>' + c.PNR + '</strong></td>' +
                    '<td><i class="fas ' + gIcon + '" style="margin-right:4px;color:var(--ir-blue)"></i><strong>' + c.PassengerName + '</strong></td>' +
                    '<td>' + (c.Age || '—') + ' / ' + c.Gender + '</td>' +
                    '<td><span class="badge" style="background:rgba(0,53,128,.1);color:var(--ir-blue)">' + c.ClassType + '</span></td>' +
                    '<td><strong>' + c.CoachNo + '</strong></td>' +
                    '<td><span class="badge" style="background:#2e7d32;color:#fff">Seat ' + c.SeatNo + '</span></td>' +
                    '<td><small style="font-weight:600;color:var(--text)">' + (c.BerthType || 'Seat') + '</small></td>' +
                    '<td>' + c.BoardName + ' (' + c.BoardingStation + ') → ' + c.ExitName + ' (' + c.ExitStation + ')</td>' +
                    '<td><span class="badge" style="background:#2e7d32;color:#fff"><i class="fas fa-check"></i> CNF</span></td>' +
                '</tr>';
            }).join('');
        }
    }

    // 2. Render Waiting List Table
    const wlBody = document.getElementById('waitingPassengerBody');
    if (wlBody) {
        if (!wlList.length) {
            wlBody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:1.5rem;color:var(--ir-green);font-weight:600"><i class="fas fa-check-circle"></i> No waitlisted passengers. All seats are cleared!</td></tr>';
        } else {
            wlBody.innerHTML = wlList.map(w => {
                const gIcon = w.Gender === 'M' ? 'fa-male' : w.Gender === 'F' ? 'fa-female' : 'fa-user';
                return '<tr>' +
                    '<td><span class="badge" style="background:var(--ir-orange);color:#fff;font-weight:800">' + w.WLNumber + '</span></td>' +
                    '<td><strong>' + w.PNR + '</strong></td>' +
                    '<td><i class="fas ' + gIcon + '" style="margin-right:4px;color:var(--ir-orange)"></i><strong>' + w.PassengerName + '</strong></td>' +
                    '<td>' + (w.Age || '—') + ' / ' + w.Gender + '</td>' +
                    '<td><span class="badge" style="background:rgba(245,124,0,.15);color:var(--ir-orange)">' + w.ClassType + '</span></td>' +
                    '<td>' + w.BoardName + ' (' + w.BoardingStation + ') → ' + w.ExitName + ' (' + w.ExitStation + ')</td>' +
                    '<td><small style="color:var(--text-light)">' + (w.BookingTime || '—') + '</small></td>' +
                    '<td><span class="badge" style="background:var(--ir-orange);color:#fff">' + w.WLNumber + ' (Waitlisted)</span></td>' +
                '</tr>';
            }).join('');
        }
    }

    // 3. Render Visual Route & Coach Grid (Tab 3)
    let html = '';

    // Route mini display
    if (d.route && d.route.length) {
        html += '<div class="route-mini">';
        d.route.forEach((s, i) => {
            html += '<span class="route-mini-stop">' + s.StationCode + '<br><small style="font-weight:400;font-size:.58rem;color:var(--text-light)">' + s.StationName + '</small></span>';
            if (i < d.route.length - 1) html += '<div class="route-mini-line"></div>';
        });
        html += '</div>';
    }

    // Per-class seat maps
    (d.classes || []).forEach(cls => {
        const coaches = {};
        (cls.seats || []).forEach(s => {
            if (!coaches[s.CoachNo]) coaches[s.CoachNo] = [];
            coaches[s.CoachNo].push(s);
        });

        Object.keys(coaches).forEach(coachNo => {
            const seats = coaches[coachNo];
            const avail = seats.filter(s => s.Status === 'Available').length;
            const occ = seats.filter(s => s.Status === 'Occupied').length;

            html += '<div class="coach-section">';
            html += '<div class="coach-header">' +
                '<h3><i class="fas fa-train"></i> Coach ' + coachNo + ' — ' + cls.classType +
                ' <span style="font-weight:400;font-size:.75rem;opacity:.8">(₹' + cls.farePerKm + '/km)</span></h3>' +
                '<div class="coach-stats">' +
                    '<span><i class="fas fa-check-circle"></i> ' + avail + ' Available</span>' +
                    '<span><i class="fas fa-user"></i> ' + occ + ' Occupied</span>' +
                '</div></div>';

            html += '<div class="seat-grid">';
            seats.forEach(s => {
                const status = s.Status.toLowerCase();
                html += '<div class="seat-cell ' + status + '">';
                html += '<div class="seat-num"><span>Seat ' + s.SeatNo + '</span><div class="seat-badge">' + s.SeatNo + '</div></div>';

                if (s.Status === 'Occupied' && s.PassengerName) {
                    const gIcon = s.Gender === 'M' ? 'fa-male' : s.Gender === 'F' ? 'fa-female' : 'fa-user';
                    html += '<div class="seat-passenger">' +
                        '<div class="pname"><i class="fas ' + gIcon + '" style="color:var(--ir-blue);margin-right:3px"></i> ' + s.PassengerName + '</div>' +
                        '<div class="pdetail">Age: ' + (s.Age || '—') + ' | PNR: ' + s.PNR + '</div>' +
                        '<div class="proute"><i class="fas fa-route"></i> ' + s.BoardingStation + ' → ' + s.ExitStation + '</div>' +
                    '</div>';
                } else {
                    html += '<div class="seat-avail-label"><i class="fas fa-check-circle"></i> Available</div>';
                }

                html += '</div>';
            });
            html += '</div></div>';
        });
    });

    document.getElementById('trainChartArea').innerHTML = html;
}


/* ── Live Railway Assistant Chat Widget ──────────────────────── */
function toggleRailChat() {
    const box = document.getElementById('railChatBox');
    if (box) {
        const isClosed = box.style.display === 'none' || !box.style.display;
        box.style.display = isClosed ? 'flex' : 'none';
        if (isClosed) {
            document.getElementById('railChatInput').focus();
        }
    }
}

async function sendRailChat() {
    const input = document.getElementById('railChatInput');
    const msg = input.value.trim();
    if (!msg) return;

    const chatMessages = document.getElementById('railChatMessages');
    chatMessages.innerHTML += '<div class="chat-msg user">' + escapeHtml(msg) + '</div>';
    input.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Loading indicator
    const tempId = 'loading-' + Date.now();
    chatMessages.innerHTML += '<div class="chat-msg bot" id="' + tempId + '"><i class="fas fa-spinner fa-spin"></i> Checking railway system...</div>';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    const res = await api('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
    });

    const loader = document.getElementById(tempId);
    if (loader) loader.remove();

    if (res && res.reply) {
        // Format markdown bold & line breaks
        let formatted = res.reply
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>')
            .replace(/• /g, '&bull; ');

        chatMessages.innerHTML += '<div class="chat-msg bot">' + formatted + '</div>';

        // If command triggered chart preparation
        if (res.action === 'prepare_chart' && res.trainNo) {
            document.getElementById('chartTrainSelect').value = res.trainNo;
            triggerChartPreparation();
        }
    } else {
        chatMessages.innerHTML += '<div class="chat-msg bot">Sorry, could not process request.</div>';
    }
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.innerText = text;
    return div.innerHTML;
}


/* ── Auto-refresh chart after booking/cancel ─────────────────── */
function refreshChartIfActive() {
    const chartPage = document.getElementById('page-chart');
    if (chartPage && chartPage.classList.contains('active')) {
        loadChartPage();
    }
}

/* ── DBMS ACADEMIC QUERIES LAB & LIVE RUNNER ─────────────────── */
let _academicQueriesCache = [];

async function loadQueriesPage() {
    if (!_academicQueriesCache.length) {
        const queries = await api('/api/sql-queries');
        if (queries && queries.length) {
            _academicQueriesCache = queries;
        }
    }
    const select = document.getElementById('academicQuerySelect');
    if (select && _academicQueriesCache.length) {
        select.innerHTML = _academicQueriesCache.map((q) => 
            '<option value="' + q.id + '">[' + q.category + '] ' + q.title + '</option>'
        ).join('');
        onAcademicQuerySelectChange();
    }
}

function onAcademicQuerySelectChange() {
    const qid = document.getElementById('academicQuerySelect')?.value;
    const query = _academicQueriesCache.find(q => q.id === qid);
    if (!query) return;

    document.getElementById('queryTitleText').innerText = query.title;
    document.getElementById('queryCategoryBadge').innerText = query.category;
    document.getElementById('queryDescriptionText').innerHTML = 
        '<strong>Objective:</strong> ' + query.description + ' &bull; <span style="color:var(--ir-blue);font-weight:600"><i class="fas fa-tag"></i> Concept: ' + query.concept + '</span>';
    document.getElementById('querySQLCode').innerText = query.sql;
}

async function executeSelectedQuery() {
    const qid = document.getElementById('academicQuerySelect')?.value;
    if (!qid) return;

    const resultsArea = document.getElementById('queryResultsArea');
    const statsBadge = document.getElementById('queryStatsBadge');
    resultsArea.innerHTML = '<div style="text-align:center;padding:2rem"><i class="fas fa-spinner fa-spin fa-2x" style="color:var(--ir-blue)"></i><p style="margin-top:.5rem">Executing query in MySQL...</p></div>';

    const res = await api('/api/sql-queries/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query_id: qid })
    });

    renderQueryResults(res);
}

function toggleCustomSQLConsole() {
    const drawer = document.getElementById('customSQLDrawer');
    if (drawer) {
        const isHidden = drawer.style.display === 'none' || !drawer.style.display;
        drawer.style.display = isHidden ? 'block' : 'none';
        if (isHidden) {
            const currentSQL = document.getElementById('querySQLCode')?.innerText || '';
            document.getElementById('customSQLInput').value = currentSQL;
        }
    }
}

async function executeCustomSQL() {
    const sql = document.getElementById('customSQLInput')?.value.trim();
    if (!sql) {
        toast('Please enter a SQL query', 'error');
        return;
    }

    const resultsArea = document.getElementById('queryResultsArea');
    resultsArea.innerHTML = '<div style="text-align:center;padding:2rem"><i class="fas fa-spinner fa-spin fa-2x" style="color:var(--ir-blue)"></i><p style="margin-top:.5rem">Executing custom query...</p></div>';

    const res = await api('/api/sql-queries/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sql: sql })
    });

    renderQueryResults(res);
}

function renderQueryResults(res) {
    const resultsArea = document.getElementById('queryResultsArea');
    const statsBadge = document.getElementById('queryStatsBadge');

    if (!res || !res.success) {
        statsBadge.innerHTML = '<span style="color:var(--ir-red)"><i class="fas fa-times-circle"></i> Execution Failed</span>';
        resultsArea.innerHTML = '<div class="result-card error"><i class="fas fa-exclamation-triangle"></i><div class="result-text"><h4>SQL Error</h4><p>' + ((res && res.message) || 'Unknown error executing query') + '</p></div></div>';
        return;
    }

    statsBadge.innerHTML = '<span style="color:#2e7d32"><i class="fas fa-check-circle"></i> Success</span> &bull; <strong>' + res.count + ' rows</strong> in <strong>' + res.execution_time_ms + ' ms</strong>';

    if (!res.rows || !res.rows.length) {
        resultsArea.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--text-light)">Query executed successfully (0 rows returned).</div>';
        return;
    }

    let html = '<table class="table"><thead><tr>';
    res.columns.forEach(col => {
        html += '<th>' + col + '</th>';
    });
    html += '</tr></thead><tbody>';

    res.rows.forEach(row => {
        html += '<tr>';
        res.columns.forEach(col => {
            const val = row[col];
            html += '<td>' + (val !== null && val !== undefined ? val : '<span style="color:var(--text-light);font-style:italic">NULL</span>') + '</td>';
        });
        html += '</tr>';
    });
    html += '</tbody></table>';

    resultsArea.innerHTML = html;
}

function copyQuerySQL() {
    const sql = document.getElementById('querySQLCode')?.innerText;
    if (sql) {
        navigator.clipboard.writeText(sql);
        toast('SQL copied to clipboard!', 'success');
    }
}

/* ── Init ────────────────────────────────────────────────────── */
loadDashboard();

