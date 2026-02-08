import React, { useState, useEffect } from 'react';
import { Table, Button, Space, message, Modal, Form, Input, InputNumber, Select, Typography, Upload, Tag, Tooltip } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, UploadOutlined, DownloadOutlined, AppstoreOutlined } from '@ant-design/icons';
import api from '../utils/api';
import { useAuth } from '../context/AuthContext';

const { Title } = Typography;
const { Option } = Select;

const ProductList = () => {
    const { user } = useAuth();
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [form] = Form.useForm();
    const [editingId, setEditingId] = useState(null);
    const [uploading, setUploading] = useState(false);

    const fetchProducts = async () => {
        setLoading(true);
        try {
            const response = await api.get('/products');
            setProducts(response.data);
        } catch (error) {
            message.error('Failed to fetch products');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProducts();
    }, []);

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
                // Update logic would go here if API supported it
                message.info('Update feature coming soon');
            } else {
                await api.post('/products', values);
                message.success('Product created successfully');
            }
            setIsModalVisible(false);
            fetchProducts();
        } catch (error) {
            message.error(error.response?.data?.detail || 'Operation failed');
        }
    };

    const handleDownloadTemplate = async () => {
        try {
            const response = await api.get('/products/template/xlsx', { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'product_template.xlsx');
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (error) {
            message.error('Failed to download template');
        }
    };

    const handleExport = async () => {
        try {
            const response = await api.get('/products/export/xlsx', { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'products_export.xlsx');
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        } catch (error) {
            message.error('Failed to export products');
        }
    };

    const handleUpload = async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        setUploading(true);
        try {
            const response = await api.post('/products/upload/xlsx', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            message.success(`Uploaded: ${response.data.success} success, ${response.data.errors.length} errors`);
            if (response.data.errors.length > 0) {
                console.log("Upload errors:", response.data.errors);
                Modal.warning({
                    title: 'Upload Items with Errors',
                    content: (
                        <div style={{ maxHeight: '300px', overflow: 'auto' }}>
                            <ul>
                                {response.data.errors.map((err, idx) => <li key={idx}>{err}</li>)}
                            </ul>
                        </div>
                    )
                });
            }
            fetchProducts();
        } catch (error) {
            message.error('Upload failed');
        } finally {
            setUploading(false);
        }
        return false; // Prevent auto upload
    };

    const columns = [
        {
            title: 'SKU',
            dataIndex: 'sku',
            key: 'sku',
        },
        {
            title: 'Name',
            dataIndex: 'name',
            key: 'name',
            render: (text, record) => (
                <Space>
                    {text}
                    {record.components_list && record.components_list.length > 0 && (
                        <Tooltip title={`Bundle of ${record.components_list.length} components`}>
                            <Tag color="purple" icon={<AppstoreOutlined />}>Bundle</Tag>
                        </Tooltip>
                    )}
                </Space>
            )
        },
        {
            title: 'Category',
            dataIndex: 'category',
            key: 'category',
        },
        {
            title: 'Unit',
            dataIndex: 'unit',
            key: 'unit',
        }
    ];

    if (user?.role?.name === 'client') {
        columns.push({
            title: 'Your Price',
            dataIndex: 'current_price',
            key: 'current_price',
            render: (text) => text ? `$${text.toFixed(2)}` : '-'
        });
    } else if (['admin', 'super_admin', 'sales'].includes(user?.role?.name)) {
        columns.push(
            {
                title: 'Tier X',
                dataIndex: ['tier_prices', 'X'],
                key: 'tier_x',
                render: (text) => text ? `$${text.toFixed(2)}` : '-'
            },
            {
                title: 'Tier S',
                dataIndex: ['tier_prices', 'S'],
                key: 'tier_s',
                render: (text) => text ? `$${text.toFixed(2)}` : '-'
            },
            {
                title: 'Tier A',
                dataIndex: ['tier_prices', 'A'],
                key: 'tier_a',
                render: (text) => text ? `$${text.toFixed(2)}` : '-'
            }
        );
    }

    columns.push({
        title: 'Action',
        key: 'action',
        render: (_, record) => (
            <Space size="middle">
                <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
                {/* <Button icon={<DeleteOutlined />} danger /> */}
            </Space>
        ),
    });

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
                <Title level={2}>Products</Title>
                <Space>
                    <Button onClick={handleExport}>
                        Export Excel
                    </Button>
                    <Button icon={<DownloadOutlined />} onClick={handleDownloadTemplate}>
                        Template (Excel)
                    </Button>
                    <Upload showUploadList={false} beforeUpload={handleUpload} accept=".xlsx">
                        <Button icon={<UploadOutlined />} loading={uploading}>
                            Bulk Upload (Excel)
                        </Button>
                    </Upload>
                    <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
                        Add Product
                    </Button>
                </Space>
            </div>

            <Table columns={columns} dataSource={products} rowKey="id" loading={loading} />

            <Modal
                title={editingId ? "Edit Product" : "Add Product"}
                open={isModalVisible}
                onCancel={handleCancel}
                onOk={() => form.submit()}
            >
                <Form form={form} layout="vertical" onFinish={handleSubmit}>
                    <Form.Item name="sku" label="SKU" rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <Form.Item name="name" label="Name" rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <Form.Item name="category" label="Category">
                        <Input />
                    </Form.Item>
                    <Form.Item name="unit" label="Unit" initialValue="pcs">
                        <Select>
                            <Option value="pcs">pcs</Option>
                            <Option value="kg">kg</Option>
                            <Option value="m">m</Option>
                            <Option value="set">set</Option>
                        </Select>
                    </Form.Item>
                    <Form.Item name="min_order_qty" label="Min Order Qty" initialValue={1}>
                        <InputNumber min={1} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item name="description" label="Description">
                        <Input.TextArea />
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default ProductList;
