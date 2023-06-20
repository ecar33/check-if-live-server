async function getAuthenticationStatus() {
    const response = await fetch('http://localhost:5000/is_authenticated');

    if (!response.ok){
        throw new Error(`HTTP error! Error status: ${response.status}`)
    }
    return response.json();
}

async function getUserData(){
    const response = await fetch('http://localhost:5000/fetch_data');

    if (!response.ok){
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

async function main() {
    try{
        const authStatus = await getAuthenticationStatus();
            const beforeVerification = document.getElementById("before_verification")
            const afterVerification = document.getElementById("after_verification")
        if (authStatus.authorized) {
            try{
                const userData = await getUserData();
                userDataView = document.getElementById("user_data_view")
                userDataView.textContent = JSON.stringify(userData)



            } catch (error) {
                console.error(`Error: ${error}`)
            }

            beforeVerification.classList.add('visually-hidden');
            afterVerification.classList.remove('visually-hidden');
        }
        else {
            beforeVerification.classList.remove('visually-hidden');
            afterVerification.classList.add('visually-hidden');
        }
    } catch (error) {
        console.error(`Error: ${error}`)
    }
}
document.addEventListener('DOMContentLoaded', (event) => {
    main();
});