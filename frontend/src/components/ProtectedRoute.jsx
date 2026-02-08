import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = () => {
    const { user, loading } = useAuth();
    const token = localStorage.getItem('token');

    if (loading) {
        return null; // Or a loading spinner handled in AuthProvider
    }

    // If no token or no user (and not loading), redirect to login
    if (!token) {
        return <Navigate to="/login" replace />;
    }

    return <Outlet />;
};

export default ProtectedRoute;
