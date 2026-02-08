import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import MainLayout from './components/MainLayout';
import ProtectedRoute from './components/ProtectedRoute';
import ProductList from './pages/ProductList';
import QuoteList from './pages/QuoteList';
import QuoteCreate from './pages/QuoteCreate';
import ClientList from './pages/ClientList';
import './index.css';

function App() {
    return (
        <ConfigProvider
            theme={{
                token: {
                    colorPrimary: '#1890ff',
                },
            }}
        >
            <AuthProvider>
                <Router>
                    <Routes>
                        <Route path="/login" element={<Login />} />

                        <Route element={<ProtectedRoute />}>
                            <Route element={<MainLayout />}>
                                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                                <Route path="/dashboard" element={<Dashboard />} />
                                <Route path="/products" element={<ProductList />} />
                                <Route path="/quotes" element={<QuoteList />} />
                                <Route path="/quotes/new" element={<QuoteCreate />} />
                                <Route path="/clients" element={<ClientList />} />
                            </Route>
                        </Route>

                        <Route path="*" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                </Router>
            </AuthProvider>
        </ConfigProvider>
    );
}

export default App;
