document.getElementById('cvForm').addEventListener('submit', function(event) {
    event.preventDefault();

    // Show the spinner before starting the request
    document.getElementById('spinner').style.display = 'block';

    const formData = new FormData(this);

    fetch('', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        // Hide the spinner once the request is completed
        document.getElementById('spinner').style.display = 'none';

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
    })
    .catch(error => {
        // Hide the spinner if an error occurs
        document.getElementById('spinner').style.display = 'none';
        alert("An error occurred: " + error);
    });
});

function updateFileName() {
    var fileInput = document.getElementById('cv');
    var fileName = fileInput.files[0] ? fileInput.files[0].name : "No file chosen";
    document.getElementById('file-name').textContent = fileName;
}
