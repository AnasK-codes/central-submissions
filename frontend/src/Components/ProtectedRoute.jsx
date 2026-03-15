import { Navigate } from 'react-router-dom';
import useAuth from '../hooks/useAuth';

/**
 * ProtectedRoute
 *
 * Wrapper component to protect routes that require authentication.
 *
 * Responsibilities:
 * - Check if the user is authenticated via Context
 * - Render children if authenticated
 * - Redirect to login page if not authenticated
 * - Show a loading spinner while checking auth state
 */
const ProtectedRoute = ({ children }) => {
    const { token, loading } = useAuth();

    // Show nothing while checking auth state on initial load
    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#dbeef9] via-[#e8f4fc] to-[#f0f8ff]">
                <div className="flex flex-col items-center gap-4">
                    <svg className="animate-spin h-10 w-10 text-[#0056b3]" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    <p className="text-gray-500 font-medium">Loading...</p>
                </div>
            </div>
        );
    }

    if (!token) {
        return <Navigate to="/" replace />;
    }

    return children;
};

export default ProtectedRoute;
