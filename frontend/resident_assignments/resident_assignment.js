var token = localStorage.getItem("access_token");

const tableBody = document.querySelector("#assignmentTable tbody");

fetch('http://localhost:5000/assignments', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      "Authorization": `Bearer ${token}`
    }
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Failed to fetch assignments');
    }
    return response.json();
  })
  .then(data => {
    console.log(data);
    if (Array.isArray(data) && data.length > 0) {
      data.forEach(assignment => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td>${assignment.resident_first_name} ${assignment.resident_last_name}</td>
          <td>${assignment.caregiver_first_name} ${assignment.caregiver_last_name}</td>
          <td>${assignment.assignment_status || '—'}</td>
          <td>${assignment.assignment_end_date || '—'}</td>
        `;

        tableBody.appendChild(row);
      });
    } else {
      const row = document.createElement("tr");
      row.innerHTML = `<td colspan="6">No assignments found</td>`;
      tableBody.appendChild(row);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="6">Failed to load data</td>`;
    tableBody.appendChild(row);
  });


const residentSelect = document.getElementById('residentSelect');
    const caregiverSelect = document.getElementById('caregiverSelect');

    // Fetch Residents
    fetch('http://localhost:5000/residents', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          "Authorization": `Bearer ${token}`
        }
      })
      .then(res => res.json())
      .then(data => {
        // console.log(data);
        data.forEach(res => {
          const option = document.createElement('option');
          option.value = `${res.first_name}|${res.last_name}|${res.date_of_birth}`;
          option.textContent = `${res.first_name} ${res.last_name}`;
          residentSelect.appendChild(option);
        });
      });

    // Fetch Caregivers
    fetch('http://localhost:5000/caregivers', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          "Authorization": `Bearer ${token}`
        }
      })
      .then(res => res.json())
      .then(data => {
        data.forEach(cg => {
          const option = document.createElement('option');
          option.value = `${cg.first_name}|${cg.last_name}|${cg.phone_number}`;
          option.textContent = `${cg.first_name} ${cg.last_name}`;
          caregiverSelect.appendChild(option);
        });
      });

    // Submit Assignment
    document.getElementById('assignmentForm').addEventListener('submit', function(e) {
      e.preventDefault();

      const [rFirst, rLast, rDob] = residentSelect.value.split('|');
      const [cFirst, cLast, cPhone] = caregiverSelect.value.split('|');

      const assignment = {
        resident_first_name: rFirst,
        resident_date_of_birth: rDob, // Placeholder, replace with actual DOB
        caregiver_phone_number: cPhone,
      };

      fetch('http://localhost:5000/assignments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(assignment)
      })
      .then(res => res.json())
      .then(response => {
        alert("Assignment created successfully!");
      })
      .catch(err => {
        console.error('Error creating assignment:', err);
        alert("Something went wrong.");
      });
    });
  