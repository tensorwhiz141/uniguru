import express from 'express';
import {
  register,
  login,
  googleAuth,
  getMe,
  logout,
  updateDetails,
  updatePassword
} from '../controller/authController.js';
import { protect } from '../middleware/auth.js';
import {
  validateUserRegistration,
  validateUserLogin
} from '../middleware/validation.js';

const router = express.Router();

// Public routes
router.post('/register', validateUserRegistration, register);
router.post('/login', validateUserLogin, login);
router.post('/google', googleAuth);
router.post('/google/token', googleAuth); // Alternative endpoint for frontend compatibility

// Protected routes
router.get('/me', protect, getMe);
router.get('/logout', protect, logout);
router.put('/updatedetails', protect, updateDetails);
router.put('/updatepassword', protect, updatePassword);

export default router;
