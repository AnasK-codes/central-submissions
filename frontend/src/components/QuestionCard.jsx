import { useState } from 'react';

/**
 * QuestionCard
 *
 * Component for displaying a single interview question and collecting the user's answer.
 *
 * Responsibilities:
 * - Render the question text visually
 * - Provide a text area for the user to type their answer
 * - Submit the answer to the backend
 * - Trigger navigation to the next question upon successful submission
 */
const QuestionCard = ({ question, onNext, onSubmitAnswer, loading }) => {
    // Stores the current text input from the user
    const [userAnswer, setUserAnswer] = useState('');
    // Tracks ongoing submission to disable the input and button
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async () => {
        // Prevent submission if answer is blank or handler is missing
        if (!userAnswer.trim() || !onSubmitAnswer) return;
        setSubmitting(true);
        try {
            await onSubmitAnswer(question.interview_question_id, userAnswer);
            // After successful submission, clear the textarea and auto-advance to the next question
            setUserAnswer('');
            onNext();
        } catch (err) {
            // Error handling is delegated to the useInterview hook
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="bg-white/80 backdrop-blur-sm p-10 rounded-2xl flex flex-col shadow-lg border-2 border-blue-100 min-h-[full] hover:shadow-xl transition-shadow duration-300">
            {/* Question */}
            <div className="flex items-start gap-4 w-full mb-8">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-[#003380] to-[#0056b3] flex items-center justify-center shadow-md">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <h2 className="text-2xl sm:text-3xl font-semibold text-gray-800 leading-relaxed">
                    {question?.question_text || question?.question || 'Loading question...'}
                </h2>
            </div>

            {/* Answer Input */}
            <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-2 text-left">
                    Your Answer
                </label>
                <textarea
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    disabled={submitting}
                    placeholder="Type your answer here..."
                    rows={4}
                    className={`w-full rounded-xl border-2 px-5 py-4 text-base font-medium text-gray-700
                        focus:outline-none focus:border-[#0056b3] focus:ring-4 focus:ring-blue-100
                        transition-all duration-200 resize-none
                        ${submitting
                            ? 'bg-gray-50 border-gray-200 cursor-not-allowed'
                            : 'bg-white border-gray-200 hover:border-gray-300 hover:shadow-md'
                        }`}
                />
            </div>



            {/* Action Buttons */}
            <div className="flex justify-end mt-auto gap-3">
                <button
                    onClick={handleSubmit}
                    disabled={loading || submitting || !userAnswer.trim()}
                    className={`px-8 py-3 rounded-xl font-bold text-base transition-all duration-300 flex items-center gap-2
                        ${(loading || submitting || !userAnswer.trim())
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white shadow-lg hover:shadow-xl hover:scale-[1.02] active:scale-[0.98]'
                        }`}
                >
                    {submitting ? (
                        <>
                            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                            Submitting...
                        </>
                    ) : (
                        <>
                            Submit Answer
                            <span>→</span>
                        </>
                    )}
                </button>
            </div>
        </div>
    );
};

export default QuestionCard;
