/**
 * Composer Routes for Uniguru-LM
 * API routes for text composition functionality
 */

import express from 'express';
import { composeText, getComposerStatus, testComposer } from '../controller/composerController.js';
import auth from '../middleware/auth.js';

const router = express.Router();

/**
 * @route   POST /api/composer/compose
 * @desc    Compose grounded text from extractive answer and chunks
 * @access  Private
 * @body    {
 *            trace_id: string,
 *            extractive_answer: string,
 *            top_chunks: Array<{text: string, source: string, score: number}>,
 *            lang: string (optional, default: 'EN')
 *          }
 */
router.post('/compose', auth, composeText);

/**
 * @route   GET /api/composer/status
 * @desc    Get composer system status and capabilities
 * @access  Private
 */
router.get('/status', auth, getComposerStatus);

/**
 * @route   GET /api/composer/test
 * @desc    Test composer with sample data
 * @access  Private
 * @query   lang: string (optional, default: 'EN')
 */
router.get('/test', auth, testComposer);

export default router;