/**
 * Composer Controller for Uniguru-LM
 * Handles composition requests and integrates with Python composer module
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Compose text using the Python composer module
 */
export const composeText = async (req, res) => {
    try {
        const { trace_id, extractive_answer, top_chunks, lang = 'EN' } = req.body;

        // Validate required fields
        if (!trace_id || !extractive_answer || !top_chunks) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields: trace_id, extractive_answer, top_chunks'
            });
        }

        // Validate top_chunks is an array
        if (!Array.isArray(top_chunks)) {
            return res.status(400).json({
                success: false,
                error: 'top_chunks must be an array'
            });
        }

        console.log(`Composer request - trace_id: ${trace_id}, lang: ${lang}`);

        // Prepare arguments for Python script
        const topChunksJson = JSON.stringify(top_chunks);
        const composerApiPath = path.join(__dirname, '..', 'composer', 'composer_api.py');

        // Execute Python composer
        const result = await executeComposer(
            composerApiPath,
            [trace_id, extractive_answer, topChunksJson, lang]
        );

        // Return result
        res.json({
            success: true,
            data: result
        });

    } catch (error) {
        console.error('Composer error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            trace_id: req.body?.trace_id || 'unknown'
        });
    }
};

/**
 * Get composer status and information
 */
export const getComposerStatus = async (req, res) => {
    try {
        const composerPath = path.join(__dirname, '..', 'composer');
        
        // Check if composer files exist
        const status = {
            available: true,
            components: {
                compose: checkFileExists(path.join(composerPath, 'compose.py')),
                templates: checkFileExists(path.join(composerPath, 'templates.py')),
                ngram_scorer: checkFileExists(path.join(composerPath, 'ngram_scorer.py')),
                gru: checkFileExists(path.join(composerPath, 'gru.py')),
                grounding: checkFileExists(path.join(composerPath, 'grounding.py'))
            },
            version: '1.0.0',
            languages: ['EN', 'HI'],
            features: {
                templates: true,
                ngram_smoothing: true,
                gru_fallback: true,
                grounding_verification: true
            }
        };

        res.json({
            success: true,
            status
        });

    } catch (error) {
        console.error('Composer status error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
};

/**
 * Test composer with sample data
 */
export const testComposer = async (req, res) => {
    try {
        const { lang = 'EN' } = req.query;

        // Sample test data
        const testData = {
            trace_id: `test_${Date.now()}`,
            extractive_answer: lang === 'HI' 
                ? 'ध्यान से आंतरिक शांति मिलती है।'
                : 'Meditation brings inner peace and spiritual growth.',
            top_chunks: [
                {
                    text: lang === 'HI'
                        ? 'पवित्र ग्रंथों के अनुसार, ध्यान एक शक्तिशाली अभ्यास है जो आंतरिक शांति और आध्यात्मिक विकास लाता है।'
                        : 'According to the sacred texts, meditation is a powerful practice that brings inner peace and spiritual growth.',
                    source: lang === 'HI' ? 'भगवद्गीता' : 'Bhagavad Gita',
                    score: 0.95
                },
                {
                    text: lang === 'HI'
                        ? 'प्राचीन ज्ञान सिखाता है कि नियमित अभ्यास से मानसिक स्पष्टता और शांति प्राप्त होती है।'
                        : 'Ancient wisdom teaches that regular practice leads to mental clarity and peace.',
                    source: lang === 'HI' ? 'उपनिषद' : 'Upanishads',
                    score: 0.88
                }
            ],
            lang
        };

        // Execute test
        const composerApiPath = path.join(__dirname, '..', 'composer', 'composer_api.py');
        const topChunksJson = JSON.stringify(testData.top_chunks);

        const result = await executeComposer(
            composerApiPath,
            [testData.trace_id, testData.extractive_answer, topChunksJson, testData.lang]
        );

        res.json({
            success: true,
            test_input: testData,
            result
        });

    } catch (error) {
        console.error('Composer test error:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
};

/**
 * Execute Python composer script
 */
function executeComposer(scriptPath, args) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', [scriptPath, ...args], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        pythonProcess.on('close', (code) => {
            if (code !== 0) {
                reject(new Error(`Python process exited with code ${code}. Stderr: ${stderr}`));
                return;
            }

            try {
                const result = JSON.parse(stdout);
                resolve(result);
            } catch (parseError) {
                reject(new Error(`Failed to parse Python output: ${parseError.message}. Output: ${stdout}`));
            }
        });

        pythonProcess.on('error', (error) => {
            reject(new Error(`Failed to start Python process: ${error.message}`));
        });

        // Set timeout
        setTimeout(() => {
            pythonProcess.kill();
            reject(new Error('Python process timeout'));
        }, 30000); // 30 second timeout
    });
}

/**
 * Check if file exists
 */
function checkFileExists(filePath) {
    try {
        const fs = require('fs');
        return fs.existsSync(filePath);
    } catch (error) {
        return false;
    }
}