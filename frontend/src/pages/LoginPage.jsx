import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import logoImg from "../assets/logo.png";
import bgImg from "../assets/bg.png";
import useAuth from "../hooks/useAuth";
import { GoogleLogin } from "@react-oauth/google";

/**
 * Login
 *
 * Page component for authenticating existing users.
 *
 * Responsibilities:
 * - Collect email and password from the user
 * - Authenticate via credentials or Google OAuth
 * - Redirect to configuration page on successful login
 * - Display authentication errors
 */
export default function Login() {
  // Track which input field is currently focused for styling purposes
  const [focusedField, setFocusedField] = useState(null);
  // Track hover state for the main card container
  const [isHovering, setIsHovering] = useState(false);
  // User login credentials
  const [credentials, setCredentials] = useState({ email: "", password: "" });
  const navigate = useNavigate();
  const { login, googleAuth, loading, error } = useAuth();

  const handleChange = (e) => {
    setCredentials({ ...credentials, [e.target.id]: e.target.value });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      // Send user credentials to the backend for authentication
      // On success, stores JWT and sets user context
      await login(credentials.email, credentials.password);
      navigate("/config");
    } catch (err) {
      // Error is already set in AuthContext
    }
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 font-sans text-gray-800">
      {/* Background */}
      <div className="absolute inset-0 z-0">
        <img
          src={bgImg}
          alt="Background"
          className="h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-black/10" />
      </div>

      {/* Content */}
      <div className="relative z-10 flex min-h-screen items-center justify-center px-4 py-10">
        <div
          className={`relative w-full max-w-[400px] md:max-w-[450px] overflow-hidden rounded-3xl border bg-white/30 p-10 shadow-[0_20px_60px_rgba(0,0,0,0.25)] backdrop-blur-2xl transition-all duration-500 ${
            isHovering
              ? "border-blue-400/70 scale-[1.02] shadow-[0_30px_80px_rgba(0,51,102,0.35)]"
              : "border-white/50"
          }`}
          onMouseEnter={() => setIsHovering(true)}
          onMouseLeave={() => setIsHovering(false)}
        >
          {/* Glow Border */}
          <div className="pointer-events-none absolute inset-0 -z-10 rounded-3xl bg-gradient-to-r from-blue-500 via-[#003366] to-blue-500 opacity-20 blur-2xl" />

          {/* Header */}
          <div className="mb-8 flex flex-col items-center text-center">
            <div className="group relative mb-6">
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-400 to-[#003366] opacity-30 blur-xl transition-all duration-300 group-hover:opacity-60 group-hover:blur-2xl" />

              <div className="relative rounded-2xl bg-white/20 p-4 backdrop-blur-md transition-all duration-300">
                <img
                  src={logoImg}
                  alt="Logo"
                  className="h-auto w-48 object-contain transition-transform duration-300"
                />
              </div>
            </div>

            <p className="text-slate-600 text-lg">Login to your account</p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm font-medium text-center animate-pulse">
              {typeof error === "string"
                ? error
                : "Login failed. Please try again."}
            </div>
          )}

          {/* Form */}
          <form className="space-y-5" onSubmit={handleLogin}>
            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className={`mb-1 block text-sm font-semibold text-left transition-all duration-300 ${
                  focusedField === "email" ? "text-[#003366]" : "text-[#003366]"
                }`}
              >
                Email
              </label>

              <div className="relative">
                <input
                  id="email"
                  type="email"
                  required
                  placeholder="Enter your email"
                  value={credentials.email}
                  onChange={handleChange}
                  onFocus={() => setFocusedField("email")}
                  onBlur={() => setFocusedField(null)}
                  className={`w-full rounded-xl py-3 px-5 shadow-lg ring-2 transition-all duration-300 placeholder:text-gray-400 ${
                    focusedField === "email"
                      ? "bg-white ring-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.35)] scale-[1.02]"
                      : "bg-white/70 ring-transparent hover:bg-white hover:shadow-xl"
                  }`}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="password"
                className={`mb-1 block text-sm font-semibold text-left transition-all duration-300 ${
                  focusedField === "password"
                    ? "text-[#003366]"
                    : "text-[#003366]"
                }`}
              >
                Password
              </label>

              <div className="relative">
                <input
                  id="password"
                  type="password"
                  required
                  placeholder="Enter password"
                  value={credentials.password}
                  onChange={handleChange}
                  onFocus={() => setFocusedField("password")}
                  onBlur={() => setFocusedField(null)}
                  className={`w-full rounded-xl py-3 px-5 shadow-lg ring-2 transition-all duration-300 placeholder:text-gray-400 ${
                    focusedField === "password"
                      ? "bg-white ring-blue-500 shadow-[0_0_20px_rgba(59,130,246,0.35)] scale-[1.02]"
                      : "bg-white/70 ring-transparent hover:bg-white hover:shadow-xl"
                  }`}
                />
              </div>
            </div>

            {/* Button */}
            <button
              type="submit"
              disabled={loading}
              className={`group relative flex w-full justify-center overflow-hidden rounded-xl px-4 py-3 text-base font-bold text-white shadow-[0_15px_50px_rgba(0,51,102,0.5)] transition-all duration-300 active:scale-95 ${
                loading
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-[#003366] via-blue-700 to-[#003366] hover:shadow-[0_25px_70px_rgba(0,51,102,0.65)]"
              }`}
            >
              <span className="relative z-10 flex items-center gap-2">
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
                    Logging in...
                  </>
                ) : (
                  "Login"
                )}
              </span>

              {!loading && (
                <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/30 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="my-6 flex items-center gap-4 before:h-px before:flex-1 before:bg-slate-200 after:h-px after:flex-1 after:bg-slate-200">
            <span className="text-sm font-medium text-slate-400">or</span>
          </div>

          {/* Google Button */}
          <div className="flex w-full justify-center mt-2">
            <GoogleLogin
              onSuccess={async (credentialResponse) => {
                try {
                  const { credential } = credentialResponse;
                  await googleAuth(credential);
                  navigate("/config");
                } catch (err) {
                  // Error is handled in AuthContext
                }
              }}
              onError={() => {
                console.log("Google Login Failed");
              }}
              theme="outline"
              size="large"
              shape="rectangular"
              width="100%"
              text="continue_with"
            />
          </div>

          {/* Signup Link */}
          <p className="mt-12 text-center text-sm font-medium text-slate-800">
            Don't have an account?{" "}
            <Link
              to="/signup"
              className="font-bold text-[#003366] underline decoration-2 underline-offset-4 transition hover:text-blue-700"
            >
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
