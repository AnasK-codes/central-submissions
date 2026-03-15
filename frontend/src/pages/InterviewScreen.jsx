import React, { useState, useEffect, useCallback } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import logo from "../assets/logo.png";
import useInterview from "../hooks/useInterview";
import useAuth from "../hooks/useAuth";
import QuestionCard from "../components/QuestionCard";

/**
 * InterviewScreen
 *
 * Main interview interface where the user answers generated questions.
 * Handles the session flow, timer, and end-of-interview summary view.
 *
 * Responsibilities:
 * - Fetch and display the next question from the backend
 * - Capture user answer and submit to the backend
 * - Track remaining time for the interview session
 * - Show a final summary screen with performance breakdown upon completion
 */
const InterviewScreen = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { user } = useAuth();
    const {
        sessionId,
        currentQuestion,
        loading,
        error,
        isComplete,
        questionNumber,
        summary,
        result,
        fetchNextQuestion,
        answer,
        fetchSummary,
        reset,
    } = useInterview();

    // Remaining time in seconds for the interview (default 10 minutes)
    const [timeLeft, setTimeLeft] = useState(600);
    // Total questions expected in this session (passed from Config)
    const [totalQuestions, setTotalQuestions] = useState(
        location.state?.totalQuestions || 5
    );
    // The unique ID matching the active session in the database
    const [interviewSessionId, setInterviewSessionId] = useState(null);
    // Flag to prevent double-fetching the first question
    const [interviewStarted, setInterviewStarted] = useState(false);

    // Get sessionId from route state
    useEffect(() => {
        const sid = location.state?.sessionId || sessionId;
        if (sid) {
            setInterviewSessionId(sid);
        } else {
            navigate('/config');
        }
    }, [location.state, sessionId, navigate]);

    // Fetch first question when session is ready
    useEffect(() => {
        if (interviewSessionId && !interviewStarted) {
            setInterviewStarted(true);
            fetchNextQuestion(interviewSessionId);
        }
    }, [interviewSessionId, interviewStarted, fetchNextQuestion]);

    // Timer logic — stops when interview is complete or time runs out
    useEffect(() => {
        if (isComplete || timeLeft <= 0) return;

        const timer = setInterval(() => {
            setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
        }, 1000);
        return () => clearInterval(timer);
    }, [isComplete, timeLeft]);

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins < 10 ? "0" : ""}${mins}:${secs < 10 ? "0" : ""}${secs}`;
    };

    // ─── SESSION HELPERS ──────────────────────────────────────────────

    /** Fetch the next interview question from backend for this session */
    const handleNextQuestion = useCallback(async () => {
        await fetchNextQuestion(interviewSessionId);
    }, [fetchNextQuestion, interviewSessionId]);

    /** Submit the user's typed answer to the backend */
    const handleSubmitAnswer = useCallback(async (interview_question_id, user_answer) => {
        return await answer(interview_question_id, user_answer, interviewSessionId);
    }, [answer, interviewSessionId]);

    /** Reset interview state and navigate back to configuration page */
    const handleExit = useCallback(() => {
        reset();
        navigate('/config');
    }, [reset, navigate]);

    // Progress as a percentage (0–100) for the progress bar
    const progressPercentage = totalQuestions > 0
        ? Math.min((questionNumber / totalQuestions) * 100, 100)
        : 0;

    // ─── RESULTS VIEW ───────────────────────────────────────────────
    if (isComplete) {
        if (!summary) {
            return (
                <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-br from-[#d2f0fa] via-[#dbeef9] to-[#e8f4fc]">
                    <div className="flex flex-col items-center gap-6 bg-white/90 backdrop-blur-sm p-12 rounded-3xl shadow-2xl border border-white/80">
                        <svg className="animate-spin h-16 w-16 text-[#0056b3]" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                        <div className="text-center">
                            <h2 className="text-2xl font-bold text-[#0056b3] mb-2">Evaluating Your Interview...</h2>
                            <p className="text-gray-500 font-medium max-w-sm">
                                Please wait while our AI reviews your answers. This may take up to a minute.
                            </p>
                        </div>
                    </div>
                </div>
            );
        }
        const getScoreColor = (score) => {
            if (score >= 90) return { ring: 'border-green-400', text: 'text-green-600', bg: 'bg-green-50' };
            if (score >= 70) return { ring: 'border-blue-400', text: 'text-blue-600', bg: 'bg-blue-50' };
            if (score >= 40) return { ring: 'border-yellow-400', text: 'text-yellow-600', bg: 'bg-yellow-50' };
            return { ring: 'border-red-400', text: 'text-red-600', bg: 'bg-red-50' };
        };

        const getLevelBadge = (level) => {
            const map = {
                Excellent: 'bg-gradient-to-r from-green-400 to-green-600 text-white',
                Strong: 'bg-gradient-to-r from-blue-400 to-blue-600 text-white',
                Average: 'bg-gradient-to-r from-yellow-400 to-yellow-500 text-white',
                Weak: 'bg-gradient-to-r from-red-400 to-red-600 text-white',
            };
            return map[level] || 'bg-gray-200 text-gray-700';
        };

        const colors = getScoreColor(summary.average_score);

        return (
            <div className="min-h-screen w-full bg-gradient-to-br from-[#d2f0fa] via-[#dbeef9] to-[#e8f4fc] overflow-x-hidden">
                {/* Header */}
                <header className="relative bg-white/40 backdrop-blur-sm px-6 py-4 flex justify-between items-center border-b-2 border-blue-100 shadow-sm">
                    <div className="flex items-center">
                        <img src={logo} alt="Logo" className="h-16 object-contain" />
                    </div>
                    <h2 className="text-xl font-bold text-[#0056b3]">Interview Results</h2>
                </header>

                <main className="max-w-3xl mx-auto w-full p-6 sm:p-8">
                    {/* Score Card */}
                    <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/80 p-8 mb-8 text-center">
                        <div className={`inline-flex items-center justify-center w-36 h-36 rounded-full border-8 ${colors.ring} ${colors.bg} mb-6`}>
                            <div>
                                <span className={`text-4xl font-extrabold ${colors.text}`}>
                                    {summary.average_score}
                                </span>
                                <span className={`block text-sm font-medium ${colors.text} opacity-70`}>/100</span>
                            </div>
                        </div>

                        <div className="mb-4">
                            <span className={`inline-block px-6 py-2 rounded-full text-base font-bold shadow-lg ${getLevelBadge(summary.performance_level)}`}>
                                {summary.performance_level}
                            </span>
                        </div>

                        <p className="text-gray-500 text-sm">
                            You answered <strong className="text-gray-700">{summary.total_answered}</strong> question{summary.total_answered !== 1 ? 's' : ''}
                        </p>
                    </div>

                    {/* Simple Score Card */}
                    {result && (
                        <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-xl border border-white/80 p-6 mb-8">
                            <h3 className="text-lg font-bold text-[#0056b3] mb-4 flex items-center gap-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                </svg>
                                Quick Result
                            </h3>
                            <div className="grid grid-cols-3 gap-4 text-center">
                                <div className="p-3 rounded-xl bg-blue-50 border border-blue-200">
                                    <p className="text-2xl font-extrabold text-[#0056b3]">{result.score}/{result.total}</p>
                                    <p className="text-xs font-medium text-gray-500 mt-1">Correct</p>
                                </div>
                                <div className="p-3 rounded-xl bg-blue-50 border border-blue-200">
                                    <p className="text-2xl font-extrabold text-[#0056b3]">{result.percentage}%</p>
                                    <p className="text-xs font-medium text-gray-500 mt-1">Percentage</p>
                                </div>
                                <div className="p-3 rounded-xl bg-blue-50 border border-blue-200">
                                    <p className="text-2xl font-extrabold text-[#0056b3]">{result.total}</p>
                                    <p className="text-xs font-medium text-gray-500 mt-1">Total</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Breakdown */}
                    {summary.breakdown && summary.breakdown.length > 0 && (
                        <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-xl border border-white/80 p-6 mb-8">
                            <h3 className="text-lg font-bold text-[#0056b3] mb-4 flex items-center gap-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                </svg>
                                Question Breakdown
                            </h3>
                            <div className="space-y-3">
                                {summary.breakdown.map((item, idx) => {
                                    const qColors = getScoreColor(item.score);
                                    return (
                                        <div key={item.question_id || idx} className={`p-4 rounded-2xl border-2 ${qColors.ring} ${qColors.bg}`}>
                                            <div className="flex items-center justify-between mb-2">
                                                <span className="text-sm font-bold text-gray-700">Question {idx + 1}</span>
                                                <span className={`text-lg font-extrabold ${qColors.text}`}>
                                                    {item.score != null ? `${item.score}/100` : 'N/A'}
                                                </span>
                                            </div>
                                            {item.feedback && (
                                                <p className="text-sm text-gray-600">{item.feedback}</p>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* Action Button */}
                    <div className="text-center">
                        <button
                            onClick={handleExit}
                            className="px-10 py-4 rounded-2xl font-bold text-base shadow-xl transition-all duration-300
                                bg-gradient-to-r from-[#003380] to-[#0056b3] hover:from-[#002260] hover:to-[#003d82]
                                text-white hover:shadow-2xl hover:scale-[1.02] active:scale-[0.98]"
                        >
                            Start New Interview →
                        </button>
                    </div>
                </main>
            </div>
        );
    }

    // ─── INTERVIEW QUESTION VIEW ────────────────────────────────────
    return (
        <div className="min-h-screen w-full bg-gradient-to-br from-[#d2f0fa] via-[#dbeef9] to-[#e8f4fc] overflow-x-hidden">

            {/* Header */}
            <header className="relative bg-white/40 backdrop-blur-sm px-6 py-4 flex justify-between items-center border-b-2 border-blue-100 shadow-sm">
                <div className="flex items-center">
                    <img
                        src={logo}
                        alt="Logo"
                        className="h-16 object-contain"
                    />
                </div>

                <div className="flex items-center space-x-6">
                    {/* Timer */}
                    <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-xl shadow-md border border-blue-100">
                        <svg className="w-5 h-5 text-[#0056b3]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className={`text-xl font-bold font-mono ${timeLeft < 60 ? 'text-red-500' : 'text-gray-700'}`}>
                            {formatTime(timeLeft)}
                        </span>
                    </div>

                    {/* Exit Button */}
                    <button
                        onClick={handleExit}
                        className="flex items-center gap-2 px-4 py-2 text-red-500 font-semibold hover:bg-red-50 rounded-xl transition-all duration-300 border-2 border-transparent hover:border-red-200"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                        Exit Interview
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 max-w-6xl mx-auto w-full p-6 sm:p-8 flex flex-col min-h-[calc(100vh-100px)]">

                {/* Progress Bar */}
                <div className="mb-6">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-semibold text-gray-600">
                            Question {questionNumber} of {totalQuestions}
                        </span>
                        <span className="text-sm font-semibold text-[#0056b3]">
                            {Math.round(progressPercentage)}% Complete
                        </span>
                    </div>
                    <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden shadow-inner">
                        <div
                            className="h-full bg-gradient-to-r from-[#003380] to-[#0056b3] transition-all duration-500 ease-out rounded-full"
                            style={{ width: `${progressPercentage}%` }}
                        ></div>
                    </div>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm font-medium text-center">
                        {typeof error === 'string' ? error : 'An error occurred'}
                    </div>
                )}

                {/* Question Tags */}
                {currentQuestion && (
                    <div className="mb-auto">
                        <div className="flex flex-wrap gap-3 mb-4">
                            <span className="inline-flex items-center gap-1.5 bg-gradient-to-r from-blue-100 to-blue-200 text-blue-700 text-sm font-bold px-4 py-2 rounded-xl border-2 border-blue-300 shadow-sm">
                                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                                </svg>
                                Q{questionNumber}
                            </span>
                            {currentQuestion.bloom_level && (
                                <span className="inline-flex items-center gap-1.5 bg-gradient-to-r from-green-100 to-green-200 text-green-700 text-sm font-bold px-4 py-2 rounded-xl border-2 border-green-300 shadow-sm">
                                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                                        <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
                                    </svg>
                                    {currentQuestion.bloom_level}
                                </span>
                            )}
                            {currentQuestion.difficulty && (
                                <span className="inline-flex items-center gap-1.5 bg-gradient-to-r from-purple-100 to-purple-200 text-purple-700 text-sm font-bold px-4 py-2 rounded-xl border-2 border-purple-300 shadow-sm">
                                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                                    </svg>
                                    {currentQuestion.difficulty}
                                </span>
                            )}
                        </div>

                        {/* Question Card */}
                        <QuestionCard
                            question={currentQuestion}
                            onNext={handleNextQuestion}
                            onSubmitAnswer={handleSubmitAnswer}
                            loading={loading}
                        />
                    </div>
                )}

                {/* Loading state when no question yet */}
                {!currentQuestion && !isComplete && (
                    <div className="flex-1 flex items-center justify-center">
                        <div className="flex flex-col items-center gap-4">
                            <svg className="animate-spin h-10 w-10 text-[#0056b3]" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                            <p className="text-gray-500 font-medium">Loading question...</p>
                        </div>
                    </div>
                )}

                {/* Footer Section */}
                <div className="mt-8 bg-white/60 backdrop-blur-sm p-5 rounded-2xl border border-blue-100 shadow-sm">
                    <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                        <p className="text-sm text-gray-600 flex items-center gap-2">
                            <svg className="w-5 h-5 text-blue-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Take your time to think through your answer. You can always come back to edit it.
                        </p>

                        <div className="flex items-center gap-4">
                            {/* Progress Dots */}
                            <div className="flex gap-2">
                                {[...Array(totalQuestions)].map((_, index) => (
                                    <div
                                        key={index}
                                        className={`w-3 h-3 rounded-full transition-all duration-300 ${index < questionNumber
                                            ? 'bg-gradient-to-r from-[#003380] to-[#0056b3] scale-110 shadow-md'
                                            : index === questionNumber - 1
                                                ? 'bg-[#0056b3] scale-125 shadow-lg ring-2 ring-blue-300'
                                                : 'bg-gray-300'
                                            }`}
                                    ></div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default InterviewScreen;