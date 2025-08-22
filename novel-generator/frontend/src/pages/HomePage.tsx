import React from 'react'
import { Button, Space } from 'antd'
import { useNavigate } from 'react-router-dom'
import { 
  UploadOutlined, 
  BookOutlined, 
  UserOutlined, 
  RobotOutlined 
} from '@ant-design/icons'

const HomePage: React.FC = () => {
  const navigate = useNavigate()

  const features = [
    {
      icon: <BookOutlined className="feature-icon" />,
      title: '章节式创作',
      description: '全新的章节式小说创作模式，自动生成大纲，逐章创作内容，支持精细化的创作控制和进度管理。'
    },
    {
      icon: <UploadOutlined className="feature-icon" />,
      title: '材料投喂系统',
      description: '支持上传《构建小说所需材料.md》文件，系统自动解析小说类别、写作指导和必需汉字。'
    },
    {
      icon: <RobotOutlined className="feature-icon" />,
      title: 'AI小说生成',
      description: '基于DeepSeek-Reasoner模型，智能生成包含大量对白的小说内容，确保使用指定的汉字材料。'
    },
    {
      icon: <UserOutlined className="feature-icon" />,
      title: '沉浸式主角扮演',
      description: '用户扮演小说主角，无需输入对白，通过阅读主角台词和确认推进来体验小说剧情发展。'
    },
    {
      icon: <BookOutlined className="feature-icon" />,
      title: '智能剧情控制',
      description: '主角对白暂停等待用户确认，其他角色对白自动推进，确保流畅的阅读体验。'
    }
  ]

  return (
    <div className="page-container">
      <div className="hero-section">
        <h1 className="hero-title">智能小说生成平台</h1>
        <p className="hero-subtitle">
          基于AI的沉浸式小说创作体验，让您成为故事的主角
        </p>
        <Space size="large">
          <Button 
            type="primary" 
            size="large" 
            icon={<BookOutlined />}
            onClick={() => navigate('/novels/chapter/create')}
          >
            章节式创作
          </Button>
          <Button 
            size="large" 
            icon={<UploadOutlined />}
            onClick={() => navigate('/upload')}
          >
            传统创作
          </Button>
          <Button 
            size="large" 
            icon={<BookOutlined />}
            onClick={() => navigate('/novels')}
          >
            浏览小说
          </Button>
        </Space>
      </div>

      <div className="feature-grid">
        {features.map((feature, index) => (
          <div key={index} className="feature-card">
            {feature.icon}
            <h3 className="feature-title">{feature.title}</h3>
            <p className="feature-description">{feature.description}</p>
          </div>
        ))}
      </div>

      <div style={{ textAlign: 'center', marginTop: '48px' }}>
        <h2 style={{ fontSize: '2rem', marginBottom: '24px', color: '#1a1a1a' }}>
          如何使用？
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', marginTop: '32px' }}>
          <div style={{ padding: '20px', background: '#f8f9fa', borderRadius: '12px' }}>
            <h3 style={{ color: '#667eea', marginBottom: '12px' }}>1. 选择创作模式</h3>
            <p style={{ color: '#666' }}>
              <strong>章节式：</strong>自动生成大纲，逐章创作<br/>
              <strong>传统式：</strong>上传材料，一次性生成
            </p>
          </div>
          <div style={{ padding: '20px', background: '#f8f9fa', borderRadius: '12px' }}>
            <h3 style={{ color: '#667eea', marginBottom: '12px' }}>2. AI智能生成</h3>
            <p style={{ color: '#666' }}>基于DeepSeek模型，生成包含丰富对白的小说内容</p>
          </div>
          <div style={{ padding: '20px', background: '#f8f9fa', borderRadius: '12px' }}>
            <h3 style={{ color: '#667eea', marginBottom: '12px' }}>3. 沉浸式体验</h3>
            <p style={{ color: '#666' }}>扮演主角，通过阅读和确认推进剧情发展</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage
