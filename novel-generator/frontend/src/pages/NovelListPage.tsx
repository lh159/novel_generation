import React, { useState, useEffect } from 'react'
import { Card, List, Button, Tag, Space, Typography, Empty, Spin, message, Tabs } from 'antd'
import { BookOutlined, EyeOutlined, PlayCircleOutlined, PlusOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { chapterNovelApi, ChapterNovelResponse } from '../utils/api'

const { Title, Text } = Typography

interface Novel {
  id: number
  title: string
  outline: string
  category_id: number
  status: string
  total_chapters: number
  completed_chapters: number
}

interface ChapterNovel extends ChapterNovelResponse {
  // 扩展接口以兼容现有代码
}

const NovelListPage: React.FC = () => {
  const [novels, setNovels] = useState<Novel[]>([])
  const [chapterNovels, setChapterNovels] = useState<ChapterNovel[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('legacy')
  const navigate = useNavigate()

  useEffect(() => {
    fetchNovels()
    fetchChapterNovels()
  }, [])

  const fetchNovels = async () => {
    try {
      const response = await fetch('/api/novels/')
      if (response.ok) {
        const data = await response.json()
        setNovels(data)
      } else {
        message.error('获取传统小说列表失败')
      }
    } catch (error) {
      message.error('网络错误，请重试')
      console.error('Fetch novels error:', error)
    }
  }

  const fetchChapterNovels = async () => {
    try {
      const data = await chapterNovelApi.getNovels()
      setChapterNovels(data)
    } catch (error) {
      console.error('Fetch chapter novels error:', error)
      // 章节式小说获取失败不显示错误，因为可能是新功能
    } finally {
      setLoading(false)
    }
  }

  const handleViewNovel = (novelId: number | string) => {
    navigate(`/novels/${novelId}`)
  }

  const handleRoleplay = (novelId: number | string) => {
    navigate(`/roleplay/${novelId}`)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success'
      case 'outline_generated':
      case 'outlined':
        return 'processing'
      case 'draft':
      case 'planning':
        return 'default'
      case 'generating':
      case 'writing':
        return 'processing'
      default:
        return 'default'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return '已完成'
      case 'outline_generated':
      case 'outlined':
        return '大纲已生成'
      case 'draft':
        return '草稿'
      case 'planning':
        return '规划中'
      case 'generating':
      case 'writing':
        return '创作中'
      default:
        return '未知'
    }
  }

  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>加载中...</div>
      </div>
    )
  }

  const renderNovelList = (novelList: Novel[], emptyText: string, createPath: string) => (
    novelList.length === 0 ? (
      <Empty
        description={emptyText}
        style={{ margin: '100px 0' }}
      >
        <Button type="primary" onClick={() => navigate(createPath)}>
          开始创作第一篇小说
        </Button>
      </Empty>
    ) : (
      <List
        grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 3 }}
        dataSource={novelList}
        renderItem={(novel) => (
          <List.Item>
            <Card
              hoverable
              actions={[
                <Button 
                  type="default" 
                  icon={<EyeOutlined />}
                  onClick={() => handleViewNovel(novel.id)}
                >
                  查看详情
                </Button>,
                <Button 
                  type="primary" 
                  icon={<PlayCircleOutlined />}
                  onClick={() => handleRoleplay(novel.id)}
                  disabled={novel.completed_chapters === 0}
                >
                  开始体验
                </Button>
              ]}
            >
              <Card.Meta
                avatar={<BookOutlined style={{ fontSize: '2rem', color: '#667eea' }} />}
                title={
                  <Space>
                    <span>{novel.title}</span>
                    <Tag color={getStatusColor(novel.status)}>
                      {getStatusText(novel.status)}
                    </Tag>
                  </Space>
                }
                description={
                  <div>
                    <div style={{ marginBottom: '8px' }}>
                      <Text type="secondary">
                        进度: {novel.completed_chapters}/{novel.total_chapters} 章
                      </Text>
                    </div>
                    <div style={{ marginTop: '8px' }}>
                      <Text ellipsis>{novel.outline}</Text>
                    </div>
                  </div>
                }
              />
            </Card>
          </List.Item>
        )}
      />
    )
  )

  const renderChapterNovelList = (novelList: ChapterNovel[]) => (
    novelList.length === 0 ? (
      <Empty
        description="暂无章节式小说"
        style={{ margin: '100px 0' }}
      >
        <Button type="primary" onClick={() => navigate('/novels/chapter/create')}>
          创建章节式小说
        </Button>
      </Empty>
    ) : (
      <List
        grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 3 }}
        dataSource={novelList}
        renderItem={(novel) => (
          <List.Item>
            <Card
              hoverable
              actions={[
                <Button 
                  type="default" 
                  icon={<EyeOutlined />}
                  onClick={() => handleViewNovel(novel.id)}
                >
                  查看详情
                </Button>,
                <Button 
                  type="primary" 
                  icon={<PlayCircleOutlined />}
                  onClick={() => handleRoleplay(novel.id)}
                  disabled={novel.completed_chapters === 0}
                >
                  开始体验
                </Button>
              ]}
            >
              <Card.Meta
                avatar={<BookOutlined style={{ fontSize: '2rem', color: '#667eea' }} />}
                title={
                  <Space>
                    <span>{novel.title}</span>
                    <Tag color={getStatusColor(novel.status)}>
                      {getStatusText(novel.status)}
                    </Tag>
                  </Space>
                }
                description={
                  <div>
                    <div style={{ marginBottom: '8px' }}>
                      <Text type="secondary">
                        进度: {novel.completed_chapters}/{novel.total_chapters} 章
                      </Text>
                    </div>
                    <div style={{ marginTop: '8px' }}>
                      <Text ellipsis>
                        {novel.outline?.summary || novel.description || '暂无描述'}
                      </Text>
                    </div>
                  </div>
                }
              />
            </Card>
          </List.Item>
        )}
      />
    )
  )

  return (
    <div className="page-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <Title level={2} style={{ margin: 0 }}>
          小说列表
        </Title>
        <Space>
          <Button 
            type="default" 
            icon={<PlusOutlined />}
            onClick={() => navigate('/upload')}
          >
            传统小说
          </Button>
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => navigate('/novels/chapter/create')}
          >
            章节式小说
          </Button>
        </Space>
      </div>

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: 'legacy',
            label: `传统小说 (${novels.length})`,
            children: renderNovelList(novels, '暂无传统小说', '/upload')
          },
          {
            key: 'chapter',
            label: `章节式小说 (${chapterNovels.length})`,
            children: renderChapterNovelList(chapterNovels)
          }
        ]}
      />

      <Card style={{ marginTop: '24px' }}>
        <Title level={4}>使用说明</Title>
        <div style={{ lineHeight: '1.8' }}>
          <p><strong>小说状态说明：</strong></p>
          <ul>
            <li><Tag color="success">已完成</Tag> - 小说所有章节已生成完成</li>
            <li><Tag color="processing">大纲已生成</Tag> - 小说大纲已生成，可以开始生成章节</li>
            <li><Tag color="processing">生成中</Tag> - 小说正在生成中，请稍候</li>
            <li><Tag color="default">草稿</Tag> - 小说为草稿状态</li>
          </ul>
          
          <p><strong>操作说明：</strong></p>
          <ul>
          <li>点击"查看详情"查看小说大纲和章节列表</li>
            <li>在详情页面可以逐章生成内容，避免生成超时</li>
            <li>点击"开始体验"进入主角扮演模式（需要至少一章内容）</li>
            <li>章节采用分段生成，包含前情提要和对白重点</li>
            <li>每章生成后会自动总结，为下一章提供前情提要</li>
            <li>点击"开始体验"按钮进入主角扮演模式</li>
            <li>在主角扮演模式中，您将扮演小说主角</li>
            <li>阅读主角台词后点击"确认读完"继续剧情</li>
            <li>其他角色对白会自动推进</li>
          </ul>
        </div>
      </Card>
    </div>
  )
}

export default NovelListPage
