import React, { useState, useEffect } from 'react';
import { Typography, Card, Statistic, Row, Col } from 'antd';
import { DollarOutlined, ShoppingOutlined, FileTextOutlined, UserOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { useAuth } from '../context/AuthContext';

const { Title } = Typography;

const Dashboard = () => {
    const navigate = useNavigate();
    const { user } = useAuth();
    const [stats, setStats] = useState({
        quotes: 0,
        products: 0,
        clients: 0,
        revenue: 0
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const requests = [api.get('/quotes')];

                // Only fetch products/clients if not a client user (or if client needs product count?)
                // Assuming client sees product count if they have access to catalog
                if (user?.role.name !== 'client') {
                    requests.push(api.get('/products'));
                    requests.push(api.get('/clients'));
                } else {
                    requests.push(Promise.resolve({ data: [] })); // Placeholder for products
                    requests.push(Promise.resolve({ data: [] })); // Placeholder for clients
                }

                const [quotesRes, productsRes, clientsRes] = await Promise.all(requests);

                // Calculate revenue (sum of all quotes for simplicity)
                const revenue = quotesRes.data.reduce((acc, curr) => acc + (parseFloat(curr.total_amount) || 0), 0);

                setStats({
                    quotes: quotesRes.data.length,
                    products: productsRes.data ? productsRes.data.length : 0,
                    clients: clientsRes.data ? clientsRes.data.length : 0,
                    revenue: revenue
                });
            } catch (error) {
                console.error("Dashboard fetch error:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [user]);

    const cardStyle = { cursor: 'pointer', height: '100%' };
    const isClient = user?.role.name === 'client';

    return (
        <div>
            <Title level={2}>Dashboard</Title>
            <Row gutter={16}>
                <Col span={6}>
                    <Card hoverable style={cardStyle} onClick={() => navigate('/quotes')}>
                        <Statistic
                            title="My Quotes"
                            value={stats.quotes}
                            loading={loading}
                            prefix={<FileTextOutlined />}
                        />
                    </Card>
                </Col>

                {!isClient && (
                    <>
                        <Col span={6}>
                            <Card hoverable style={cardStyle} onClick={() => navigate('/products')}>
                                <Statistic
                                    title="Products"
                                    value={stats.products}
                                    loading={loading}
                                    prefix={<ShoppingOutlined />}
                                />
                            </Card>
                        </Col>
                        <Col span={6}>
                            <Card hoverable style={cardStyle} onClick={() => navigate('/clients')}>
                                <Statistic
                                    title="Clients"
                                    value={stats.clients}
                                    loading={loading}
                                    prefix={<UserOutlined />}
                                />
                            </Card>
                        </Col>
                        <Col span={6}>
                            <Card hoverable style={cardStyle}>
                                <Statistic
                                    title="Total Revenue (Est.)"
                                    value={stats.revenue}
                                    precision={2}
                                    loading={loading}
                                    prefix={<DollarOutlined />}
                                />
                            </Card>
                        </Col>
                    </>
                )}

                {isClient && (
                    <Col span={6}>
                        {/* Placeholder for Orders when implemented */}
                        <Card hoverable style={cardStyle}>
                            <Statistic
                                title="My Orders"
                                value={0}
                                loading={loading}
                                prefix={<ShoppingOutlined />}
                            />
                        </Card>
                    </Col>
                )}
            </Row>
        </div>
    );
};

export default Dashboard;
