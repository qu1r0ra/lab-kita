const form = document.querySelector("#forms")


form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = form.email.value
    const password = form.password.value

    if(email.length < 11){ //If the length of the submitted email is too short
        alert("Email must be at least 11 characters long");
        return;
    }
    if(!password){ //If password doesnt exist       
       alert("Password required!");
       return;
    }  

    try{
        const response = await fetch("/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ email, password})
        });

        const data = await response.json();

        if(response.ok) {
            alert(data.message);
        }else
            alert(data.message);

    }catch (error) {
        console.error(error);
        alert("Error!")
    }

})