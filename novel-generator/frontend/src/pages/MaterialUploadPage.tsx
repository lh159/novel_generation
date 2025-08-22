import React, { useState } from 'react'
import { Upload, Button, message, Card, List, Tag, Space, Typography } from 'antd'
import { InboxOutlined, FileTextOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const { Dragger } = Upload
const { Title } = Typography

interface Category {
  id: number
  name: string
  description: string
}

const MaterialUploadPage: React.FC = () => {
  const [fileList, setFileList] = useState<any[]>([])
  const [uploading, setUploading] = useState(false)
  const [categories, setCategories] = useState<Category[]>([])
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [generating, setGenerating] = useState<number | null>(null)
  const navigate = useNavigate()

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning('请先选择文件')
      return
    }

    const formData = new FormData()
    // 修复：使用正确的字段名 'file' 而不是 'files[]'
    formData.append('file', fileList[0])

    setUploading(true)

    try {
      const response = await fetch('/api/materials/upload', {
        method: 'POST',
        body: formData,
      })
      
      if (response.ok) {
        const result = await response.json()
        setCategories(result.categories || [])
        setUploadSuccess(true)
        message.success(`材料上传成功！解析出 ${result.categories_count} 个小说类别`)
      } else {
        const error = await response.json()
        // 修复：显示更详细的错误信息
        const errorMessage = error.detail || error.message || '未知错误'
        message.error(`上传失败: ${errorMessage}`)
        console.error('Upload error response:', error)
      }
    } catch (error) {
      // 修复：显示具体的错误信息
      const errorMessage = error instanceof Error ? error.message : '网络错误'
      message.error(`上传失败: ${errorMessage}`)
      console.error('Upload error:', error)
    } finally {
      setUploading(false)
    }
  }

  const handleGenerateNovel = async (categoryId: number) => {
    setGenerating(categoryId)
    try {
      // 显示生成开始的提示
      message.loading('正在生成小说大纲，请稍候...', 0)
      
      const response = await fetch('/api/novels/generate-outline', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ category_id: categoryId }),
      })

      // 关闭loading消息
      message.destroy()

      if (response.ok) {
        const result = await response.json()
        message.success(`小说大纲生成成功！标题: ${result.title}`, 3)
        // 延迟导航，让用户看到成功消息
        setTimeout(() => {
          navigate(`/novels/${result.novel_id}`)
        }, 1500)
      } else {
        const error = await response.json()
        message.error(`生成失败: ${error.detail || '未知错误'}`)
      }
    } catch (error) {
      message.destroy()
      message.error('生成失败，请重试')
      console.error('Generate error:', error)
    } finally {
      setGenerating(null)
    }
  }

  const uploadProps = {
    name: 'file',
    multiple: false,
    fileList,
    beforeUpload: (file: any) => {
      const isMarkdown = file.type === 'text/markdown' || file.name.endsWith('.md')
      const isText = file.type === 'text/plain' || file.name.endsWith('.txt')
      
      if (!isMarkdown && !isText) {
        message.error('只支持 Markdown 和文本文件格式!')
        return false
      }
      
      const isLt10M = file.size / 1024 / 1024 < 10
      if (!isLt10M) {
        message.error('文件大小不能超过 10MB!')
        return false
      }
      
      setFileList([file])
      return false
    },
    onRemove: () => {
      setFileList([])
      setUploadSuccess(false)
      setCategories([])
    },
  }

  return (
    <div className="page-container">
      <Title level={2} style={{ textAlign: 'center', marginBottom: '32px' }}>
        上传小说材料
      </Title>
      
      <Card style={{ marginBottom: '24px' }}>
        <Dragger {...uploadProps}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持 Markdown (.md) 和文本 (.txt) 文件格式，文件大小不超过 10MB
          </p>
        </Dragger>
        
        <div style={{ textAlign: 'center', marginTop: '16px' }}>
          <Button
            type="primary"
            onClick={handleUpload}
            loading={uploading}
            disabled={fileList.length === 0}
            size="large"
            icon={<FileTextOutlined />}
          >
            {uploading ? '上传中...' : '开始上传'}
          </Button>
        </div>
      </Card>

      {uploadSuccess && categories.length > 0 && (
        <Card title="解析结果" extra={<CheckCircleOutlined style={{ color: '#52c41a' }} />}>
          <List
            dataSource={categories}
            renderItem={(category) => (
              <List.Item
                actions={[
                  <Button 
                    type="primary" 
                    onClick={() => handleGenerateNovel(category.id)}
                    icon={<FileTextOutlined />}
                    loading={generating === category.id}
                    disabled={generating !== null}
                  >
                    {generating === category.id ? '生成中...' : '生成大纲'}
                  </Button>
                ]}
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <span>{category.name}</span>
                      <Tag color="blue">类别 {category.id}</Tag>
                    </Space>
                  }
                  description={category.description}
                />
              </List.Item>
            )}
          />
        </Card>
      )}

      <Card style={{ marginTop: '24px' }}>
        <Title level={4}>使用说明</Title>
        <div style={{ lineHeight: '1.8' }}>
          <p><strong>1. 文件格式要求：</strong></p>
          <ul>
            <li>支持 Markdown (.md) 和纯文本 (.txt) 格式</li>
            <li>文件大小不超过 10MB</li>
            <li>内容必须包含小说类别、写作指导和必需汉字信息</li>
          </ul>
          
          <p><strong>2. 上传流程：</strong></p>
          <ul>
            <li>选择或拖拽文件到上传区域</li>
            <li>点击"开始上传"按钮</li>
            <li>系统自动解析文件内容</li>
            <li>选择感兴趣的小说类别生成大纲</li>
          </ul>
          
          <p><strong>3. 注意事项：</strong></p>
          <ul>
            <li>确保文件编码为 UTF-8</li>
            <li>文件内容需要按照指定格式组织</li>
            <li>生成大纲后可在详情页逐章生成内容</li>
          </ul>
        </div>
      </Card>
    </div>
  )
}

export default MaterialUploadPage
