import React, { useState, useEffect } from 'react'
import { 
  Card, 
  Form, 
  Input, 
  InputNumber, 
  Button, 
  Select, 
  Space, 
  Typography, 
  message,
  Steps,
  Alert,
  Upload,
  List,
  Tag,
  Divider
} from 'antd'
import { BookOutlined, EditOutlined, CheckOutlined, InboxOutlined, FileTextOutlined, DeleteOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { chapterNovelApi, ChapterNovelResponse } from '../utils/api'

const { Title, Text } = Typography
const { Option } = Select
const { Dragger } = Upload

interface Material {
  id: string
  title: string
  category: string
}

interface UploadedFile {
  uid: string
  name: string
  status: 'uploading' | 'done' | 'error'
  response?: any
}

const ChapterNovelCreatePage: React.FC = () => {
  const [form] = Form.useForm()
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [materials, setMaterials] = useState<Material[]>([])
  const [createdNovel, setCreatedNovel] = useState<ChapterNovelResponse | null>(null)
  const [outlineGenerating, setOutlineGenerating] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [uploading, setUploading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    // 这里应该获取材料列表，暂时使用模拟数据
    setMaterials([
      { id: '1', title: '武侠小说写作指导', category: '武侠' },
      { id: '2', title: '现代都市素材', category: '都市' },
      { id: '3', title: '科幻世界设定', category: '科幻' },
    ])
  }, [])

  // 处理文件上传
  const handleFileUpload = async (file: any) => {
    const formData = new FormData()
    formData.append('file', file)

    setUploading(true)
    
    try {
      const response = await fetch('/api/materials/upload', {
        method: 'POST',
        body: formData,
      })
      
      if (response.ok) {
        const result = await response.json()
        
        // 添加上传成功的文件到列表
        const newFile: UploadedFile = {
          uid: file.uid,
          name: file.name,
          status: 'done',
          response: result
        }
        
        setUploadedFiles(prev => [...prev, newFile])
        
        // 将上传的材料添加到材料列表
        if (result.categories && result.categories.length > 0) {
          const newMaterials = result.categories.map((cat: any) => ({
            id: cat.id.toString(),
            title: cat.name,
            category: cat.description || '上传材料'
          }))
          setMaterials(prev => [...prev, ...newMaterials])
        }
        
        message.success(`文件上传成功！解析出 ${result.categories_count || 0} 个材料类别`)
      } else {
        const error = await response.json()
        message.error(`上传失败: ${error.detail || '未知错误'}`)
        
        const failedFile: UploadedFile = {
          uid: file.uid,
          name: file.name,
          status: 'error'
        }
        setUploadedFiles(prev => [...prev, failedFile])
      }
    } catch (error) {
      message.error(`上传失败: ${error instanceof Error ? error.message : '网络错误'}`)
      
      const failedFile: UploadedFile = {
        uid: file.uid,
        name: file.name,
        status: 'error'
      }
      setUploadedFiles(prev => [...prev, failedFile])
    } finally {
      setUploading(false)
    }
  }

  // 删除上传的文件
  const handleRemoveFile = (file: UploadedFile) => {
    setUploadedFiles(prev => prev.filter(f => f.uid !== file.uid))
    
    // 如果文件有关联的材料，也从材料列表中移除
    if (file.response && file.response.categories) {
      const categoryIds = file.response.categories.map((cat: any) => cat.id.toString())
      setMaterials(prev => prev.filter(material => !categoryIds.includes(material.id)))
    }
  }

  const handleCreateNovel = async (values: any) => {
    setLoading(true)
    try {
      const novelData = {
        title: values.title,
        chapter_count: values.chapter_count,
        material_ids: values.material_ids || []
      }
      
      const novel = await chapterNovelApi.createNovel(novelData)
      setCreatedNovel(novel)
      setCurrentStep(1)
      message.success('小说创建成功！')
    } catch (error) {
      message.error(error instanceof Error ? error.message : '创建小说失败')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateOutline = async () => {
    if (!createdNovel) return
    
    setOutlineGenerating(true)
    try {
      const result = await chapterNovelApi.generateOutline(
        createdNovel.id, 
        createdNovel.material_ids
      )
      
      // 重新获取小说信息以获取更新的大纲
      const updatedNovel = await chapterNovelApi.getNovel(createdNovel.id)
      setCreatedNovel(updatedNovel)
      setCurrentStep(2)
      message.success(result.message)
    } catch (error) {
      message.error(error instanceof Error ? error.message : '生成大纲失败')
    } finally {
      setOutlineGenerating(false)
    }
  }

  const handleViewNovel = () => {
    if (createdNovel) {
      navigate(`/novels/${createdNovel.id}`)
    }
  }

  const steps = [
    {
      title: '创建小说',
      icon: <EditOutlined />,
      description: '设置小说基本信息'
    },
    {
      title: '生成大纲',
      icon: <BookOutlined />,
      description: '生成小说大纲和章节规划'
    },
    {
      title: '完成',
      icon: <CheckOutlined />,
      description: '开始章节创作'
    }
  ]

  return (
    <div className="page-container">
      <Title level={2} style={{ textAlign: 'center', marginBottom: '32px' }}>
        创建章节式小说
      </Title>

      <Card style={{ maxWidth: '800px', margin: '0 auto' }}>
        <Steps current={currentStep} items={steps} style={{ marginBottom: '32px' }} />

        {currentStep === 0 && (
          <div>
            <Alert
              message="章节式小说创建"
              description="创建一部分章节写作的小说，系统将自动生成大纲，然后您可以逐章生成内容。"
              type="info"
              showIcon
              style={{ marginBottom: '24px' }}
            />
            
            <Form
              form={form}
              layout="vertical"
              onFinish={handleCreateNovel}
              initialValues={{
                chapter_count: 5,
                material_ids: []
              }}
            >
              <Form.Item
                name="title"
                label="小说标题"
                rules={[{ required: true, message: '请输入小说标题' }]}
              >
                <Input placeholder="请输入小说标题" size="large" />
              </Form.Item>

              <Form.Item
                name="chapter_count"
                label="章节数量"
                rules={[
                  { required: true, message: '请输入章节数量' },
                  { type: 'number', min: 1, max: 50, message: '章节数量应在1-50之间' }
                ]}
              >
                <InputNumber
                  min={1}
                  max={50}
                  placeholder="请输入章节数量"
                  style={{ width: '100%' }}
                  size="large"
                />
              </Form.Item>

              <Form.Item
                label="上传材料文件（可选）"
                help="上传 Markdown 或文本文件作为写作材料，支持拖拽上传"
              >
                <Dragger
                  name="file"
                  multiple={true}
                  showUploadList={false}
                  beforeUpload={(file) => {
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
                    
                    handleFileUpload(file)
                    return false
                  }}
                  disabled={uploading}
                >
                  <p className="ant-upload-drag-icon">
                    <InboxOutlined />
                  </p>
                  <p className="ant-upload-text">
                    点击或拖拽文件到此区域上传
                  </p>
                  <p className="ant-upload-hint">
                    支持单个或批量上传。只支持 .md 和 .txt 文件格式，单个文件不超过 10MB
                  </p>
                </Dragger>
                
                {uploadedFiles.length > 0 && (
                  <div style={{ marginTop: '16px' }}>
                    <Text strong>已上传文件：</Text>
                    <List
                      size="small"
                      dataSource={uploadedFiles}
                      renderItem={(file) => (
                        <List.Item
                          actions={[
                            <Button
                              key="delete"
                              type="link"
                              size="small"
                              icon={<DeleteOutlined />}
                              onClick={() => handleRemoveFile(file)}
                              danger
                            >
                              删除
                            </Button>
                          ]}
                        >
                          <List.Item.Meta
                            avatar={<FileTextOutlined />}
                            title={file.name}
                            description={
                              <Space>
                                <Tag color={file.status === 'done' ? 'green' : file.status === 'error' ? 'red' : 'blue'}>
                                  {file.status === 'done' ? '上传成功' : file.status === 'error' ? '上传失败' : '上传中'}
                                </Tag>
                                {file.response && file.response.categories_count && (
                                  <Text type="secondary">解析出 {file.response.categories_count} 个类别</Text>
                                )}
                              </Space>
                            }
                          />
                        </List.Item>
                      )}
                    />
                  </div>
                )}
              </Form.Item>

              <Divider />

              <Form.Item
                name="material_ids"
                label="关联材料（可选）"
                help="选择相关的写作材料，将用于生成大纲和内容"
              >
                <Select
                  mode="multiple"
                  placeholder="选择关联材料"
                  size="large"
                  allowClear
                >
                  {materials.map(material => (
                    <Option key={material.id} value={material.id}>
                      [{material.category}] {material.title}
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item style={{ textAlign: 'center', marginTop: '32px' }}>
                <Button
                  type="primary"
                  htmlType="submit"
                  size="large"
                  loading={loading}
                  style={{ minWidth: '120px' }}
                >
                  创建小说
                </Button>
              </Form.Item>
            </Form>
          </div>
        )}

        {currentStep === 1 && createdNovel && (
          <div>
            <Alert
              message="小说创建成功"
              description="现在为您的小说生成详细大纲和章节规划。"
              type="success"
              showIcon
              style={{ marginBottom: '24px' }}
            />

            <Card title="小说信息" style={{ marginBottom: '24px' }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <Text strong>标题：</Text>
                  <Text>{createdNovel.title}</Text>
                </div>
                <div>
                  <Text strong>章节数：</Text>
                  <Text>{createdNovel.total_chapters}章</Text>
                </div>
                <div>
                  <Text strong>状态：</Text>
                  <Text>{createdNovel.status === 'planning' ? '规划中' : '其他'}</Text>
                </div>
              </Space>
            </Card>

            <div style={{ textAlign: 'center' }}>
              <Button
                type="primary"
                size="large"
                loading={outlineGenerating}
                onClick={handleGenerateOutline}
                style={{ minWidth: '120px' }}
              >
                {outlineGenerating ? '生成中...' : '生成大纲'}
              </Button>
            </div>
          </div>
        )}

        {currentStep === 2 && createdNovel && (
          <div>
            <Alert
              message="大纲生成完成"
              description="小说大纲已生成完成，现在可以开始逐章创作内容了。"
              type="success"
              showIcon
              style={{ marginBottom: '24px' }}
            />

            {createdNovel.outline && (
              <Card title="小说大纲" style={{ marginBottom: '24px' }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text strong>简介：</Text>
                    <div style={{ marginTop: '8px' }}>
                      <Text>{createdNovel.outline.summary}</Text>
                    </div>
                  </div>
                  
                  {createdNovel.outline.main_characters && createdNovel.outline.main_characters.length > 0 && (
                    <div>
                      <Text strong>主要角色：</Text>
                      <div style={{ marginTop: '8px' }}>
                        {createdNovel.outline.main_characters.map((character, index) => (
                          <div key={index} style={{ marginBottom: '8px' }}>
                            <Text strong>{character.name}：</Text>
                            <Text>{character.description}</Text>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div>
                    <Text strong>章节规划：</Text>
                    <div style={{ marginTop: '8px' }}>
                      {createdNovel.outline.chapters?.map((chapter, index) => (
                        <div key={index} style={{ marginBottom: '8px' }}>
                          <Text strong>第{chapter.number}章 {chapter.title}：</Text>
                          <br />
                          <Text type="secondary">{chapter.summary}</Text>
                        </div>
                      ))}
                    </div>
                  </div>
                </Space>
              </Card>
            )}

            <div style={{ textAlign: 'center' }}>
              <Space>
                <Button size="large" onClick={() => navigate('/novels')}>
                  返回小说列表
                </Button>
                <Button type="primary" size="large" onClick={handleViewNovel}>
                  开始创作
                </Button>
              </Space>
            </div>
          </div>
        )}
      </Card>
    </div>
  )
}

export default ChapterNovelCreatePage
