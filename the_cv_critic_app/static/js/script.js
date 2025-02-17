document.getElementById('cvForm').addEventListener('submit', function(event) {
    event.preventDefault();

    // Check if a file has been selected
    const fileInput = document.getElementById('cv');
    if (!fileInput.files.length) {
        alert("Please select a file before uploading.");
        return;
    }


    const formData = new FormData(this);
    const submitButton = document.querySelector('.submit-button');
    const spinnerContainer = document.getElementById('spinner-container');

    // Initially hide the button text and show the spinner
    submitButton.innerHTML = ''; 
    spinnerContainer.style.display = 'block';  
    submitButton.classList.add('shrink'); 

    // Show the spinner and hide the button text after a short delay
    setTimeout(function() {
        spinnerContainer.classList.add('show');
        submitButton.classList.add('hidden');  
    }, 300);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '', true);

    // On successful upload
    xhr.onload = function() {
        if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            if (data.error) {
                alert(data.error);
            } else {
                document.getElementById('score').textContent = data.score;
                const recommendationsList = document.getElementById('recommendations');
                recommendationsList.innerHTML = ''; 
                const ul = document.createElement('ul'); 
                data.recommendations.forEach(rec => {
                    const li = document.createElement('li');
                    li.textContent = rec;
                    ul.appendChild(li);
                });
                recommendationsList.appendChild(ul);
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
