import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';
import DashboardLayout from './components/DashboardLayout';
import LandingPage from './pages/LandingPage';
import AuthPage from './pages/AuthPage';

/**
 * App – root component.
 *
 * Routes:
 *   /         → LandingPage (public)
 *   /login    → AuthPage (public)
 *   /app/*    → DashboardLayout (protected)
 */
export default function App() {
    return (
        <ErrorBoundary>
            <AuthProvider>
                <Routes>
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/login" element={<AuthPage />} />
                    <Route
                        path="/app/*"
                        element={
                            <ProtectedRoute>
                                <DashboardLayout />
                            </ProtectedRoute>
                        }
                    />
                </Routes>
            </AuthProvider>
        </ErrorBoundary>
    );
}
