// API 工具函数
const API_BASE_URL = 'http://localhost:8000'

// 章节式小说API接口
export interface ChapterNovelRequest {
  title: string
  chapter_count: number
  material_ids: string[]
}

export interface ChapterNovelResponse {
  id: string
  title: string
  description?: string
  outline?: {
    title: string
    summary: string
    main_characters: Array<{
      name: string
      description: string
    }>
    chapters: Array<{
      number: number
      title: string
      summary: string
    }>
  }
  total_chapters: number
  completed_chapters: number
  status: 'planning' | 'outlined' | 'writing' | 'completed'
  material_ids: string[]
  created_at: string
  updated_at: string
}

export interface ChapterInfo {
  id: string
  novel_id: string
  chapter_number: number
  title: string
  summary?: string
  content?: string
  word_count: number
  status: 'planned' | 'writing' | 'completed' | 'failed'
  created_at: string
  updated_at: string
}

export interface GenerateChapterRequest {
  target_length: number
}

// 章节式小说API
export const chapterNovelApi = {
  // 创建小说
  async createNovel(data: ChapterNovelRequest): Promise<ChapterNovelResponse> {
    const response = await fetch(`${API_BASE_URL}/api/novels-v2/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    
    if (!response.ok) {
      throw new Error(`创建小说失败: ${response.statusText}`)
    }
    
    return response.json()
  },

  // 获取小说列表
  async getNovels(skip: number = 0, limit: number = 20): Promise<ChapterNovelResponse[]> {
    const response = await fetch(`${API_BASE_URL}/api/novels-v2/?skip=${skip}&limit=${limit}`)
    
    if (!response.ok) {
      throw new Error(`获取小说列表失败: ${response.statusText}`)
    }
    
    return response.json()
  },

  // 获取小说详情
  async getNovel(novelId: string): Promise<ChapterNovelResponse> {
    const response = await fetch(`${API_BASE_URL}/api/novels-v2/${novelId}`)
    
    if (!response.ok) {
      throw new Error(`获取小说详情失败: ${response.statusText}`)
    }
    
    return response.json()
  },

  // 删除小说
  async deleteNovel(novelId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/novels-v2/${novelId}`, {
      method: 'DELETE',
    })
    
    if (!response.ok) {
      throw new Error(`删除小说失败: ${response.statusText}`)
    }
  },

  // 生成大纲
  async generateOutline(novelId: string, materialIds: string[] = []): Promise<{
    message: string
    outline: ChapterNovelResponse['outline']
  }> {
    const response = await fetch(`${API_BASE_URL}/api/novels-v2/${novelId}/outline`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        material_ids: materialIds,
        required_words: []
      }),
    })
    
    if (!response.ok) {
      throw new Error(`生成大纲失败: ${response.statusText}`)
    }
    
    return response.json()
  },

  // 获取大纲
  async getOutline(novelId: string): Promise<ChapterNovelResponse['outline']> {
    const response = await fetch(`${API_BASE_URL}/api/novels-v2/${novelId}/outline`)
    
    if (!response.ok) {
      throw new Error(`获取大纲失败: ${response.statusText}`)
    }
    
    return response.json()
  },

  // 生成章节
  async generateChapter(
    novelId: string, 
    chapterNumber: number, 
    data: GenerateChapterRequest,
    materialIds: string[] = []
  ): Promise<{
    message: string
    chapter: ChapterInfo
  }> {
    const url = new URL(`${API_BASE_URL}/api/novels-v2/${novelId}/chapters/${chapterNumber}/generate`)
    if (materialIds.length > 0) {
      materialIds.forEach(id => url.searchParams.append('material_ids', id))
    }
    
    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    
    if (!response.ok) {
      throw new Error(`生成章节失败: ${response.statusText}`)
    }
    
    return response.json()
  },

  // 获取章节列表
  async getChapters(novelId: string): Promise<ChapterInfo[]> {
    const response = await fetch(`${API_BASE_URL}/api/novels-v2/${novelId}/chapters`)
    
    if (!response.ok) {
      throw new Error(`获取章节列表失败: ${response.statusText}`)
    }
    
    return response.json()
  },

  // 获取单个章节
  async getChapter(novelId: string, chapterNumber: number): Promise<ChapterInfo> {
    const response = await fetch(`${API_BASE_URL}/api/novels-v2/${novelId}/chapters/${chapterNumber}`)
    
    if (!response.ok) {
      throw new Error(`获取章节失败: ${response.statusText}`)
    }
    
    return response.json()
  },
}

// 兼容旧API的适配器函数
export const legacyApi = {
  // 将章节式小说转换为旧格式
  convertToLegacyNovel(novel: ChapterNovelResponse): any {
    return {
      id: novel.id,
      title: novel.title,
      outline: novel.outline?.summary || novel.description || '',
      content: novel.outline?.summary || '',
      category_id: 1, // 默认分类
      status: novel.status,
      total_chapters: novel.total_chapters,
      completed_chapters: novel.completed_chapters,
      chapters: [] // 需要单独获取
    }
  },

  // 将章节信息转换为旧格式
  convertToLegacyChapter(chapter: ChapterInfo): any {
    return {
      id: chapter.id,
      chapter_number: chapter.chapter_number,
      title: chapter.title,
      content: chapter.content || '',
      summary: chapter.summary || '',
      status: chapter.status,
      is_generating: chapter.status === 'writing'
    }
  }
}
