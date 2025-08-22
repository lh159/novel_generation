import React, { useState, useEffect } from 'react'
import { 
  Card, 
  Typography, 
  Button, 
  Space, 
  Divider, 
  Tag, 
  Empty, 
  Spin, 
  message,
  List,

  Breadcrumb
} from 'antd'
import { 
  BookOutlined, 
  UserOutlined, 
  LeftOutlined, 
  RightOutlined,
  HomeOutlined,
  PlayCircleOutlined,
  MessageOutlined
} from '@ant-design/icons'
import { useNavigate, useParams } from 'react-router-dom'

const { Title, Text, Paragraph } = Typography

interface Dialogue {
  id: number
  speaker: string
  text: string
  required_chars_used: string[]
  is_protagonist: boolean
  sequence_order: number
}

interface Chapter {
  id: number
  novel_id: number
  chapter_number: number
  title: string
  content: string
  summary: string
  status: string
  is_generating: boolean
  dialogues: Dialogue[]
}

const ChapterViewPage: React.FC = () => {
  const [chapter, setChapter] = useState<Chapter | null>(null)
  const [novelTitle, setNovelTitle] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const { novelId, chapterNumber } = useParams<{ novelId: string; chapterNumber: string }>()

  useEffect(() => {
    if (novelId && chapterNumber) {
      fetchChapter(novelId, parseInt(chapterNumber))
    }
  }, [novelId, chapterNumber])

  const fetchChapter = async (novelId: string, chapterNum: number) => {
    try {
      const response = await fetch(`/api/novels-v2/${novelId}/chapters/${chapterNum}`)
      if (response.ok) {
        const data = await response.json()
        setChapter(data)
        
        // 获取小说标题
        const novelResponse = await fetch(`/api/novels-v2/${novelId}`)
        if (novelResponse.ok) {
          const novelData = await novelResponse.json()
          setNovelTitle(novelData.title)
        }
      } else {
        message.error('获取章节内容失败')
      }
    } catch (error) {
      message.error('网络错误，请重试')
      console.error('Fetch chapter error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePreviousChapter = () => {
    if (chapter && chapter.chapter_number > 1) {
      navigate(`/novels/${novelId}/chapters/${chapter.chapter_number - 1}`)
    }
  }

  const handleNextChapter = () => {
    if (chapter) {
      navigate(`/novels/${novelId}/chapters/${chapter.chapter_number + 1}`)
    }
  }

  const handleRoleplay = () => {
    navigate(`/roleplay/${novelId}/${chapterNumber}`)
  }

  const getSpeakerIcon = (dialogue: Dialogue) => {
    return dialogue.is_protagonist ? (
      <UserOutlined style={{ color: '#667eea' }} />
    ) : (
      <MessageOutlined style={{ color: '#52c41a' }} />
    )
  }



  if (loading) {
    return (
      <div className="page-container" style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>加载中...</div>
      </div>
    )
  }

  if (!chapter) {
    return (
      <div className="page-container">
        <Empty description="章节不存在" />
      </div>
    )
  }

  return (
    <div className="page-container">
      <Card style={{ marginBottom: '24px' }}>
        <Breadcrumb style={{ marginBottom: '16px' }}>
          <Breadcrumb.Item href="/">
            <HomeOutlined />
            首页
          </Breadcrumb.Item>
          <Breadcrumb.Item href="/novels">
            小说列表
          </Breadcrumb.Item>
          <Breadcrumb.Item href={`/novels/${novelId}`}>
            {novelTitle}
          </Breadcrumb.Item>
          <Breadcrumb.Item>
            第{chapter.chapter_number}章
          </Breadcrumb.Item>
        </Breadcrumb>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Title level={2} style={{ marginBottom: '8px' }}>
              <BookOutlined style={{ marginRight: '8px', color: '#667eea' }} />
              {chapter.title}
            </Title>
            <Text type="secondary">第{chapter.chapter_number}章</Text>
          </div>
          
          <Button 
            type="primary" 
            icon={<PlayCircleOutlined />}
            onClick={handleRoleplay}
          >
            体验此章节
          </Button>
        </div>
      </Card>

      <Card style={{ marginBottom: '24px', minHeight: '400px' }}>
        <Title level={4} style={{ marginBottom: '20px', borderBottom: '2px solid #f0f0f0', paddingBottom: '12px' }}>
          <BookOutlined style={{ marginRight: '8px', color: '#667eea' }} />
          章节内容
        </Title>
        <div style={{ 
          backgroundColor: '#fafafa', 
          padding: '24px', 
          borderRadius: '8px',
          border: '1px solid #e8e8e8',
          maxHeight: '600px',
          overflowY: 'auto'
        }}>
          <Paragraph style={{ 
            fontSize: '17px', 
            lineHeight: '2.2', 
            textAlign: 'justify',
            textIndent: '2em',
            marginBottom: '0',
            color: '#333',
            whiteSpace: 'pre-wrap'
          }}>
            {chapter.content}
          </Paragraph>
        </div>
        
        {chapter.summary && (
          <>
            <Divider style={{ margin: '24px 0' }} />
            <Title level={5} style={{ color: '#666' }}>
              📝 章节总结
            </Title>
            <div style={{ 
              backgroundColor: '#f6f8fa', 
              padding: '16px', 
              borderRadius: '6px',
              borderLeft: '4px solid #667eea'
            }}>
              <Paragraph style={{ 
                fontStyle: 'italic', 
                color: '#666',
                fontSize: '15px',
                marginBottom: '0',
                lineHeight: '1.6'
              }}>
                {chapter.summary}
              </Paragraph>
            </div>
          </>
        )}
      </Card>

      {chapter.dialogues && chapter.dialogues.length > 0 && (
        <Card style={{ marginBottom: '24px' }}>
          <Title level={4} style={{ marginBottom: '20px', borderBottom: '2px solid #f0f0f0', paddingBottom: '12px' }}>
            💬 对白详情
          </Title>
          <div style={{ 
            backgroundColor: '#fafafa', 
            padding: '16px', 
            borderRadius: '8px',
            border: '1px solid #e8e8e8',
            maxHeight: '500px',
            overflowY: 'auto'
          }}>
            <List
              dataSource={chapter.dialogues}
              renderItem={(dialogue, index) => (
                <List.Item style={{ 
                  padding: '16px 0', 
                  borderBottom: index < chapter.dialogues.length - 1 ? '1px solid #e8e8e8' : 'none',
                  backgroundColor: 'white',
                  margin: '8px 0',
                  borderRadius: '6px',
                  paddingLeft: '16px',
                  paddingRight: '16px'
                }}>
                  <div style={{ width: '100%' }}>
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        backgroundColor: dialogue.is_protagonist ? '#e6f7ff' : '#f6ffed',
                        padding: '4px 12px',
                        borderRadius: '16px',
                        border: `1px solid ${dialogue.is_protagonist ? '#91d5ff' : '#b7eb8f'}`
                      }}>
                        {getSpeakerIcon(dialogue)}
                        <span style={{ marginLeft: '6px', fontWeight: '500', fontSize: '14px' }}>
                          {dialogue.is_protagonist ? '主角' : dialogue.speaker}
                        </span>
                      </div>
                      {dialogue.required_chars_used && dialogue.required_chars_used.length > 0 && (
                        <div style={{ marginLeft: '12px' }}>
                          {dialogue.required_chars_used.map((char, charIndex) => (
                            <Tag key={charIndex} color="volcano" style={{ marginRight: '4px', fontSize: '12px' }}>
                              {char}
                            </Tag>
                          ))}
                        </div>
                      )}
                    </div>
                    <div style={{ 
                      backgroundColor: '#f9f9f9',
                      padding: '12px 16px',
                      borderRadius: '8px',
                      borderLeft: `4px solid ${dialogue.is_protagonist ? '#667eea' : '#52c41a'}`,
                      marginLeft: '8px'
                    }}>
                      <Paragraph style={{ 
                        marginBottom: 0, 
                        fontSize: '15px',
                        lineHeight: '1.6',
                        color: '#333'
                      }}>
                        "{dialogue.text}"
                      </Paragraph>
                    </div>
                  </div>
                </List.Item>
              )}
            />
          </div>
        </Card>
      )}

      <Card style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        border: 'none'
      }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Button 
            size="large"
            icon={<LeftOutlined />}
            disabled={chapter.chapter_number <= 1}
            onClick={handlePreviousChapter}
            style={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              border: 'none',
              fontWeight: '500'
            }}
          >
            上一章
          </Button>
          
          <Space size="middle">
            <Button 
              size="large"
              onClick={() => navigate(`/novels/${novelId}`)}
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                border: 'none',
                fontWeight: '500'
              }}
            >
              返回章节列表
            </Button>
            <Button 
              type="primary" 
              size="large"
              icon={<PlayCircleOutlined />}
              onClick={handleRoleplay}
              style={{ 
                backgroundColor: '#52c41a',
                borderColor: '#52c41a',
                fontWeight: '500',
                boxShadow: '0 2px 8px rgba(82, 196, 26, 0.3)'
              }}
            >
              体验此章节
            </Button>
          </Space>
          
          <Button 
            size="large"
            icon={<RightOutlined />}
            onClick={handleNextChapter}
            style={{ 
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              border: 'none',
              fontWeight: '500'
            }}
          >
            下一章
          </Button>
        </Space>
      </Card>
    </div>
  )
}

export default ChapterViewPage
