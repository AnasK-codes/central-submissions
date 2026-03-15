import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "../hooks/useAuth";
import useInterview from "../hooks/useInterview";

/**
 * InterviewConfig
 *
 * Page component for configuring the parameters of a new interview session.
 *
 * Responsibilities:
 * - Allow user to select subject, bloom mode, difficulty, and question count
 * - Provide a summary of selected setup
 * - Initialize a new interview session via API
 * - Redirect to InterviewScreen upon successful setup
 */
const InterviewConfig = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { start, loading, error } = useInterview();

  // The selected category or topic for the interview (e.g., 'React', 'Python')
  const [subject, setSubject] = useState("");
  // Determines if questions target a 'single' or 'mixed' cognitive level
  const [bloomMode, setBloomMode] = useState("single");
  // The specific Bloom's taxonomy level to target if mode is 'single'
  const [bloomLevel, setBloomLevel] = useState("L-1 - Remember");
  // The difficulty tier of the questions (Easy/Medium/Hard)
  const [difficulty, setDifficulty] = useState("Medium");
  // Total number of questions requested for the session
  const [questionCount, setQuestionCount] = useState(5);
  // Local error state for configuration specific validation/API errors
  const [configError, setConfigError] = useState(null);

  const isFormValid = subject !== "";

  // Map UI values to API payload values
  const bloomLevelMap = {
    "L-1 - Remember": "L1",
    "L-2 - Understand": "L2",
    "L-3 - Apply": "L3",
  };

  const handleStartInterview = async () => {
    setConfigError(null);
    try {
      const payload = {
        subject: subject,
        mode: bloomMode === "single" ? "single_bloom" : "mixed_bloom",
        bloom_level: bloomLevelMap[bloomLevel] || "L1",
        difficulty: difficulty.toLowerCase(),
        num_questions: questionCount,
        language: "en",
        bloom_strategy: "fixed",
      };

      // Start new interview session by calling API
      // Returns the unique session ID required to fetch questions
      const sessionId = await start(payload);
      navigate("/interview", {
        state: { sessionId, totalQuestions: questionCount },
      });
    } catch (err) {
      const message =
        err?.detail || err?.message || "Failed to start interview";
      setConfigError(
        typeof message === "string" ? message : "Failed to start interview",
      );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#dbeef9] via-[#e8f4fc] to-[#f0f8ff] flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-[560px] bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/80 p-8 sm:p-10">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-block p-3 bg-gradient-to-br from-[#0056b3] to-[#003d82] rounded-2xl mb-4">
            <svg
              className="w-8 h-8 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-[#0056b3] mb-2">
            Interview Configuration
          </h1>
          <p className="text-gray-500 text-sm mt-4">
            Customize your AI interview experience
          </p>
        </div>

        {/* Error Message */}
        {(configError || error) && (
          <div className="mb-6 p-3 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm font-medium text-center animate-pulse">
            {configError || error}
          </div>
        )}

        <div className="space-y-7">
          {/* Subject */}
          <div className="group">
            <label className="block text-sm font-semibold text-gray-700 mb-2.5 text-left flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[#0056b3]"></span>
              Subject
              <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <select
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full rounded-2xl border-2 border-gray-200 bg-white px-5 py-4
                                text-base font-medium text-gray-700 appearance-none cursor-pointer
                                focus:outline-none focus:border-[#0056b3] focus:ring-4 focus:ring-blue-100
                                transition-all duration-200 hover:border-gray-300 hover:shadow-md"
                style={{
                  backgroundImage: "none",
                }}
              >
                <option value="" disabled>
                  Choose your subject
                </option>
                <option value="React">⚛️ React</option>
                <option value="JavaScript">🟨 JavaScript</option>
                <option value="Full-Frontend">🎨 Full Frontend</option>
                <option value="Python">🐍 Python</option>
                <option value="Java">☕ Java</option>
                <option value="Data Structures">💚 Data Structuress</option>
                <option value="Full-Backend"> Backend</option>
              </select>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
                <svg
                  className="w-5 h-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2.5}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </div>
            </div>
          </div>

          {/* Bloom Mode */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2.5 text-left flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[#0056b3]"></span>
              Bloom Mode
              <span className="text-red-500">*</span>
            </label>
            <div className="flex bg-gradient-to-r from-[#dbeef9] to-[#e8f4fc] rounded-2xl p-1.5 shadow-inner">
              {["single", "mix"].map((mode) => (
                <button
                  key={mode}
                  onClick={() => setBloomMode(mode)}
                  className={`flex-1 py-3 text-sm rounded-xl transition-all duration-300 font-semibold
                                    ${
                                      bloomMode === mode
                                        ? "bg-white text-[#0056b3] shadow-lg scale-[1.02]"
                                        : "text-blue-600 hover:text-[#0056b3]"
                                    }`}
                >
                  {mode === "single" ? "Single Level" : "Mixed Levels"}
                </button>
              ))}
            </div>
          </div>

          {/* Bloom Level */}
          {bloomMode === "single" && (
            <div className="animate-fadeIn">
              <label className="block text-sm font-semibold text-gray-700 mb-2.5 text-left flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[#0056b3]"></span>
                Bloom Level
                <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <select
                  value={bloomLevel}
                  onChange={(e) => setBloomLevel(e.target.value)}
                  className="w-full rounded-2xl border-2 border-gray-200 bg-white px-5 py-4
                                    text-base font-medium text-gray-700 appearance-none cursor-pointer
                                    focus:outline-none focus:border-[#0056b3] focus:ring-4 focus:ring-blue-100
                                    transition-all duration-200 hover:border-gray-300 hover:shadow-md"
                >
                  <option>L-1 - Remember</option>
                  <option>L-2 - Understand</option>
                  <option>L-3 - Apply</option>
                </select>
                <svg
                  className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2.5}
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </div>
            </div>
          )}

          {/* Difficulty */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2.5 text-left flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[#0056b3]"></span>
              Difficulty
              <span className="text-red-500">*</span>
            </label>
            <div className="flex gap-3">
              {["Easy", "Medium", "Hard"].map((level) => (
                <button
                  key={level}
                  onClick={() => setDifficulty(level)}
                  className={`flex-1 py-3 rounded-xl text-sm font-semibold border-2 transition-all duration-300
                                    ${
                                      difficulty === level
                                        ? "bg-gradient-to-br from-blue-50 to-blue-100 border-[#0056b3] text-[#0056b3] shadow-md scale-[1.02]"
                                        : "bg-white border-gray-200 text-gray-600 hover:border-gray-300 hover:bg-gray-50"
                                    }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          {/* Questions */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <label className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[#0056b3]"></span>
                Number of Questions
                <span className="text-red-500">*</span>
              </label>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-[#0056b3]">
                  {questionCount}
                </span>
                <span className="text-xs text-gray-500 font-medium">
                  questions
                </span>
              </div>
            </div>

            <div className="relative pt-1">
              <input
                type="range"
                min="1"
                max="20"
                value={questionCount}
                onChange={(e) => setQuestionCount(Number(e.target.value))}
                style={{
                  background: `linear-gradient(to right,
                                    #0056b3 0%,
                                    #0056b3 ${((questionCount - 1) * 100) / 19}%,
                                    #e0e7ff ${((questionCount - 1) * 100) / 19}%,
                                    #e0e7ff 100%)`,
                }}
                className="w-full h-2.5 rounded-full appearance-none cursor-pointer
                                [&::-webkit-slider-thumb]:appearance-none
                                [&::-webkit-slider-thumb]:h-5
                                [&::-webkit-slider-thumb]:w-5
                                [&::-webkit-slider-thumb]:rounded-full
                                [&::-webkit-slider-thumb]:bg-white
                                [&::-webkit-slider-thumb]:border-4
                                [&::-webkit-slider-thumb]:border-[#0056b3]
                                [&::-webkit-slider-thumb]:shadow-lg
                                [&::-webkit-slider-thumb]:cursor-pointer
                                [&::-webkit-slider-thumb]:transition-transform
                                [&::-webkit-slider-thumb]:hover:scale-110
                                [&::-moz-range-thumb]:h-5
                                [&::-moz-range-thumb]:w-5
                                [&::-moz-range-thumb]:rounded-full
                                [&::-moz-range-thumb]:bg-white
                                [&::-moz-range-thumb]:border-4
                                [&::-moz-range-thumb]:border-[#0056b3]
                                [&::-moz-range-thumb]:shadow-lg
                                [&::-moz-range-thumb]:cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-400 font-medium mt-2 px-1">
                <span>1</span>
                <span>20</span>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="bg-gradient-to-br from-[#dbeef9] to-[#e8f4fc] rounded-2xl p-6 border border-blue-100 shadow-inner">
            <div className="flex items-center gap-2 mb-4">
              <svg
                className="w-5 h-5 text-[#0056b3]"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h3 className="text-[#0056b3] font-bold text-base">
                Interview Summary
              </h3>
            </div>
            <div className="space-y-2.5 text-sm">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-700 min-w-[90px]">
                  Subject:
                </span>
                <span className="text-gray-600">{subject || "—"}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-700 min-w-[90px]">
                  Mode:
                </span>
                <span className="text-gray-600">
                  {bloomMode === "single" ? bloomLevel : "Mixed Bloom Levels"}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-700 min-w-[90px]">
                  Difficulty:
                </span>
                <span className="text-gray-600">{difficulty}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-700 min-w-[90px]">
                  Questions:
                </span>
                <span className="text-gray-600">{questionCount}</span>
              </div>
            </div>
          </div>

          {/* CTA */}
          <button
            onClick={handleStartInterview}
            disabled={!isFormValid || loading}
            className={`w-full py-4 rounded-2xl font-bold text-base shadow-xl transition-all duration-300 flex items-center justify-center gap-2
                        ${
                          isFormValid && !loading
                            ? "bg-gradient-to-r from-[#003380] to-[#0056b3] hover:from-[#002260] hover:to-[#003d82] text-white hover:shadow-2xl hover:scale-[1.02] active:scale-[0.98]"
                            : "bg-gray-300 text-gray-500 cursor-not-allowed"
                        }`}
          >
            {loading ? (
              <>
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Starting Interview...
              </>
            ) : isFormValid ? (
              "Start Interview →"
            ) : (
              "Please Select a Subject"
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default InterviewConfig;
