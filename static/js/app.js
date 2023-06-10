// Fetch the authentication status
fetch('http://localhost:5000/is_authenticated')
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Received JSON response:', data);

        // Based on whether the user is authenticated, show the appropriate view
        const beforeVerification = document.getElementById('before_verification');
        const afterVerification = document.getElementById('after_verification');

        if (data.authorized) {
            console.log('User is authorized');
            beforeVerification.classList.add('hidden');
            afterVerification.classList.remove('hidden');
            //fetchDataAndUpdateView();  // Function to fetch user data and update the view

        } else {
            console.log('User is not authorized');

            afterVerification.classList.add('hidden');
            beforeVerification.classList.remove('hidden');
        }
    })
    .catch(error => {
        console.log('Error:', error);
    });