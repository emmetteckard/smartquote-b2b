import React, { useState, useEffect } from 'react';
import { Table, Button, Space, message, Modal, Form, Input, Select, Typography, Tag, Card } from 'antd';
import { PlusOutlined, EditOutlined, UserOutlined } from '@ant-design/icons';
import api from '../utils/api';
import { useAuth } from '../context/AuthContext';

const { Title } = Typography;
const { Option } = Select;

const ClientList = () => {
    const [clients, setClients] = useState([]);
    const [salesReps, setSalesReps] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [form] = Form.useForm();
    const [editingId, setEditingId] = useState(null);
    const { user } = useAuth(); // Get current user and role

    const fetchClients = async () => {
        setLoading(true);
        try {
            const response = await api.get('/clients');
            setClients(response.data);
        } catch (error) {
            message.error('Failed to fetch clients');
        } finally {
            setLoading(false);
        }
    };

    const fetchSalesReps = async () => {
        if (user?.role.name === 'admin' || user?.role.name === 'super_admin') {
            try {
                const response = await api.get('/users?role=sales');
                setSalesReps(response.data);
            } catch (error) {
                console.error("Failed to fetch sales reps", error);
            }
        }
    };

    useEffect(() => {
        fetchClients();
        fetchSalesReps();
    }, [user]);

    const handleAdd = () => {
        setEditingId(null);
        form.resetFields();
        setIsModalVisible(true);
    };

    const handleEdit = (record) => {
        setEditingId(record.id);
        form.setFieldsValue(record);
        setIsModalVisible(true);
    };

    const handleCancel = () => {
        setIsModalVisible(false);
    };

    const handleSubmit = async (values) => {
        try {
            if (editingId) {
                await api.put(`/clients/${editingId}`, values);
                message.success('Client updated successfully');
            } else {
                await api.post('/clients', values);
                message.success('Client created successfully');
            }
            setIsModalVisible(false);
            fetchClients();
        } catch (error) {
            message.error(error.response?.data?.detail || 'Operation failed');
        }
    };

    const columns = [
        {
            title: 'Company',
            dataIndex: 'company_name',
            key: 'company_name',
        },
        {
            title: 'Contact',
            dataIndex: 'contact_person',
            key: 'contact_person',
        },
        {
            title: 'Email',
            dataIndex: 'email',
            key: 'email',
        },
        {
            title: 'Tier',
            dataIndex: 'tier',
            key: 'tier',
            render: (tier) => {
                let color = 'default';
                if (tier === 'X') color = 'gold';
                if (tier === 'S') color = 'blue';
                return <Tag color={color}>{tier}</Tag>;
            }
        },
        {
            title: 'Payment Terms',
            dataIndex: 'payment_terms',
            key: 'payment_terms',
            render: (days) => `${days} Days`,
        },
        // Only show Sales Rep to Admins
        ...(user?.role.name === 'admin' || user?.role.name === 'super_admin' ? [{
            title: 'Sales Rep',
            dataIndex: 'sales_rep_id',
            key: 'sales_rep_id',
            render: (id) => {
                const rep = salesReps.find(r => r.id === id);
                return rep ? rep.full_name : 'Unassigned';
            }
        }] : []),
        {
            title: 'Action',
            key: 'action',
            render: (_, record) => (
                <Space size="middle">
                    <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
                </Space>
            ),
        },
    ];

    const canEditTier = user?.role.name === 'admin' || user?.role.name === 'super_admin';

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
                <Title level={2}>Clients</Title>
                <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
                    Add Client
                </Button>
            </div>

            <Table columns={columns} dataSource={clients} rowKey="id" loading={loading} />

            <Modal
                title={editingId ? "Edit Client" : "Add Client"}
                open={isModalVisible}
                onCancel={handleCancel}
                onOk={() => form.submit()}
                width={800}
            >
                <Form form={form} layout="vertical" onFinish={handleSubmit}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <Form.Item name="company_name" label="Company Name" rules={[{ required: true }]}>
                            <Input prefix={<UserOutlined />} />
                        </Form.Item>
                        <Form.Item name="contact_person" label="Contact Person">
                            <Input />
                        </Form.Item>
                        <Form.Item name="email" label="Email" rules={[{ type: 'email' }]}>
                            <Input />
                        </Form.Item>
                        <Form.Item name="phone" label="Phone">
                            <Input />
                        </Form.Item>

                        <Form.Item name="tier" label="Pricing Tier" initialValue="A">
                            <Select disabled={!canEditTier}>
                                <Option value="A">Tier A (Economy)</Option>
                                <Option value="S">Tier S (Standard)</Option>
                                <Option value="X">Tier X (Premium)</Option>
                            </Select>
                        </Form.Item>

                        {(user?.role.name === 'admin' || user?.role.name === 'super_admin') && (
                            <Form.Item name="sales_rep_id" label="Assigned Sales Rep">
                                <Select placeholder="Select Sales Rep" allowClear>
                                    {salesReps.map(rep => (
                                        <Option key={rep.id} value={rep.id}>{rep.full_name}</Option>
                                    ))}
                                </Select>
                            </Form.Item>
                        )}

                        <Form.Item name="payment_terms" label="Payment Terms (Days)" initialValue={30}>
                            <Input type="number" disabled={!canEditTier} />
                        </Form.Item>
                        <Form.Item name="tax_id" label="Tax ID">
                            <Input />
                        </Form.Item>
                        <Form.Item name="credit_limit" label="Credit Limit">
                            <Input type="number" step="0.01" disabled={!canEditTier} />
                        </Form.Item>
                    </div>
                    <Form.Item name="address" label="Address">
                        <Input.TextArea rows={2} />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default ClientList;
