import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  Card, 
  Button, 
  Avatar, 
  Space, 
  Typography, 
  Spin, 
  message, 
  Tag,
  Progress,
  Switch
} from 'antd'
import { 
  UserOutlined, 
  RobotOutlined, 
  CheckCircleOutlined,
  ArrowLeftOutlined,
  BookOutlined,
  SoundOutlined
} from '@ant-design/icons'
import PinyinText from '../components/PinyinText'

const { Title, Text } = Typography

interface PinyinChar {
  char: string
  pinyin: string
  is_chinese: boolean
}

interface Dialogue {
  speaker: string
  text: string
  required_chars_used: string[]
  is_protagonist_dialogue: boolean
  waiting_confirmation?: boolean
  message?: string
  auto_advance?: boolean
  timestamp?: string
  pinyin_text?: PinyinChar[]  // 添加拼音数据字段
}

interface NovelInfo {
  id: string
  title: string
  description?: string
  outline?: any
}

interface ChapterInfo {
  chapter_number: number
  title: string
  content: string
  word_count: number
  status: string
}

const ProtagonistRoleplayPage: React.FC = () => {
  const { novelId, chapterNumber } = useParams<{ novelId: string; chapterNumber: string }>()
  const navigate = useNavigate()
  const [currentDialogue, setCurrentDialogue] = useState<Dialogue | null>(null)
  const [dialogueHistory, setDialogueHistory] = useState<Dialogue[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [waitingConfirmation, setWaitingConfirmation] = useState(false)
  const [novelInfo, setNovelInfo] = useState<NovelInfo | null>(null)
  const [chapterInfo, setChapterInfo] = useState<ChapterInfo | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [gameStarted, setGameStarted] = useState(false)  // 控制小说是否已开始
  const [showPinyin, setShowPinyin] = useState(true)  // 控制是否显示拼音

  const dialogueEndRef = useRef<HTMLDivElement>(null)
  const autoAdvanceCountRef = useRef(0)  // 防止无限循环的计数器
  const getCurrentDialogueCallCountRef = useRef(0)  // 跟踪getCurrentDialogue调用次数
  const isInitialLoadingRef = useRef(false)  // 防止React.StrictMode重复调用
  const hasStartedGameRef = useRef(false)  // 防止游戏重复开始

  useEffect(() => {
    if (novelId && chapterNumber) {
      // 重置所有标志
      isInitialLoadingRef.current = false
      hasStartedGameRef.current = false
      autoAdvanceCountRef.current = 0
      getCurrentDialogueCallCountRef.current = 0
      console.log('🔄 页面初始化，重置所有标志')
      
      // 重置游戏状态
      setGameStarted(false)
      setCurrentDialogue(null)
      setSessionId(null)
      
      fetchNovelInfo()
      fetchChapterInfo()
    }
  }, [novelId, chapterNumber])

  useEffect(() => {
    // 当小说信息和章节信息都加载完成，且游戏已开始后，开始获取对话
    console.log('🔍 useEffect触发 - novelInfo:', !!novelInfo, 'chapterInfo:', !!chapterInfo, 'gameStarted:', gameStarted, 'currentDialogue:', !!currentDialogue, 'isLoading:', isLoading, 'hasStartedGame:', hasStartedGameRef.current)
    if (novelInfo && chapterInfo && gameStarted && !currentDialogue && !isLoading && !hasStartedGameRef.current) {
      console.log('✅ 条件满足，调用getCurrentDialogue()')
      hasStartedGameRef.current = true  // 设置标志防止重复调用
      getCurrentDialogue()
    }
  }, [novelInfo, chapterInfo, gameStarted])

  useEffect(() => {
    scrollToBottom()
  }, [dialogueHistory])

  const scrollToBottom = () => {
    dialogueEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchNovelInfo = async () => {
    try {
      const response = await fetch(`/api/novels-v2/${novelId}`)
      if (response.ok) {
        const data = await response.json()
        setNovelInfo(data)
      } else {
        message.error('获取小说信息失败')
      }
    } catch (error) {
      message.error('网络错误，请重试')
      console.error('Fetch novel error:', error)
    }
  }

  const fetchChapterInfo = async () => {
    try {
      const response = await fetch(`/api/novels-v2/${novelId}/chapters/${chapterNumber}`)
      if (response.ok) {
        const data = await response.json()
        setChapterInfo(data)
        console.log('📖 章节信息加载完成，等待用户点击开始按钮')
      } else {
        message.error('获取章节信息失败')
      }
    } catch (error) {
      message.error('网络错误，请重试')
      console.error('Fetch chapter error:', error)
    }
  }

  // 开始游戏
  const handleStartGame = () => {
    console.log('🎮 用户点击开始游戏')
    setGameStarted(true)
    // 重置标志，允许获取对话
    hasStartedGameRef.current = false
  }

    const getCurrentDialogue = async () => {
    if (!novelId) return
    
    getCurrentDialogueCallCountRef.current += 1
    const startTime = Date.now()
    console.log('📡 [时间戳] 开始获取当前对话... (第', getCurrentDialogueCallCountRef.current, '次调用)', new Date().toLocaleTimeString())
    setIsLoading(true)
    try {
      const response = await fetch('/api/chapter-dialogue/current', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          novel_id: novelId,
          chapter_number: parseInt(chapterNumber || '1'),
          session_id: sessionId
        })
      })

      if (response.ok) {
        const data = await response.json()
        const responseTime = Date.now() - startTime
        console.log('🔍 [时间戳] getCurrentDialogue 收到数据 (耗时:', responseTime + 'ms):', data)
        
        if (data.session_id && !sessionId) {
          // 新会话，设置session_id
          setSessionId(data.session_id)
        }

        console.log('📋 设置currentDialogue:', {
          speaker: data.speaker,
          text: data.text?.substring(0, 50) + '...',
          auto_advance: data.auto_advance,
          is_protagonist_dialogue: data.is_protagonist_dialogue
        })
        setCurrentDialogue(data)
        setWaitingConfirmation(data.waiting_confirmation || false)
        
        // 如果是自动推进的对话（非主角对话），延迟后将当前对话移入历史记录并获取下一个
        if (data.auto_advance && !data.is_protagonist_dialogue) {
          console.log('🚀 检测到自动推进对话:', data.text?.substring(0, 50) + '...')
          
          // 防止无限循环：限制连续自动推进次数
          autoAdvanceCountRef.current += 1
          console.log('⏰ 自动推进计数:', autoAdvanceCountRef.current)
          if (autoAdvanceCountRef.current < 20) {
            // 显示当前对话一段时间后，将其移入历史记录并获取下一个
            const delay = autoAdvanceCountRef.current === 1 ? 1500 : 2000
            console.log('⏳ [时间戳]', delay/1000 + '秒后将当前对话移入历史记录并推进...', new Date().toLocaleTimeString())
            
            // 获取当前的sessionId（可能是刚刚设置的新sessionId）
            const currentSessionId = data.session_id || sessionId
            console.log('🔑 使用的sessionId:', currentSessionId)
            
            setTimeout(() => {
              console.log('▶️ [时间戳] 将当前对话移入历史记录并获取下一个', new Date().toLocaleTimeString())
              // 将当前对话移入历史记录
              setDialogueHistory(prev => {
                console.log('📝 将当前对话移入历史记录，当前长度:', prev.length)
                return [...prev, {
                  ...data,
                  timestamp: new Date().toISOString()
                }]
              })
              // 获取下一个对话 - 使用当前的sessionId
              advanceDialogueWithSessionId(currentSessionId)
            }, delay)
          } else {
            console.warn('⚠️ 检测到连续自动推进过多，停止自动推进防止无限循环')
            autoAdvanceCountRef.current = 0
            message.warning('检测到过多连续对话，已暂停自动推进，请手动刷新页面')
          }
        } else {
          console.log('🛑 非自动推进对话，重置计数器. 是主角对话:', data.is_protagonist_dialogue)
          // 主角对话或其他情况时重置计数器
          autoAdvanceCountRef.current = 0
        }
      } else {
        message.error('获取对白失败')
      }
    } catch (error) {
      message.error('网络错误，请重试')
      console.error('Get dialogue error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const advanceDialogueWithSessionId = async (useSessionId: string) => {
    if (!useSessionId) {
      console.error('❌ advanceDialogueWithSessionId: sessionId为空')
      return
    }
    
    const startTime = Date.now()
    console.log('🔄 [时间戳] advanceDialogueWithSessionId 被调用，sessionId:', useSessionId, new Date().toLocaleTimeString())
    setIsLoading(true)
    try {
      const response = await fetch('/api/chapter-dialogue/advance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: useSessionId
        })
      })

      if (response.ok) {
        const data = await response.json()
        const responseTime = Date.now() - startTime
        console.log('🔄 [时间戳] advanceDialogueWithSessionId 收到数据 (耗时:', responseTime + 'ms):', data)
        setCurrentDialogue(data)
        setWaitingConfirmation(data.waiting_confirmation || false)
        
        // 如果又是非主角对话，继续自动推进
        if (data.auto_advance && !data.is_protagonist_dialogue) {
          console.log('🔄 advanceDialogueWithSessionId 又是自动推进对话:', data.text?.substring(0, 50) + '...')
          
          // 防止无限循环：限制连续自动推进次数
          autoAdvanceCountRef.current += 1
          console.log('🔄 advanceDialogueWithSessionId 自动推进计数:', autoAdvanceCountRef.current)
          if (autoAdvanceCountRef.current < 20) {
            console.log('🔄 advanceDialogueWithSessionId 继续自动推进...')
            setTimeout(() => {
              // 将当前对话移入历史记录
              setDialogueHistory(prev => {
                console.log('🔄 advanceDialogueWithSessionId 将当前对话移入历史记录，当前长度:', prev.length)
                return [...prev, {
                  ...data,
                  timestamp: new Date().toISOString()
                }]
              })
              // 获取下一个对话
              advanceDialogueWithSessionId(useSessionId)
            }, 3000)
          } else {
            console.warn('🔄 advanceDialogueWithSessionId 检测到连续自动推进过多，停止自动推进防止无限循环')
            autoAdvanceCountRef.current = 0
            message.warning('检测到过多连续对话，已暂停自动推进，请手动刷新页面')
          }
        } else {
          console.log('🔄 advanceDialogueWithSessionId 非自动推进对话，停止自动推进. 是主角对话:', data.is_protagonist_dialogue)
          // 如果是主角对话或章节结束，重置计数器
          autoAdvanceCountRef.current = 0
        }
        
        // 滚动到底部
        scrollToBottom()
      } else {
        message.error('推进对话失败')
        console.error('Advance dialogue failed:', response.status)
      }
    } catch (error) {
      message.error('网络错误，请重试')
      console.error('Advance dialogue error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleConfirmRead = async () => {
    if (!waitingConfirmation || !sessionId) return
    
    setIsLoading(true)
    try {
      const response = await fetch('/api/chapter-dialogue/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        // 当前主角对白添加到历史记录（只添加一次）
        if (currentDialogue && currentDialogue.is_protagonist_dialogue) {
          setDialogueHistory(prev => [...prev, {
            ...currentDialogue,
            timestamp: new Date().toISOString()
          }])
        }
        
        // 设置新对白
        setCurrentDialogue(data)
        setWaitingConfirmation(data.waiting_confirmation || false)
        
        // 重置自动推进计数器
        autoAdvanceCountRef.current = 0
        
        // 如果是自动推进的对白（非主角），开始自动推进流程
        if (data.auto_advance && !data.is_protagonist_dialogue) {
          // 添加当前非主角对话到历史记录
          setDialogueHistory(prev => [...prev, {
            ...data,
            timestamp: new Date().toISOString()
          }])
          
          // 自动推进到下一个对话
          setTimeout(() => {
            if (sessionId) {
              advanceDialogueWithSessionId(sessionId)
            }
          }, 1500)
        }
        
        // 滚动到底部
        setTimeout(scrollToBottom, 100)
      } else {
        const errorData = await response.json()
        message.error(errorData.detail || '确认失败')
      }
    } catch (error) {
      message.error('网络错误，请重试')
      console.error('Confirm dialogue error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (!novelInfo || !chapterInfo) {
    return (
      <div className="page-container" style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>加载小说信息中...</div>
      </div>
    )
  }

  return (
    <div className="page-container" style={{ 
      background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',  // 添加背景渐变
      minHeight: '100vh',
      padding: '20px'
    }}>
      <div style={{ marginBottom: '24px' }}>
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate('/novels')}
          style={{ 
            marginBottom: '16px',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
            border: 'none',
            background: 'rgba(255, 255, 255, 0.9)',
            backdropFilter: 'blur(10px)'
          }}
        >
          返回小说列表
        </Button>
        
        <Card style={{
          borderRadius: '16px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          border: 'none',
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)'
        }}>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div style={{ flex: 1 }}>
                <Title level={3} style={{ 
                  margin: 0,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}>
                  <BookOutlined style={{ marginRight: '8px', color: '#667eea' }} />
                  {novelInfo.title} - 第{chapterInfo.chapter_number}章
                </Title>
                <Title level={4} style={{ 
                  margin: '8px 0 4px 0', 
                  color: '#5a6c7d',
                  fontWeight: '600'
                }}>
                  {chapterInfo.title}
                </Title>
                <Text type="secondary" style={{ fontSize: '14px' }}>
                  字数: {chapterInfo.word_count} | 状态: {chapterInfo.status}
                </Text>
              </div>
              
              {/* 拼音显示控制器 */}
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '8px',
                padding: '12px 16px',
                background: 'rgba(102, 126, 234, 0.05)',
                borderRadius: '8px',
                border: '1px solid rgba(102, 126, 234, 0.1)'
              }}>
                <SoundOutlined style={{ color: '#667eea' }} />
                <Text style={{ marginRight: '8px', color: '#667eea', fontWeight: 'medium' }}>
                  拼音标注
                </Text>
                <Switch
                  checked={showPinyin}
                  onChange={setShowPinyin}
                  size="small"
                  style={{
                    backgroundColor: showPinyin ? '#667eea' : undefined
                  }}
                />
              </div>
            </div>
            
            <Progress 
              percent={Math.round((dialogueHistory.length / 10) * 100)}  // 假设每章最多10个对话
              size="small" 
              status="active"
              strokeColor={{
                '0%': '#667eea',
                '100%': '#764ba2',
              }}
              trailColor="rgba(102, 126, 234, 0.1)"
              style={{
                marginTop: '8px'
              }}
            />
          </Space>
        </Card>
      </div>

      {/* 开始游戏按钮 */}
      {!gameStarted && novelInfo && chapterInfo && (
        <Card style={{ 
          textAlign: 'center', 
          marginBottom: '24px', 
          padding: '60px 40px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          border: 'none',
          borderRadius: '16px',
          boxShadow: '0 8px 32px rgba(102, 126, 234, 0.3)'
        }}>
          <div style={{ marginBottom: '24px' }}>
            <div style={{ 
              fontSize: '24px', 
              fontWeight: 'bold', 
              color: 'white',
              marginBottom: '12px'
            }}>
              🎭 准备开始角色扮演
            </div>
            <div style={{ 
              fontSize: '16px', 
              color: 'rgba(255, 255, 255, 0.9)',
              lineHeight: '1.6'
            }}>
              你将扮演小说中的主角，与其他角色进行对话互动<br/>
              请仔细阅读每段对话，体验沉浸式的故事情节
            </div>
          </div>
          <Button
            type="primary"
            size="large"
            onClick={handleStartGame}
            style={{
              fontSize: '18px',
              padding: '16px 48px',
              height: 'auto',
              borderRadius: '12px',
              background: 'rgba(255, 255, 255, 0.2)',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              color: 'white',
              fontWeight: 'bold',
              backdropFilter: 'blur(10px)',
              boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)',
              transform: 'translateY(0)',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(0, 0, 0, 0.3)'
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.2)'
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)'
            }}
          >
            🚀 开始游戏
          </Button>
        </Card>
      )}

      {/* 加载状态 */}
      {isLoading && !currentDialogue && gameStarted && (
        <Card style={{ textAlign: 'center', marginBottom: '24px', padding: '40px' }}>
          <Spin size="large" />
          <div style={{ marginTop: '16px', fontSize: '16px', color: '#666' }}>
            正在加载剧情内容...
          </div>
        </Card>
      )}

      {/* 历史对话记录 */}
      {gameStarted && dialogueHistory.map((dialogue, index) => (
        <Card
          key={`history-${index}-${dialogue.timestamp}`}
          className="dialogue-card history-dialogue"
          style={{ 
            marginBottom: '20px',
            border: 'none',
            borderRadius: '16px',
            boxShadow: dialogue.is_protagonist_dialogue 
              ? '0 8px 32px rgba(102, 126, 234, 0.15)' 
              : '0 8px 32px rgba(0, 0, 0, 0.08)',
            background: dialogue.is_protagonist_dialogue 
              ? 'linear-gradient(135deg, #f5f7ff 0%, #ffffff 100%)' 
              : 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.3s ease',
            transform: 'translateY(0)',
            opacity: 0.85,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)'
            e.currentTarget.style.opacity = '1'
            e.currentTarget.style.boxShadow = dialogue.is_protagonist_dialogue 
              ? '0 12px 40px rgba(102, 126, 234, 0.25)' 
              : '0 12px 40px rgba(0, 0, 0, 0.12)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)'
            e.currentTarget.style.opacity = '0.85'
            e.currentTarget.style.boxShadow = dialogue.is_protagonist_dialogue 
              ? '0 8px 32px rgba(102, 126, 234, 0.15)' 
              : '0 8px 32px rgba(0, 0, 0, 0.08)'
          }}
        >
          <Space direction="vertical" size={16} style={{ width: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <Avatar
                icon={dialogue.is_protagonist_dialogue ? <UserOutlined /> : <RobotOutlined />}
                size={56}
                style={{ 
                  backgroundColor: dialogue.is_protagonist_dialogue ? '#667eea' : '#52c41a',
                  border: '3px solid rgba(255, 255, 255, 0.8)',
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)'
                }}
              />
              <div>
                <div style={{ 
                  fontSize: '1.1rem', 
                  fontWeight: '700', 
                  marginBottom: '4px',
                  background: dialogue.is_protagonist_dialogue 
                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                    : 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}>
                  {dialogue.is_protagonist_dialogue ? '你 (主角)' : dialogue.speaker}
                </div>
                <Tag 
                  style={{
                    background: dialogue.is_protagonist_dialogue 
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                      : 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '16px',
                    padding: '4px 12px',
                    fontWeight: '600',
                    fontSize: '12px'
                  }}
                >
                  {dialogue.is_protagonist_dialogue ? '✨ 主角' : '🎭 配角'}
                </Tag>
              </div>
            </div>
            
            <div style={{ 
              fontSize: '1rem', 
              lineHeight: dialogue.is_protagonist_dialogue && dialogue.pinyin_text && showPinyin ? '3.2' : '1.6', 
              textAlign: 'left',
              padding: '16px',
              background: dialogue.is_protagonist_dialogue ? 'rgba(102, 126, 234, 0.05)' : 'rgba(0, 0, 0, 0.02)',
              borderRadius: '8px',
              border: dialogue.is_protagonist_dialogue ? '1px solid rgba(102, 126, 234, 0.1)' : '1px solid rgba(0, 0, 0, 0.06)',
              wordSpacing: dialogue.is_protagonist_dialogue && dialogue.pinyin_text && showPinyin ? '0.2em' : 'normal'
            }}>
              {dialogue.is_protagonist_dialogue && dialogue.pinyin_text ? (
                <PinyinText 
                  pinyinData={dialogue.pinyin_text}
                  showPinyin={showPinyin}
                />
              ) : (
                dialogue.text
              )}
            </div>
          </Space>
        </Card>
      ))}

      {/* 当前对白显示区域 */}
      {gameStarted && currentDialogue && (
        <Card
          key={`current-${currentDialogue.timestamp || Date.now()}`}
          className={`dialogue-card current-dialogue ${currentDialogue.is_protagonist_dialogue ? 'protagonist-dialogue' : 'other-dialogue'}`}
          style={{ 
            marginBottom: '24px',
            border: 'none',
            borderRadius: '20px',
            boxShadow: currentDialogue.is_protagonist_dialogue 
              ? '0 12px 40px rgba(102, 126, 234, 0.25)' 
              : '0 12px 40px rgba(0, 0, 0, 0.15)',
            background: currentDialogue.is_protagonist_dialogue 
              ? 'linear-gradient(135deg, #f5f7ff 0%, #ffffff 100%)' 
              : 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
            backdropFilter: 'blur(15px)',
            position: 'relative'
          }}
        >
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <Avatar
                icon={currentDialogue.is_protagonist_dialogue ? <UserOutlined /> : <RobotOutlined />}
                size={72}
                style={{ 
                  backgroundColor: currentDialogue.is_protagonist_dialogue ? '#667eea' : '#52c41a',
                  border: '4px solid rgba(255, 255, 255, 0.8)',
                  boxShadow: '0 8px 24px rgba(0, 0, 0, 0.15)'
                }}
              />
              <div>
                <div style={{ 
                  fontSize: '1.3rem', 
                  fontWeight: '700', 
                  marginBottom: '6px',
                  background: currentDialogue.is_protagonist_dialogue 
                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                    : 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}>
                  {currentDialogue.is_protagonist_dialogue ? '你 (主角)' : currentDialogue.speaker}
                </div>
                <Tag 
                  style={{
                    background: currentDialogue.is_protagonist_dialogue 
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                      : 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '16px',
                    padding: '4px 12px',
                    fontWeight: '600',
                    fontSize: '12px'
                  }}
                >
                  {currentDialogue.is_protagonist_dialogue ? '✨ 主角' : '🎭 配角'}
                </Tag>
              </div>
            </div>
            
            <div style={{ 
              fontSize: '1.1rem', 
              lineHeight: currentDialogue.is_protagonist_dialogue && currentDialogue.pinyin_text && showPinyin ? '3.2' : '1.8', 
              textAlign: 'left',
              padding: '20px',
              background: currentDialogue.is_protagonist_dialogue ? 'rgba(102, 126, 234, 0.05)' : 'rgba(0, 0, 0, 0.02)',
              borderRadius: '12px',
              border: currentDialogue.is_protagonist_dialogue ? '1px solid rgba(102, 126, 234, 0.1)' : '1px solid rgba(0, 0, 0, 0.06)',
              wordSpacing: currentDialogue.is_protagonist_dialogue && currentDialogue.pinyin_text && showPinyin ? '0.2em' : 'normal'
            }}>
              {currentDialogue.is_protagonist_dialogue && currentDialogue.pinyin_text ? (
                <PinyinText 
                  pinyinData={currentDialogue.pinyin_text}
                  showPinyin={showPinyin}
                  style={{ fontSize: '1.1rem' }}
                />
              ) : (
                currentDialogue.text
              )}
            </div>
            
            {currentDialogue.required_chars_used && currentDialogue.required_chars_used.length > 0 && (
              <div style={{ background: '#f6f8fa', padding: '12px', borderRadius: '8px' }}>
                <Text strong>使用汉字: </Text>
                <Space wrap>
                  {currentDialogue.required_chars_used.map((char, index) => (
                    <Tag key={index} color="blue">{char}</Tag>
                  ))}
                </Space>
              </div>
            )}
            
            {currentDialogue.waiting_confirmation && (
              <div style={{ 
                background: 'linear-gradient(135deg, #e6f7ff 0%, #f0f9ff 100%)', 
                padding: '20px', 
                borderRadius: '12px', 
                border: '2px solid #91d5ff',
                textAlign: 'center',
                boxShadow: '0 2px 8px rgba(24, 144, 255, 0.15)'
              }}>
                <Text strong style={{ color: '#1890ff', fontSize: '16px' }}>
                  {currentDialogue.message || '请阅读完主角台词后点击下方按钮继续剧情'}
                </Text>
              </div>
            )}
          </Space>
        </Card>
      )}

      {/* 确认按钮 */}
      {gameStarted && waitingConfirmation && (
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <Button
            type="primary"
            size="large"
            onClick={handleConfirmRead}
            loading={isLoading}
            icon={<CheckCircleOutlined />}
            style={{ 
              fontSize: '18px', 
              padding: '16px 40px',
              height: 'auto',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
              boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
              transform: 'translateY(0)',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)'
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.5)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)'
            }}
          >
            ✅ 确认读完，继续剧情
          </Button>
        </div>
      )}

      {/* 隐藏剧情发展记录，保持界面简洁 */}
      <div ref={dialogueEndRef} />
    </div>
  )
}

export default ProtagonistRoleplayPage
