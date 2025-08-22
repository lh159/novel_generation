import React, { useState, useEffect } from 'react'
import { 
  Card, 
  List, 
  Button, 
  Tag, 
  Space, 
  Typography, 
  Empty, 
  Spin, 
  message, 
  Progress,
  Modal,
  Descriptions
} from 'antd'
import { 
  BookOutlined, 
  PlayCircleOutlined, 
  EyeOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import { useNavigate, useParams } from 'react-router-dom'

const { Title, Text, Paragraph } = Typography

interface Chapter {
  id: number
  chapter_number: number
  title: string
  content: string
  summary: string
  status: string
  is_generating: boolean
}

interface Novel {
  id: number
  title: string
  outline: string
  content: string
  category_id: number
  status: string
  total_chapters: number
  completed_chapters: number
  chapters: Chapter[]
}

const NovelDetailPage: React.FC = () => {
  const [novel, setNovel] = useState<Novel | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState<number | null>(null)
  const [outlineVisible, setOutlineVisible] = useState(false)
  const navigate = useNavigate()
  const { novelId } = useParams<{ novelId: string }>()

  useEffect(() => {
    if (novelId) {
      fetchNovel(parseInt(novelId))
    }
  }, [novelId])

  const fetchNovel = async (id: number) => {
    try {
      const response = await fetch(`/api/novels/${id}`)
      if (response.ok) {
        const data = await response.json()
        setNovel(data)
      } else {
        message.error('获取小说详情失败')
      }
    } catch (error) {
      message.error('网络错误，请重试')
      console.error('Fetch novel error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateChapter = async (chapterNumber: number) => {
    if (!novel) return
    
    setGenerating(chapterNumber)
    try {
      const response = await fetch('/api/novels/generate-chapter', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          novel_id: novel.id,
          chapter_number: chapterNumber
        })
      })

      if (response.ok) {
        message.success(`第${chapterNumber}章生成成功！`)
        await fetchNovel(novel.id) // 重新获取小说数据
      } else {
        const error = await response.json()
        message.error(error.detail || `第${chapterNumber}章生成失败`)
      }
    } catch (error) {
      message.error('网络错误，请重试')
      console.error('Generate chapter error:', error)
    } finally {
      setGenerating(null)
    }
  }

  const handleViewChapter = (chapterNumber: number) => {
    navigate(`/novels/${novel?.id}/chapters/${chapterNumber}`)
  }

  const handleRoleplay = (chapterNumber: number) => {
    navigate(`/roleplay/${novel?.id}/${chapterNumber}`)
  }

  const getChapterStatusIcon = (chapter: Chapter) => {
    if (chapter.is_generating || generating === chapter.chapter_number) {
      return <LoadingOutlined spin style={{ color: '#1890ff' }} />
    }
    
    switch (chapter.status) {
      case 'completed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />
      case 'planned':
        return <ClockCircleOutlined style={{ color: '#faad14' }} />
      case 'failed':
        return <ExclamationCircleOutlined style={{ color: '#f5222d' }} />
      default:
        return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />
    }
  }

  const getChapterStatusText = (chapter: Chapter) => {
    if (chapter.is_generating || generating === chapter.chapter_number) {
      return '生成中'
    }
    
    switch (chapter.status) {
      case 'completed':
        return '已完成'
      case 'planned':
        return '待生成'
      case 'failed':
        return '生成失败'
      default:
        return '未知'
    }
  }

  const getChapterStatusColor = (chapter: Chapter) => {
    if (chapter.is_generating || generating === chapter.chapter_number) {
      return 'processing'
    }
    
    switch (chapter.status) {
      case 'completed':
        return 'success'
      case 'planned':
        return 'warning'
      case 'failed':
        return 'error'
      default:
        return 'default'
    }
  }

  const canGenerateChapter = (chapter: Chapter) => {
    if (chapter.status === 'completed' || chapter.is_generating || generating === chapter.chapter_number) {
      return false
    }
    
    // 第一章可以直接生成
    if (chapter.chapter_number === 1) {
      return true
    }
    
    // 其他章节需要前一章已完成
    const previousChapter = novel?.chapters.find(c => c.chapter_number === chapter.chapter_number - 1)
    return previousChapter?.status === 'completed'
  }

  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>加载中...</div>
      </div>
    )
  }

  if (!novel) {
    return (
      <div className="page-container">
        <Empty description="小说不存在" />
      </div>
    )
  }

  const progress = (novel.completed_chapters / novel.total_chapters) * 100

  return (
    <div className="page-container">
      <Card style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div style={{ flex: 1 }}>
            <Title level={2} style={{ marginBottom: '16px' }}>
              <BookOutlined style={{ marginRight: '8px', color: '#667eea' }} />
              {novel.title}
            </Title>
            
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>进度：</Text>
                <Progress 
                  percent={Math.round(progress)} 
                  strokeColor="#667eea"
                  format={() => `${novel.completed_chapters}/${novel.total_chapters} 章`}
                  style={{ marginLeft: '12px', maxWidth: '300px' }}
                />
              </div>
              
              <div>
                <Text strong>状态：</Text>
                <Tag color={novel.status === 'completed' ? 'success' : 'processing'} style={{ marginLeft: '8px' }}>
                  {novel.status === 'completed' ? '已完成' : novel.status === 'outline_generated' ? '大纲已生成' : '进行中'}
                </Tag>
              </div>
              
              <div>
                <Button type="link" onClick={() => setOutlineVisible(true)}>
                  查看大纲
                </Button>
              </div>
            </Space>
          </div>
        </div>
      </Card>

      <Title level={3} style={{ marginBottom: '16px' }}>章节列表</Title>
      
      <List
        grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 4 }}
        dataSource={novel.chapters}
        renderItem={(chapter) => (
          <List.Item>
            <Card
              size="small"
              hoverable={chapter.status === 'completed'}
              title={
                <Space>
                  {getChapterStatusIcon(chapter)}
                  <span>第{chapter.chapter_number}章</span>
                </Space>
              }
              extra={
                <Tag color={getChapterStatusColor(chapter)}>
                  {getChapterStatusText(chapter)}
                </Tag>
              }
              actions={
                chapter.status === 'completed' ? [
                  <Button 
                    type="text" 
                    icon={<EyeOutlined />}
                    onClick={() => handleViewChapter(chapter.chapter_number)}
                  >
                    阅读
                  </Button>,
                  <Button 
                    type="text" 
                    icon={<PlayCircleOutlined />}
                    onClick={() => handleRoleplay(chapter.chapter_number)}
                  >
                    体验
                  </Button>
                ] : [
                  <Button 
                    type="primary"
                    size="small"
                    loading={chapter.is_generating || generating === chapter.chapter_number}
                    disabled={!canGenerateChapter(chapter)}
                    onClick={() => handleGenerateChapter(chapter.chapter_number)}
                  >
                    {chapter.is_generating || generating === chapter.chapter_number ? '生成中' : '生成'}
                  </Button>
                ]
              }
            >
              <Card.Meta
                title={chapter.title}
                description={
                  <div>
                    {chapter.summary && (
                      <Text type="secondary" ellipsis>
                        {chapter.summary}
                      </Text>
                    )}
                    {!chapter.summary && chapter.status === 'planned' && (
                      <Text type="secondary">待生成内容</Text>
                    )}
                  </div>
                }
              />
            </Card>
          </List.Item>
        )}
      />

      <Modal
        title="小说大纲"
        open={outlineVisible}
        onCancel={() => setOutlineVisible(false)}
        footer={[
          <Button key="close" onClick={() => setOutlineVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        <Descriptions column={1} bordered>
          <Descriptions.Item label="小说标题">{novel.title}</Descriptions.Item>
          <Descriptions.Item label="总章节数">{novel.total_chapters}</Descriptions.Item>
          <Descriptions.Item label="已完成章节">{novel.completed_chapters}</Descriptions.Item>
          <Descriptions.Item label="故事大纲">
            <Paragraph>
              {novel.outline}
            </Paragraph>
          </Descriptions.Item>
          {novel.content && (
            <Descriptions.Item label="主角设定">
              <Paragraph>
                {novel.content}
              </Paragraph>
            </Descriptions.Item>
          )}
        </Descriptions>
      </Modal>
    </div>
  )
}

export default NovelDetailPage
