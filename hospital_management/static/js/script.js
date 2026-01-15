// ==================== API BASE URL ====================
const API_BASE = 'http://127.0.0.1:5000/api';

// ==================== MODAL FUNCTIONS ====================
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}

// ==================== DASHBOARD ====================
async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const stats = await response.json();
        
        document.getElementById('totalPatients').textContent = stats.total_patients;
        document.getElementById('totalDoctors').textContent = stats.total_doctors;
        document.getElementById('pendingAppointments').textContent = stats.pending_appointments;
        document.getElementById('todayAppointments').textContent = stats.today_appointments;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// ==================== PATIENTS ====================
async function loadPatients() {
    try {
        const response = await fetch(`${API_BASE}/patients`);
        const patients = await response.json();
        
        const tbody = document.getElementById('patientsTableBody');
        tbody.innerHTML = '';
        
        patients.forEach(patient => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${patient.patient_id}</td>
                <td>${patient.first_name} ${patient.last_name}</td>
                <td>${patient.date_of_birth || '-'}</td>
                <td>${patient.gender || '-'}</td>
                <td>${patient.phone || '-'}</td>
                <td>${patient.email || '-'}</td>
                <td>${patient.blood_group || '-'}</td>
                <td>
                    <button class="btn btn-danger" onclick="deletePatient(${patient.patient_id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading patients:', error);
    }
}

async function addPatient(event) {
    event.preventDefault();
    
    const form = document.getElementById('patientForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch(`${API_BASE}/patients`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert('Patient added successfully!');
            closeModal('patientModal');
            form.reset();
            loadPatients();
        } else {
            alert('Error adding patient');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error adding patient');
    }
}

async function deletePatient(patientId) {
    if (confirm('Are you sure you want to delete this patient?')) {
        try {
            const response = await fetch(`${API_BASE}/patients/${patientId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                alert('Patient deleted successfully!');
                loadPatients();
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }
}

// ==================== DOCTORS ====================
async function loadDoctors() {
    try {
        const response = await fetch(`${API_BASE}/doctors`);
        const doctors = await response.json();
        
        const grid = document.getElementById('doctorsGrid');
        grid.innerHTML = '';
        
        doctors.forEach(doctor => {
            const card = document.createElement('div');
            card.className = 'doctor-card';
            card.innerHTML = `
                <h3>Dr. ${doctor.first_name} ${doctor.last_name}</h3>
                <p class="specialization">${doctor.specialization || 'General'}</p>
                <div class="info-item">
                    <i class="fas fa-briefcase"></i>
                    <span>${doctor.experience_years || 0} years experience</span>
                </div>
                <div class="info-item">
                    <i class="fas fa-phone"></i>
                    <span>${doctor.phone || 'Not provided'}</span>
                </div>
                <div class="info-item">
                    <i class="fas fa-envelope"></i>
                    <span>${doctor.email || 'Not provided'}</span>
                </div>
                <div class="info-item">
                    <i class="fas fa-rupee-sign"></i>
                    <span>₹${doctor.consultation_fee || 0} per visit</span>
                </div>
                <div class="info-item">
                    <i class="fas fa-calendar-alt"></i>
                    <span>${doctor.available_days || 'All days'}</span>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading doctors:', error);
    }
}

async function addDoctor(event) {
    event.preventDefault();
    
    const form = document.getElementById('doctorForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch(`${API_BASE}/doctors`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert('Doctor added successfully!');
            closeModal('doctorModal');
            form.reset();
            loadDoctors();
        } else {
            alert('Error adding doctor');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error adding doctor');
    }
}

// ==================== APPOINTMENTS ====================
async function loadAppointments() {
    try {
        const response = await fetch(`${API_BASE}/appointments`);
        const appointments = await response.json();
        
        const tbody = document.getElementById('appointmentsTableBody');
        tbody.innerHTML = '';
        
        appointments.forEach(apt => {
            const row = document.createElement('tr');
            const statusClass = apt.status.toLowerCase();
            
            row.innerHTML = `
                <td>${apt.appointment_id}</td>
                <td>${apt.patient_name}</td>
                <td>Dr. ${apt.doctor_name}</td>
                <td>${apt.specialization}</td>
                <td>${apt.appointment_date}</td>
                <td>${apt.appointment_time}</td>
                <td><span class="status-badge ${statusClass}">${apt.status}</span></td>
                <td>
                    ${apt.status === 'Scheduled' ? `
                        <button class="btn btn-success" onclick="updateAppointmentStatus(${apt.appointment_id}, 'Completed')">
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="btn btn-danger" onclick="updateAppointmentStatus(${apt.appointment_id}, 'Cancelled')">
                            <i class="fas fa-times"></i>
                        </button>
                    ` : '-'}
                </td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading appointments:', error);
    }
}

async function loadPatientsDropdown() {
    try {
        const response = await fetch(`${API_BASE}/patients`);
        const patients = await response.json();
        
        const select = document.getElementById('patientSelect');
        patients.forEach(patient => {
            const option = document.createElement('option');
            option.value = patient.patient_id;
            option.textContent = `${patient.first_name} ${patient.last_name}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading patients dropdown:', error);
    }
}

async function loadDoctorsDropdown() {
    try {
        const response = await fetch(`${API_BASE}/doctors`);
        const doctors = await response.json();
        
        const select = document.getElementById('doctorSelect');
        doctors.forEach(doctor => {
            const option = document.createElement('option');
            option.value = doctor.doctor_id;
            option.textContent = `Dr. ${doctor.first_name} ${doctor.last_name} - ${doctor.specialization}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading doctors dropdown:', error);
    }
}

async function addAppointment(event) {
    event.preventDefault();
    
    const form = document.getElementById('appointmentForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch(`${API_BASE}/appointments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert('Appointment booked successfully!');
            closeModal('appointmentModal');
            form.reset();
            loadAppointments();
        } else {
            alert('Error booking appointment');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error booking appointment');
    }
}

async function updateAppointmentStatus(appointmentId, status) {
    try {
        const response = await fetch(`${API_BASE}/appointments/${appointmentId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status })
        });
        
        if (response.ok) {
            alert(`Appointment ${status.toLowerCase()} successfully!`);
            loadAppointments();
        }
    } catch (error) {
        console.error('Error:', error);
    }
}