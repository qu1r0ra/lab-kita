const express = require("express")
const app = express()
const hbs = require("handlebars")
const path = require('path')
const authRoutes = require('./routes/authRoutes')
const connectDB = require('./config/connect')


const PORT = process.env.PORT || 3000

//Connect to db
// connectDB();

// Templates and Static Files
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'templates'));
app.use(express.static(path.join(__dirname, 'public')));

app.get("/", (req, res) => {
    res.render("login")
})


//Middleware
app.use(express.json()) //used to parse data into a JSON


//Routes
app.use('/',authRoutes)

app.get("/forgot", (req, res) => {
    res.render("forgot")
})

app.get("/drafts", (req, res) => {
    res.render("drafts")
})

app.get("/view", (req, res) => {
    res.render("/views")
})

app.get("/users", (req, res) => {
    res.render("users")
})


app.get("/post", (req, res) => {
  res.render("post");
});

app.get("/view", (req, res) => {
  res.render("view");
});


app.listen(PORT, () => {
    console.log(`Listening on port ${PORT}`)
})

