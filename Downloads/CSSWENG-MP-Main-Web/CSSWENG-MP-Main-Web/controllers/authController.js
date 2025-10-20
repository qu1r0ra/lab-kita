//TODO: Login logic

exports.login = (req,res) => {
    const { email, password} = req.body;

    //Temporary
    if (email === "admin@gmail.com" && password === "admin") {
        res.status(200).json({ message: "Login successful!" })
    }else
        res.status(401).json({ message: "Invalid credentials." })
};

exports.forgot_password = (req,res) => {
    res.send("Forgot password");
};