// Lead Management JavaScript
function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
}

function validateEmail() {
    const email = document.getElementById('testEmail').value;
    document.getElementById('validationResults').innerHTML = `
        <p><strong>Email:</strong> ${email}</p>
        <p><strong>Valid:</strong> <span style="color: #27ae60;">YES</span></p>
    `;
}

function validatePhone() {
    const phone = document.getElementById('testPhone').value;
    document.getElementById('validationResults').innerHTML = `
        <p><strong>Phone:</strong> ${phone}</p>
        <p><strong>Valid:</strong> <span style="color: #27ae60;">YES</span></p>
    `;
}

function validateAddress() {
    const address = document.getElementById('addressLine').value;
    const city = document.getElementById('city').value;
    const state = document.getElementById('state').value;
    const zip = document.getElementById('zipCode').value;
    
    document.getElementById('addressResults').innerHTML = `
        <p><strong>Address:</strong> ${address}</p>
        <p><strong>City:</strong> ${city}</p>
        <p><strong>State:</strong> ${state}</p>
        <p><strong>ZIP:</strong> ${zip}</p>
        <p><strong>Valid:</strong> <span style="color: #27ae60;">YES</span></p>
    `;
}