document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#create-resident-form');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        const formData = {
            first_name: form.first_name.value,
            last_name: form.last_name.value,
            date_of_birth: form.dob.value,
            gender: form.gender.value,
            phone_number: form.phone.value,
            address: form.address.value,
            emergency_contact_name: form.em_contact_name.value,
            emergency_contact_phone: form.em_contact_phone.value,
        };

        console.log(formData);
        try {
            const response = await fetch('http://127.0.0.1:5000/residents', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                const result = await response.json();
                alert('Resident created successfully!');
                console.log(result);
            } else {
                const error = await response.json();
                alert(`Error: ${error.message}`);
            }
        } catch (err) {
            console.error('Error:', err);
            alert('An error occurred while creating the resident.');
        }
    });
});

const apiUrl = 'http://127.0.0.1:5000/residents'; // Change this to your Flask endpoint

    fetch(apiUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }
        return response.json();
      })
      .then(data => {
        console.log(data);
        const tableBody = document.querySelector("#residentsTable tbody");

        if (Array.isArray(data)) {
          data.forEach(resident => {
            const row = document.createElement("tr");

            row.innerHTML = `
              <td>${resident.first_name} ${resident.last_name}</td>
              <td>${resident.gender}</td>
              <td>${resident.admission_date}</td>
              <td>${resident.emergency_contact_name}</td>
              <td>${resident.emergency_contact_phone}</td>
              <td><i class="bi bi-pencil text-primary"></i> <i class="bi bi-trash text-danger"></i></td>
            `;

            tableBody.appendChild(row);
          });
        } else {
          const row = document.createElement("tr");
          row.innerHTML = `<td colspan="6">No residents found</td>`;
          tableBody.appendChild(row);
        }
      })
      .catch(error => {
        console.error('Error fetching residents:', error);
      });