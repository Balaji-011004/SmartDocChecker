import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * ProtectedRoute – guards routes that require authentication.
 *
 * Props:
 *   children  – the protected content to render
 *
 * Behaviour:
 *   • While auth is loading → shows a spinner
 *   • No user → redirects to /login (preserving the intended destination)
 *   • User exists → renders children
 */
export default function ProtectedRoute({ children }) {
    const { user, loading } = useAuth();
    const location = useLocation();

    if (loading) {
        return (
            <div className="auth-loading">
                <div className="spinner"></div>
                <p>Loading...</p>
            </div>
        );
    }

    if (!user) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return children;
}
