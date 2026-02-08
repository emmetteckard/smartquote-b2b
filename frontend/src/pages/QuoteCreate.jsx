import React, { useState, useEffect } from 'react';
import { Form, Select, DatePicker, Input, Button, Table, InputNumber, Typography, Card, message, Divider } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';

const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const QuoteCreate = () => {
    const navigate = useNavigate();
    const [form] = Form.useForm();
    const [clients, setClients] = useState([]); // Mock for now if API missing
    const [products, setProducts] = useState([]);
    const [items, setItems] = useState([]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [productsRes, clientsRes] = await Promise.all([
                    api.get('/products'),
                    api.get('/clients')
                ]);
                setProducts(productsRes.data);
                setClients(clientsRes.data);
            } catch (error) {
                message.error('Failed to fetch data');
            }
        };
        fetchData();
    }, []);

    const handleAddItem = () => {
        const newItem = {
            key: Date.now(),
            product_id: null,
            quantity: 1,
            unit_price: 0,
            discount_percent: 0,
        };
        setItems([...items, newItem]);
    };

    const handleRemoveItem = (key) => {
        setItems(items.filter(item => item.key !== key));
    };

    const handleItemChange = (key, field, value) => {
        const newItems = items.map(item => {
            if (item.key === key) {
                const updatedItem = { ...item, [field]: value };
                if (field === 'product_id') {
                    // Auto-fill price (mock logic, usually fetch price)
                    updatedItem.unit_price = 100; // Placeholder
                }
                return updatedItem;
            }
            return item;
        });
        setItems(newItems);
    };

    const calculateTotal = () => {
        return items.reduce((sum, item) => {
            const price = item.unit_price || 0;
            const qty = item.quantity || 0;
            const discount = item.discount_percent || 0;
            return sum + (price * qty * (1 - discount / 100));
        }, 0);
    };

    const onFinish = async (values) => {
        if (items.length === 0) {
            message.error('Please add at least one item');
            return;
        }

        const payload = {
            client_id: values.client_id,
            valid_until: values.valid_until.format('YYYY-MM-DD'),
            notes: values.notes,
            currency: "USD",
            items: items.map(item => ({
                product_id: item.product_id,
                quantity: item.quantity,
                unit_price: item.unit_price,
                discount_percent: item.discount_percent,
                notes: ""
            }))
        };

        try {
            await api.post('/quotes', payload);
            message.success('Quotation created successfully');
            navigate('/quotes');
        } catch (error) {
            message.error(error.response?.data?.detail || 'Failed to create quotation');
        }
    };

    const columns = [
        {
            title: 'Product',
            dataIndex: 'product_id',
            render: (text, record) => (
                <Select
                    style={{ width: 200 }}
                    value={record.product_id}
                    onChange={(val) => handleItemChange(record.key, 'product_id', val)}
                >
                    {products.map(p => <Option key={p.id} value={p.id}>{p.sku} - {p.name}</Option>)}
                </Select>
            )
        },
        {
            title: 'Quantity',
            dataIndex: 'quantity',
            render: (text, record) => (
                <InputNumber min={1} value={record.quantity} onChange={(val) => handleItemChange(record.key, 'quantity', val)} />
            )
        },
        {
            title: 'Unit Price',
            dataIndex: 'unit_price',
            render: (text, record) => (
                <InputNumber min={0} value={record.unit_price} onChange={(val) => handleItemChange(record.key, 'unit_price', val)} />
            )
        },
        {
            title: 'Discount %',
            dataIndex: 'discount_percent',
            render: (text, record) => (
                <InputNumber min={0} max={100} value={record.discount_percent} onChange={(val) => handleItemChange(record.key, 'discount_percent', val)} />
            )
        },
        {
            title: 'Total',
            render: (_, record) => {
                const total = (record.unit_price || 0) * (record.quantity || 0) * (1 - (record.discount_percent || 0) / 100);
                return total.toFixed(2);
            }
        },
        {
            title: 'Action',
            render: (_, record) => (
                <Button icon={<DeleteOutlined />} onClick={() => handleRemoveItem(record.key)} danger />
            )
        }
    ];

    return (
        <div>
            <Title level={2}>New Quotation</Title>
            <Form form={form} layout="vertical" onFinish={onFinish}>
                <Card title="Client Details" style={{ marginBottom: 24 }}>
                    <Form.Item name="client_id" label="Client" rules={[{ required: true }]}>
                        <Select placeholder="Select Client" showSearch optionFilterProp="children">
                            {clients.map(client => (
                                <Option key={client.id} value={client.id}>{client.company_name}</Option>
                            ))}
                        </Select>
                    </Form.Item>
                    <Form.Item name="valid_until" label="Valid Until" rules={[{ required: true }]}>
                        <DatePicker style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item name="notes" label="Notes">
                        <TextArea rows={2} />
                    </Form.Item>
                </Card>

                <Card title="Items" style={{ marginBottom: 24 }}>
                    <Table
                        dataSource={items}
                        columns={columns}
                        pagination={false}
                        footer={() => (
                            <Button type="dashed" onClick={handleAddItem} block icon={<PlusOutlined />}>
                                Add Item
                            </Button>
                        )}
                    />
                    <div style={{ textAlign: 'right', marginTop: 16 }}>
                        <Title level={4}>Total: USD {calculateTotal().toFixed(2)}</Title>
                    </div>
                </Card>

                <Form.Item>
                    <Button type="primary" htmlType="submit" size="large">Create Quotation</Button>
                </Form.Item>
            </Form>
        </div>
    );
};

export default QuoteCreate;
