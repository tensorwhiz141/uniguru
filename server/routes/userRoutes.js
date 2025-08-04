import express from 'express';
import {
  signup,
  login,
  getAuthStatus,
  logout,
  updateUser,
  updatePassword,
  deleteUser
} from '../controller/userController.js';
import { protect } from '../middleware/auth.js';
import {
  validateUserRegistration,
  validateUserLogin
} from '../middleware/validation.js';

const router = express.Router();

// Public routes
router.post('/signup', validateUserRegistration, signup);
router.post('/login', validateUserLogin, login);

// Protected routes
router.get('/auth-status', protect, getAuthStatus);
router.get('/logout', protect, logout);
router.put('/update', protect, updateUser);
router.put('/password', protect, updatePassword);
router.delete('/delete', protect, deleteUser);

export default router;
