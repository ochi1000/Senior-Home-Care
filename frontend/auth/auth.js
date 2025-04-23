const loginForm = document.getElementById("loginForm");

  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("user_id").value;
    const password = document.getElementById("password").value;

    try {
      const response = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
      });

      const result = await response.json();
      console.log(result);
      if (response.ok) {
        localStorage.setItem("access_token", result.access_token);
        // document.getElementById("message").textContent = "Login successful!";
        alert("Login successful!");
        window.location.href = "../index.html";
        // Redirect or load protected data here
      } else {
        alert("Login failed!");
      }
    } catch (error) {
      console.error("Login error:", error);
      document.getElementById("message").textContent = "Something went wrong.";
    }
  });



  