document.addEventListener("DOMContentLoaded", function () {
    const navItems = document.querySelectorAll(".nav-item");
    const contentArea = document.getElementById("content-area");

    function loadContent(page) {
        fetch(`pages/${page}.html`).then(
            r => {
                if (!r.ok) {
                    throw new Error("Network response was not ok " + r.statusText);
                }

                return r.text();
            }
        ).then(
            value => {
                contentArea.innerHTML = value;

                if (page === "face-recognize") {
                    loadScript("scripts/face-recognize-script.js", function () {
                        if (typeof startCamera === "function") {
                            startCamera();
                        } else {
                            console.error("startCamera is not defined even after script load.");
                        }
                    });
                }
                else if (page === "history") {
                    fetchActivityLog();
                } else if (page === "all-users") {
                    fetchUserDetails();
                } else if (page === "register-user") {
                    attachRegisterFormListener();
                }
            }
        ).catch(error => {
            console.error("Error loading page: ", error);
            contentArea.innerHTML = "<p>Error loading content.</p>";
        });
    }

    loadContent("face-recognize");

    function loadScript(url, callback) {
        const script = document.createElement("script");
        script.type = "text/javascript";
        script.src = url;

        script.onload = function () {
            console.log(`${url} has been loaded successfully.`);
            if (callback) callback();
        };

        script.onerror = function () {
            console.error(`Error loading script: ${url}`);
        };

        document.head.appendChild(script);
    }

    navItems.forEach(navItem => {
        navItem.addEventListener("click", function (e) {
            e.preventDefault();

            navItems.forEach(item => item.classList.remove("active"));

            navItem.classList.add("active");

            loadContent(navItem.getAttribute("data-content"));
        });
    });

    document.getElementById("userRegisterForm").addEventListener("click", function () {

    });

    function attachRegisterFormListener() {
        const registerForm = document.getElementById("userRegisterForm");
        if (registerForm) {
            registerForm.addEventListener("submit", async function (event) {
                event.preventDefault();

                const formData = new FormData(this);

                try {
                    const response = await fetch("http://127.0.0.1:8000/user/register", {
                        method: "POST",
                        body: formData,
                        headers: {
                            "Accept": "application/json"
                        }
                    });

                    if (response.ok) {
                        const result = await response.json();
                        alert(result.message || "Đăng ký người dùng thành công!");
                    } else {
                        const errorText = await response.text();
                        alert("Đăng ký thất bại: " + errorText);
                    }
                } catch (error) {
                    console.error("Error during registration:", error);
                    alert("Có lỗi xảy ra trong quá trình đăng ký.");
                }
            });
        } else {
            console.log("cannot fieedji");
        }
    }
});

function takePhotoAndUpload() {
    const videoElement = document.getElementById("camera-feed");
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");

    canvas.height = videoElement.videoHeight;
    canvas.width = videoElement.videoWidth;

    context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append("file", blob, "photo.jpg");

        try {
            const response = await fetch("http://127.0.0.1:8000/check_in_out/", {
                method: "POST",
                body: formData,
                headers: {
                    "Accept": "application/json"
                },
            });

            if (response.ok) {
                const jsonResponse = await response.json();

                alert(jsonResponse.message);
            } else {
                const errorText = await response.text();
                alert("Failed to upload photo: " + errorText);
            }

        } catch (error) {
            console.error("Error uploading photo:", error);
            alert("An error occurred while uploading the photo.");
        }
    }, "image/png");

}

async function fetchActivityLog() {
    try {
        const response = await fetch("http://127.0.0.1:8000/check_in_out/get_all", {
            headers: {
                "Accept": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        populateTable(data);
    } catch (error) {
        console.error("Error fetching activity log:", error);
    }
}

function populateTable(data) {
    const tbody = document.getElementById("activity-log-body");
    tbody.innerHTML = "";

    data.forEach((log) => {
        const row = document.createElement("tr");

        const idCell = document.createElement("td");
        idCell.textContent = log.log_id;

        const userCell = document.createElement("td");
        userCell.innerHTML = `${log.full_name}`;

        const actionCell = document.createElement("td");
        actionCell.className = "action";
        actionCell.textContent = log.action;
        if (log.action === "CHECK_IN") {
            actionCell.style.color = "#28a745";
        } else if (log.action === "CHECK_OUT") {
            actionCell.style.color = "#dc3545";
        }

        const timeCell = document.createElement("td");
        const checkTime = new Date(log.check_time);
        timeCell.textContent = checkTime.toLocaleString("vi-VN", {
            dateStyle: "medium",
            timeStyle: "short",
            timeZone: "UTC"
        });

        row.appendChild(idCell);
        row.appendChild(userCell);
        row.appendChild(actionCell);
        row.appendChild(timeCell);

        tbody.appendChild(row);
    });
}

function populateUserTable(data) {
    const tbody = document.getElementById("user-details-body");
    tbody.innerHTML = ""; // Clear existing rows

    data.forEach((user) => {
        const row = document.createElement("tr");

        row.onclick = function() {
            sessionStorage.setItem('selectedUserId', user.user_id);
            window.location.href = `/user-profile`;
        };

        const idCell = document.createElement("td");
        idCell.textContent = user.user_id;

        const nameCell = document.createElement("td");
        nameCell.textContent = user.full_name;

        const dobCell = document.createElement("td");
        const dob = new Date(user.dob);
        dobCell.textContent = dob.toLocaleDateString("vi-VN", {
            year: "numeric",
            month: "long",
            day: "numeric"
        });

        const addressCell = document.createElement("td");
        addressCell.textContent = user.address;

        const phoneCell = document.createElement("td");
        phoneCell.textContent = user.phone_number;

        row.appendChild(idCell);
        row.appendChild(nameCell);
        row.appendChild(dobCell);
        row.appendChild(addressCell);
        row.appendChild(phoneCell);

        tbody.appendChild(row);
    });
}

async function fetchUserDetails() {
    try {
        const response = await fetch("http://127.0.0.1:8000/user/", {
            headers: {
                "Accept": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        populateUserTable(data);
    } catch (error) {
        console.error("Error fetching user details:", error);
    }
}