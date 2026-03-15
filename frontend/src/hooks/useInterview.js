import { useState, useCallback } from 'react';
import {
    startInterview as apiStartInterview,
    getNextQuestion as apiGetNextQuestion,
    submitAnswer as apiSubmitAnswer,
    getSummary as apiGetSummary,
    getResult as apiGetResult,
} from '../api/api';

/**
 * useInterview hook
 *
 * Custom hook managing the state and API interactions for an interview session.
 *
 * Responsibilities:
 * - Handle starting and resetting interview sessions
 * - Fetching questions and submitting answers
 * - Fetching performance summary and results
 * - Managing loading and error states during interview
 */
const useInterview = () => {
    // Current interview session ID
    const [sessionId, setSessionId] = useState(null);
    // The current question object fetched from the backend
    const [currentQuestion, setCurrentQuestion] = useState(null);
    // Loading state for API calls
    const [loading, setLoading] = useState(false);
    // History of submitted answers
    const [answers, setAnswers] = useState([]);
    // Final interview summary including AI evaluation
    const [summary, setSummary] = useState(null);
    // Basic final result (score and percentage)
    const [result, setResult] = useState(null);
    // Error messages from API calls
    const [error, setError] = useState(null);
    // Flag indicating if the interview session is finished
    const [isComplete, setIsComplete] = useState(false);
    // Current question sequence number
    const [questionNumber, setQuestionNumber] = useState(0);

    const start = async (payload) => {
        setError(null);
        setLoading(true);
        setSummary(null);
        setAnswers([]);
        setIsComplete(false);
        setQuestionNumber(0);
        try {
            // Initiate a new interview session and get the sessionId
            const res = await apiStartInterview(payload);
            const newSessionId = res.session_id;
            setSessionId(newSessionId);
            return newSessionId;
        } catch (err) {
            const message = err?.detail || err?.message || 'Failed to start interview';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const fetchResult = useCallback(async (sid) => {
        if (!sid) return;
        try {
            const data = await apiGetResult(sid);
            setResult(data);
            return data;
        } catch (err) {
            // Non-critical — result is supplementary to summary
            console.warn('Failed to fetch result:', err);
        }
    }, []);

    const fetchSummary = useCallback(async (sid) => {
        if (!sid) return;

        setError(null);
        setLoading(true);
        try {
            // Await summary first so backend finishes grading answers
            const summaryData = await apiGetSummary(sid);
            // Then fetch the result
            await fetchResult(sid);
            
            setSummary(summaryData);
            setIsComplete(true);
            return data;
        } catch (err) {
            const message = err?.detail || err?.message || 'Failed to get summary';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [fetchResult]);

    const fetchNextQuestion = useCallback(async (sid) => {
        if (!sid) return null;

        setError(null);
        setLoading(true);
        try {
            // Fetch the next interview question from backend
            const data = await apiGetNextQuestion(sid);

            // If backend signals no more questions
            if (!data || data.status === 'completed') {
                setIsComplete(true);
                setCurrentQuestion(null);
                // Auto-fetch summary
                await fetchSummary(sid);
                return null;
            }

            setCurrentQuestion(data);
            setQuestionNumber((prev) => prev + 1);
            return data;
        } catch (err) {
            // Backend returns 404 when session not found
            if (err?.status === 404 || err?.detail?.includes?.('no more')) {
                setIsComplete(true);
                setCurrentQuestion(null);
                await fetchSummary(sid);
                return null;
            }
            const message = err?.detail || err?.message || 'Failed to get next question';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [fetchSummary]);

    const answer = useCallback(async (interview_question_id, user_answer, sid) => {
        const id = sid || sessionId;
        if (!id) return;

        setError(null);
        setLoading(true);
        try {
            // Submit the user's answer to the backend
            const data = await apiSubmitAnswer(id, interview_question_id, user_answer);
            setAnswers((prev) => [...prev, { interview_question_id, user_answer, response: data }]);
            return data;
        } catch (err) {
            const message = err?.detail || err?.message || 'Failed to submit answer';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [sessionId]);

    const reset = useCallback(() => {
        setSessionId(null);
        setCurrentQuestion(null);
        setLoading(false);
        setAnswers([]);
        setSummary(null);
        setResult(null);
        setError(null);
        setIsComplete(false);
        setQuestionNumber(0);
    }, []);

    return {
        sessionId,
        currentQuestion,
        loading,
        answers,
        summary,
        result,
        error,
        isComplete,
        questionNumber,
        start,
        fetchNextQuestion,
        answer,
        fetchSummary,
        fetchResult,
        reset,
    };
};

export default useInterview;
