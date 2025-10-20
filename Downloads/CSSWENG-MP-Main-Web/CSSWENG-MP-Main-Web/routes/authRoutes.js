const authController = require('../controllers/authController');
const express = require('express');
const router = express.Router();


router.post('/login',authController.login);

router.post('/forgot_password',authController.forgot_password);

module.exports = router;