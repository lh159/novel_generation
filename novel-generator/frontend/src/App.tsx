import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import zhCN from 'antd/locale/zh_CN'

import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import MaterialUploadPage from './pages/MaterialUploadPage'
import NovelListPage from './pages/NovelListPage'
import AdaptedNovelDetailPage from './pages/AdaptedNovelDetailPage'
import ChapterViewPage from './pages/ChapterViewPage'
import ProtagonistRoleplayPage from './pages/ProtagonistRoleplayPage'
import ChapterNovelCreatePage from './pages/ChapterNovelCreatePage'

import './App.css'

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <div className="app">
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/upload" element={<MaterialUploadPage />} />
            <Route path="/novels" element={<NovelListPage />} />
            <Route path="/novels/chapter/create" element={<ChapterNovelCreatePage />} />
            <Route path="/novels/:novelId" element={<AdaptedNovelDetailPage />} />
            <Route path="/novels/:novelId/chapters/:chapterNumber" element={<ChapterViewPage />} />
            <Route path="/roleplay/:novelId" element={<ProtagonistRoleplayPage />} />
            <Route path="/roleplay/:novelId/:chapterNumber" element={<ProtagonistRoleplayPage />} />
          </Routes>
        </Layout>
      </div>
    </ConfigProvider>
  )
}

export default App
