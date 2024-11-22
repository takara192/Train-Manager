function startCamera() {
    const videoElement = document.getElementById("camera-feed")

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia()) {
        navigator.mediaDevices.getUserMedia({video: true}).then(
            stream => {
                videoElement.srcObject = stream;
            }
        ).catch(error => {
            console.error("Error accessing the camera: ", error);
        });
    } else {
        alert("Your browser does not support accessing the camera.");
    }
}