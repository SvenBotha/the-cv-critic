document.getElementById('cvForm').addEventListener('submit', function(event) {
    event.preventDefault();
    console.log('Form submitted');
    const fileInput = document.getElementById('cv');
    if (!fileInput.files.length) {
        alert("Please select a file before uploading.");
        return; // Stop execution if no file is selected
    }


    const formData = new FormData(this);
    const submitButton = document.querySelector('.submit-button');
    const spinnerContainer = document.getElementById('spinner-container');

    // Initially hide the button text and show the spinner
    submitButton.innerHTML = '';  // Clear the button text
    spinnerContainer.style.display = 'block';  // Show the spinner
    submitButton.classList.add('shrink');  // Shrink the button

    // Apply the class to make the spinner appear smoothly
    setTimeout(function() {
        spinnerContainer.classList.add('show');
        console.log("2", fileInput.files.length);
        submitButton.classList.add('hidden');  
    }, 300);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '', true);

    // Set up the progress event handler to update the progress bar (if needed)
    xhr.upload.onprogress = function(event) {
        if (event.lengthComputable) {
            const percent = (event.loaded / event.total) * 100;
            // Optionally update a progress bar here
        }
    };

    // On successful upload
    xhr.onload = function() {
        if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            if (data.error) {
                alert(data.error);
            } else {
                document.getElementById('score').textContent = data.score;
                const recommendationsList = document.getElementById('recommendations');
                recommendationsList.innerHTML = '';  // Clear previous recommendations
                const ul = document.createElement('ul');  // Create a new unordered list
                data.recommendations.forEach(rec => {
                    const li = document.createElement('li');
                    li.textContent = rec;
                    ul.appendChild(li);
                });
                recommendationsList.appendChild(ul);  // Append the list to the results container
                document.getElementById('results').style.display = 'block';
            }
        } else {
            alert('Upload failed');
        }
    };

    // Handle errors
    xhr.onerror = function() {
        alert("An error occurred during the file upload.");
    };

    // Send the request
    xhr.send(formData);

    // After the request finishes (successful or error), revert the button back to its original state
    xhr.onloadend = function() {
        // After processing, restore the button
        submitButton.classList.remove('shrink'); // Restore the button size
        submitButton.classList.remove('hidden'); // Restore the button size
        submitButton.innerHTML = 'Upload'; // Reset button text back
        spinnerContainer.classList.remove('show'); // Hide the spinner
    };
});

function updateFileName() {
    var fileInput = document.getElementById('cv');
    var fileName = fileInput.files[0] ? fileInput.files[0].name : "No file chosen";
    document.getElementById('file-name').textContent = fileName;
}
