import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

/**
 * useAuth hook
 *
 * Custom hook to consume the AuthContext.
 * Ensures the component is wrapped in an AuthProvider.
 *
 * Responsibilities:
 * - Return the current authentication state and functions
 */
const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export default useAuth;
