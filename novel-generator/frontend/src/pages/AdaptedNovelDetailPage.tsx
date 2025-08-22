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
  Descriptions,
  InputNumber
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
import { chapterNovelApi, ChapterNovelResponse, ChapterInfo } from '../utils/api'

const { Title, Text, Paragraph } = Typography

interface LegacyChapter {
  id: number
  chapter_number: number
  title: string
  content: string
  summary: string
  status: string
  is_generating: boolean
}

interface LegacyNovel {
  id: number
  title: string
  outline: string
  content: string
  category_id: number
  status: string
  total_chapters: number
  completed_chapters: number
  chapters: LegacyChapter[]
}

const AdaptedNovelDetailPage: React.FC = () => {
  const [novel, setNovel] = useState<LegacyNovel | ChapterNovelResponse | null>(null)
  const [chapters, setChapters] = useState<(LegacyChapter | ChapterInfo)[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState<number | null>(null)
  const [outlineVisible, setOutlineVisible] = useState(false)
  const [targetLength, setTargetLength] = useState(2000)
  const [isChapterNovel, setIsChapterNovel] = useState(false)
  const navigate = useNavigate()
  const { novelId } = useParams<{ novelId: string }>()

  useEffect(() => {
    if (novelId) {
      fetchNovel(novelId)
    }
  }, [novelId])

  const fetchNovel = async (id: string) => {
    try {
      // 首先尝试作为章节式小说获取
      try {
        const chapterNovel = await chapterNovelApi.getNovel(id)
        const chapterList = await chapterNovelApi.getChapters(id)
        setNovel(chapterNovel)
        setChapters(chapterList)
        setIsChapterNovel(true)
      } catch {
        // 如果失败，尝试作为传统小说获取
        const response = await fetch(`/api/novels/${id}`)
        if (response.ok) {
          const legacyNovel = await response.json()
          setNovel(legacyNovel)
          setChapters(legacyNovel.chapters || [])
          setIsChapterNovel(false)
        } else {
          throw new Error('小说不存在')
        }
      }
    } catch (error) {
      message.error(error instanceof Error ? error.message : '获取小说详情失败')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateChapter = async (chapterNumber: number) => {
    if (!novel) return
    
    setGenerating(chapterNumber)
    try {
      if (isChapterNovel) {
        // 章节式小说生成
        await chapterNovelApi.generateChapter(
          novel.id as string,
          chapterNumber,
          { target_length: targetLength }
        )
        message.success(`第${chapterNumber}章生成成功！`)
        await fetchNovel(novel.id as string)
      } else {
        // 传统小说生成（保持原有逻辑）
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
          await fetchNovel(novel.id as string)
        } else {
          const error = await response.json()
          message.error(error.detail || `第${chapterNumber}章生成失败`)
        }
      }
    } catch (error) {
      message.error(error instanceof Error ? error.message : '生成章节失败')
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

  const getChapterStatusIcon = (chapter: LegacyChapter | ChapterInfo) => {
    const isGenerating = 'is_generating' in chapter ? chapter.is_generating : chapter.status === 'writing'
    
    if (isGenerating || generating === chapter.chapter_number) {
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

  const getChapterStatusText = (chapter: LegacyChapter | ChapterInfo) => {
    const isGenerating = 'is_generating' in chapter ? chapter.is_generating : chapter.status === 'writing'
    
    if (isGenerating || generating === chapter.chapter_number) {
      return '生成中'
    }
    
    switch (chapter.status) {
      case 'completed':
        return '已完成'
      case 'planned':
        return '待生成'
      case 'failed':
        return '生成失败'
      case 'writing':
        return '创作中'
      default:
        return '未知'
    }
  }

  const getChapterStatusColor = (chapter: LegacyChapter | ChapterInfo) => {
    const isGenerating = 'is_generating' in chapter ? chapter.is_generating : chapter.status === 'writing'
    
    if (isGenerating || generating === chapter.chapter_number) {
      return 'processing'
    }
    
    switch (chapter.status) {
      case 'completed':
        return 'success'
      case 'planned':
        return 'warning'
      case 'failed':
        return 'error'
      case 'writing':
        return 'processing'
      default:
        return 'default'
    }
  }

  const canGenerateChapter = (chapter: LegacyChapter | ChapterInfo) => {
    const isGenerating = 'is_generating' in chapter ? chapter.is_generating : chapter.status === 'writing'
    
    if (chapter.status === 'completed' || isGenerating || generating === chapter.chapter_number) {
      return false
    }
    
    // 第一章可以直接生成
    if (chapter.chapter_number === 1) {
      return true
    }
    
    // 其他章节需要前一章已完成
    const previousChapter = chapters.find(c => c.chapter_number === chapter.chapter_number - 1)
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
  const novelOutline = isChapterNovel 
    ? (novel as ChapterNovelResponse).outline?.summary || (novel as ChapterNovelResponse).description
    : (novel as LegacyNovel).outline

  return (
    <div className="page-container">
      <Card style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div style={{ flex: 1 }}>
            <Title level={2} style={{ marginBottom: '16px' }}>
              <BookOutlined style={{ marginRight: '8px', color: '#667eea' }} />
              {novel.title}
              {isChapterNovel && (
                <Tag color="blue" style={{ marginLeft: '8px' }}>章节式</Tag>
              )}
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
                  {novel.status === 'completed' ? '已完成' : 
                   novel.status === 'outline_generated' || novel.status === 'outlined' ? '大纲已生成' : 
                   novel.status === 'writing' ? '创作中' : '进行中'}
                </Tag>
              </div>
              
              <div>
                <Button type="link" onClick={() => setOutlineVisible(true)}>
                  查看大纲
                </Button>
              </div>

              {isChapterNovel && (
                <div>
                  <Text strong>章节字数设置：</Text>
                  <InputNumber
                    min={500}
                    max={5000}
                    value={targetLength}
                    onChange={(value) => setTargetLength(value || 2000)}
                    style={{ marginLeft: '8px', width: '120px' }}
                    addonAfter="字"
                  />
                </div>
              )}
            </Space>
          </div>
        </div>
      </Card>

      <Title level={3} style={{ marginBottom: '16px' }}>章节列表</Title>
      
      <List
        grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 4 }}
        dataSource={chapters}
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
                    loading={('is_generating' in chapter ? chapter.is_generating : chapter.status === 'writing') || generating === chapter.chapter_number}
                    disabled={!canGenerateChapter(chapter)}
                    onClick={() => handleGenerateChapter(chapter.chapter_number)}
                  >
                    {(('is_generating' in chapter ? chapter.is_generating : chapter.status === 'writing') || generating === chapter.chapter_number) ? '生成中' : '生成'}
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
                    {isChapterNovel && 'word_count' in chapter && chapter.word_count > 0 && (
                      <div style={{ marginTop: '4px' }}>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {chapter.word_count} 字
                        </Text>
                      </div>
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
          <Descriptions.Item label="小说类型">
            {isChapterNovel ? '章节式小说' : '传统小说'}
          </Descriptions.Item>
          <Descriptions.Item label="总章节数">{novel.total_chapters}</Descriptions.Item>
          <Descriptions.Item label="已完成章节">{novel.completed_chapters}</Descriptions.Item>
          <Descriptions.Item label="故事大纲">
            <Paragraph>
              {novelOutline}
            </Paragraph>
          </Descriptions.Item>
          
          {isChapterNovel && (novel as ChapterNovelResponse).outline && (
            <>
              {(novel as ChapterNovelResponse).outline!.main_characters && (novel as ChapterNovelResponse).outline!.main_characters.length > 0 && (
                <Descriptions.Item label="主要角色">
                  <div>
                    {(novel as ChapterNovelResponse).outline!.main_characters.map((character, index) => (
                      <div key={index} style={{ marginBottom: '8px' }}>
                        <Text strong>{character.name}：</Text>
                        <Text>{character.description}</Text>
                      </div>
                    ))}
                  </div>
                </Descriptions.Item>
              )}
              
              {(novel as ChapterNovelResponse).outline!.chapters && (
                <Descriptions.Item label="章节规划">
                  <div>
                    {(novel as ChapterNovelResponse).outline!.chapters.map((chapter, index) => (
                      <div key={index} style={{ marginBottom: '8px' }}>
                        <Text strong>第{chapter.number}章 {chapter.title}：</Text>
                        <br />
                        <Text type="secondary">{chapter.summary}</Text>
                      </div>
                    ))}
                  </div>
                </Descriptions.Item>
              )}
            </>
          )}
          
          {!isChapterNovel && (novel as LegacyNovel).content && (
            <Descriptions.Item label="主角设定">
              <Paragraph>
                {(novel as LegacyNovel).content}
              </Paragraph>
            </Descriptions.Item>
          )}
        </Descriptions>
      </Modal>
    </div>
  )
}

export default AdaptedNovelDetailPage
