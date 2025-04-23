// Retrieve the token from localStorage
var token = localStorage.getItem("access_token");

// Function to parse a JWT token
function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = decodeURIComponent(
      atob(base64Url)
        .split('')
        .map(function (c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join('')
    );
    return JSON.parse(base64);
  } catch (e) {
    return null;
  }
}

// Function to show role-based UI elements
function showRoleBasedUI() {
  if (token) {
    const user = parseJwt(token);
    const role = user?.sub?.role;
    console.log(token, user, role);
    if (user && role) {
      if (role === "admin") {
        document.getElementById("admin-panel").style.display = "block";

        // Select all elements with the class name 'myClass'
        var elements = document.getElementsByClassName('admin');

        // Loop through each element and set its display property to 'block'
        for (var i = 0; i < elements.length; i++) {
            elements[i].style.display = 'block';
        }
      } else if (role === "caregiver") {
        document.getElementById("caregiver-panel").style.display = "block";
        // Select all elements with the class name 'myClass'
        var elements = document.getElementsByClassName('caregiver');

        // Loop through each element and set its display property to 'block'
        for (var i = 0; i < elements.length; i++) {
            elements[i].style.display = 'block';
        }
      } else if (role === "resident") {
        document.getElementById("resident-panel").style.display = "block";
        // Select all elements with the class name 'myClass'
        var elements = document.getElementsByClassName('resident');

        // Loop through each element and set its display property to 'block'
        for (var i = 0; i < elements.length; i++) {
            elements[i].style.display = 'block';
        }
      }
      document.getElementById("logout").style.display = "block";
    }
  } else {
    // Not logged in — show login/register section
    document.getElementById("auth-section").style.display = "block";
  }
}


function logout() {
  localStorage.removeItem("access_token");  // Remove token from localStorage
  alert("You have been logged out.");
  // window.location.href = "/login.html";    // Redirect to login page
}

const totalApiUrl = 'http://127.0.0.1:5000/total-caregivers'; // Change this to your Flask endpoint

    
async function fetchSchedules() {
  try {
    const response = await fetch('http://localhost:5000/schedules', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const schedules = await response.json();
    const tbody = document.querySelector('#schedulesTable tbody');
    tbody.innerHTML = '';

    schedules.forEach(schedule => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${schedule.schedule_id}</td>
        <td>${schedule.resident_name || ''}</td>
        <td>${schedule.caregiver_name || ''}</td>
        <td>${new Date(schedule.shift_date).toLocaleDateString()}</td>
        <td>${schedule.shift_start}</td>
        <td>${schedule.shift_end}</td>
      `;
      tbody.appendChild(row);
    });
  } catch (error) {
    console.error('Error fetching schedules:', error);
  }
}
      
      async function cfetchSchedules() {
        try {
          const response = await fetch('http://localhost:5000/schedulesw', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
    
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
    
          const schedules = await response.json();
          const tbody = document.querySelector('#cschedulesTable tbody');
          tbody.innerHTML = '';
    
          schedules.forEach(schedule => {
            const row = document.createElement('tr');
            row.innerHTML = `
              <td>${schedule.schedule_id}</td>
              <td>${schedule.resident_name || ''}</td>
              <td>${schedule.caregiver_name || ''}</td>
              <td>${new Date(schedule.shift_date).toLocaleDateString()}</td>
              <td>${schedule.shift_start}</td>
              <td>${schedule.shift_end}</td>
            `;
            tbody.appendChild(row);
          });
        } catch (error) {
          console.error('Error fetching schedules:', error);
        }
      }
      
      async function rfetchSchedules() {
        try {
          const response = await fetch('http://localhost:5000/schedulesw', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
    
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
    
          const schedules = await response.json();
          const tbody = document.querySelector('#rschedulesTable tbody');
          tbody.innerHTML = '';
    
          schedules.forEach(schedule => {
            const row = document.createElement('tr');
            row.innerHTML = `
              <td>${schedule.schedule_id}</td>
              <td>${schedule.resident_name || ''}</td>
              <td>${schedule.caregiver_name || ''}</td>
              <td>${new Date(schedule.shift_date).toLocaleDateString()}</td>
              <td>${schedule.shift_start}</td>
              <td>${schedule.shift_end}</td>
            `;
            tbody.appendChild(row);
          });
        } catch (error) {
          console.error('Error fetching schedules:', error);
        }
      }
    

// Initialize the UI on page load
window.onload = function () {
  showRoleBasedUI();
  fetchSchedules();
  cfetchSchedules();
  rfetchSchedules();
};

fetch(totalApiUrl, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    "Authorization": `Bearer ${token}`
  }
})
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to fetch data');
    }
    return response.json();
  })
  .then(data => {
    const totalResidentsElement = document.getElementById("total-caregivers");
    if (totalResidentsElement) {
      totalResidentsElement.textContent = data.total_caregivers; // Set the result
    }
  })
  .catch(error => {
    console.error('Error fetching caregivers:', error);
  });
  
const totalresApiUrl = 'http://127.0.0.1:5000/total-residents'; // Change this to your Flask endpoint

fetch(totalresApiUrl, {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    "Authorization": `Bearer ${token}`
  }
})
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to fetch data');
    }
    return response.json();
  })
  .then(data => {
    const totalResidentsElement = document.getElementById("total-residents");
    if (totalResidentsElement) {
      totalResidentsElement.textContent = data.total_residents; // Set the result
    }
  })
  .catch(error => {
    console.error('Error fetching caregivers:', error);
  });
