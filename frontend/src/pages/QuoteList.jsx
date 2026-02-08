import React, { useState, useEffect } from 'react';
import { Table, Button, Tag, Typography, message, Space } from 'antd';
import { PlusOutlined, FileTextOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';

const { Title } = Typography;

const QuoteList = () => {
    const [quotes, setQuotes] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchQuotes = async () => {
            try {
                const response = await api.get('/quotes');
                setQuotes(response.data);
            } catch (error) {
                message.error('Failed to fetch quotations');
            } finally {
                setLoading(false);
            }
        };
        fetchQuotes();
    }, []);

    const columns = [
        {
            title: 'Quote #',
            dataIndex: 'quotation_number',
            key: 'quotation_number',
        },
        {
            title: 'Client',
            dataIndex: 'client_id', // TODO: Show client name
            key: 'client',
            render: (clientId) => `Client #${clientId}`,
        },
        {
            title: 'Total',
            dataIndex: 'total_amount',
            key: 'total_amount',
            render: (amount, record) => `${record.currency} ${amount}`,
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (status) => (
                <Tag color={status === 'confirmed' ? 'green' : 'orange'}>
                    {status.toUpperCase()}
                </Tag>
            ),
        },
        {
            title: 'Created At',
            dataIndex: 'created_at',
            key: 'created_at',
            render: (date) => new Date(date).toLocaleDateString(),
        },
        {
            title: 'Action',
            key: 'action',
            render: (_, record) => (
                <Space>
                    <Button size="small" icon={<FileTextOutlined />}>View</Button>
                </Space>
            ),
        }
    ];

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
                <Title level={2}>Quotations</Title>
                <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/quotes/new')}>
                    New Quotation
                </Button>
            </div>

            <Table columns={columns} dataSource={quotes} rowKey="id" loading={loading} />
        </div>
    );
};

export default QuoteList;
