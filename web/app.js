const loginForm = document.getElementById("loginForm");
const message = document.getElementById("message");


async function checkSession() {
    const token = localStorage.getItem("access_token");

    if (!token) {
        return;
    }

    const response = await fetch("http://127.0.0.1:8000/me", {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (response.ok) {
        const data = await response.json();

        loginForm.style.display = "none";
        message.textContent = "Hos geldin, " + data.username;
    } else {
        localStorage.removeItem("access_token");
        loginForm.style.display = "block";
        message.textContent = "Oturum suresi doldu. Tekrar giris yap.";
    }
}


loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch("http://127.0.0.1:8000/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    });

    const data = await response.json();

    if (response.ok) {
        localStorage.setItem(
            "access_token",
            data.access_token
        );

        loginForm.style.display = "none";
        message.textContent = "Hos geldin, " + username;
    } else {
        message.textContent = data.detail;
    }
});


checkSession();