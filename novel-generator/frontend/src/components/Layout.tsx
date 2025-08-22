import React from 'react'
import { Layout as AntLayout, Menu, Button, Space } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import { 
  HomeOutlined, 
  UploadOutlined, 
  BookOutlined, 
  UserOutlined 
} from '@ant-design/icons'

const { Header, Content } = AntLayout

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/upload',
      icon: <UploadOutlined />,
      label: '上传材料',
    },
    {
      key: '/novels',
      icon: <BookOutlined />,
      label: '小说列表',
    },
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  return (
    <AntLayout>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{ color: 'white', fontSize: '1.5rem', fontWeight: 'bold', marginRight: '48px' }}>
            小说生成网站
          </div>
          <Menu
            theme="dark"
            mode="horizontal"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={handleMenuClick}
            style={{ background: 'transparent', border: 'none' }}
          />
        </div>
        <Space>
          <Button type="primary" icon={<UserOutlined />}>
            开始体验
          </Button>
        </Space>
      </Header>
      <Content>
        {children}
      </Content>
    </AntLayout>
  )
}

export default Layout
