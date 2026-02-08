import React, { useState } from 'react';
import { Layout, Menu, Button, theme } from 'antd';
import {
    MenuFoldOutlined,
    MenuUnfoldOutlined,
    DashboardOutlined,
    UserOutlined,
    ShoppingOutlined,
    FileTextOutlined,
    LogoutOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const { Header, Sider, Content } = Layout;

const MainLayout = () => {
    const [collapsed, setCollapsed] = useState(false);
    const { token: { colorBgContainer, borderRadiusLG } } = theme.useToken();
    const navigate = useNavigate();
    const location = useLocation();
    const { logout, user } = useAuth();

    const handleMenuClick = (e) => {
        if (e.key === 'logout') {
            logout();
            navigate('/login');
        } else {
            navigate(e.key);
        }
    };

    const getMenuItems = () => {
        const role = user?.role?.name;

        const items = [
            {
                key: '/dashboard',
                icon: <DashboardOutlined />,
                label: 'Dashboard',
            }
        ];

        // Products: Admin, Super Admin, Sales
        if (['admin', 'super_admin', 'sales'].includes(role)) {
            items.push({
                key: '/products',
                icon: <ShoppingOutlined />,
                label: 'Products',
            });
        }

        // Quotations: Everyone (but clients see filtered list)
        items.push({
            key: '/quotes',
            icon: <FileTextOutlined />,
            label: 'Quotations',
        });

        // Clients: Admin, Super Admin, Sales
        if (['admin', 'super_admin', 'sales'].includes(role)) {
            items.push({
                key: '/clients',
                icon: <UserOutlined />,
                label: 'Clients',
            });
        }

        items.push({
            key: 'logout',
            icon: <LogoutOutlined />,
            label: 'Logout',
            danger: true,
        });

        return items;
    };

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Sider trigger={null} collapsible collapsed={collapsed}>
                <div className="demo-logo-vertical" style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)', borderRadius: 6 }} />
                <Menu
                    theme="dark"
                    mode="inline"
                    defaultSelectedKeys={[location.pathname]}
                    onClick={handleMenuClick}
                    items={getMenuItems()}
                />
            </Sider>
            <Layout>
                <Header style={{ padding: 0, background: colorBgContainer, display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingRight: 24 }}>
                    <Button
                        type="text"
                        icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                        onClick={() => setCollapsed(!collapsed)}
                        style={{
                            fontSize: '16px',
                            width: 64,
                            height: 64,
                        }}
                    />
                    <div>
                        {user?.role?.name === 'client' && <span style={{ marginRight: 16, fontWeight: 'bold' }}>Client Portal</span>}
                        Welcome, {user?.full_name}
                    </div>
                </Header>
                <Content
                    style={{
                        margin: '24px 16px',
                        padding: 24,
                        minHeight: 280,
                        background: colorBgContainer,
                        borderRadius: borderRadiusLG,
                    }}
                >
                    <Outlet />
                </Content>
            </Layout>
        </Layout>
    );
};

export default MainLayout;
