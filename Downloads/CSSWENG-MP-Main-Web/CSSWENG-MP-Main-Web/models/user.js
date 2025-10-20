const mongoose = require('mongoose');
const bcrypt = require('bcrypt');

const userSchema = new mongoose.Schema({
    email: {type: String, required: true, unique: true},
    username: {type: String, required: true, unique: true},
    password: {type: String, required: true},
});

const SALT_WORK_FACTOR = 10;

userSchema.pre('save', async function (next) {
    if(!this.isModified('password'))
        return next();
    this.password = await bcrypt.hash(this.password,SALT_WORK_FACTOR);
    next();
    
});

userSchema.method("comparePassword", async function(candidatePassword){
    return bcrypt.compare(candidatePassword,this.password);
});
    

module.exports = mongoose.model('User', userSchema);