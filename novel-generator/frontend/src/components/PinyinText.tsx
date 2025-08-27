/**
 * 拼音文本显示组件
 * 用于在汉字上方显示拼音标注，支持开关控制
 */

import React from 'react';

interface PinyinChar {
  char: string;
  pinyin: string;
  is_chinese: boolean;
}

interface PinyinTextProps {
  pinyinData: PinyinChar[];
  showPinyin?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

const PinyinText: React.FC<PinyinTextProps> = ({
  pinyinData,
  showPinyin = true,
  className = '',
  style = {}
}) => {
  if (!pinyinData || pinyinData.length === 0) {
    return null;
  }

  const containerStyle: React.CSSProperties = {
         lineHeight: showPinyin ? '3.2' : '1.8',  // 增加行高，为拼音留出更多空间
    display: 'inline-block',
    position: 'relative',
    ...style
  };

  return (
    <span className={className} style={containerStyle}>
      {pinyinData.map((item, index) => {
        // 如果是换行符，特殊处理
        if (item.char === '\n') {
          return <br key={index} />;
        }

        return (
          <span
            key={index}
            style={{
              position: 'relative',
              display: 'inline-block',
              margin: item.is_chinese && showPinyin ? '0 10px' : '0',  // 大幅增加汉字间距，给拼音更多空间
              transition: 'all 0.2s ease',  // 添加平滑过渡
              minWidth: item.is_chinese && showPinyin ? '28px' : 'auto'  // 增加汉字最小宽度
            }}
          >
            {/* 拼音标注 - 只为中文字符显示 */}
            {showPinyin && item.is_chinese && item.pinyin && (
              <span
                style={{
                  position: 'absolute',
                  top: '-1.6em',  // 拼音稍微靠近汉字一点
                  left: '50%',
                  transform: 'translateX(-50%)',
                  fontSize: '0.7em',  // 稍微减小拼音字体，给更多空间
                  color: '#8b7355',  // 使用更温暖的颜色
                  fontWeight: '500',  // 略微加粗
                  whiteSpace: 'nowrap',
                  zIndex: 1,
                  textAlign: 'center',
                  lineHeight: '1.2',
                  pointerEvents: 'none', // 防止拼音影响点击
                  fontFamily: 'system-ui, -apple-system, sans-serif',  // 优化字体
                  textShadow: '0 1px 2px rgba(255, 255, 255, 0.8)',  // 添加微妙阴影提升可读性
                  letterSpacing: '0.3px',  // 减少字母间距，节省空间
                  maxWidth: '70px',  // 增加拼音最大宽度，减少省略号出现
                  overflow: 'visible',  // 改为可见，不隐藏溢出
                  padding: '1px 3px',  // 增加内边距
                  background: 'rgba(255, 255, 255, 0.8)',  // 增强背景透明度
                  borderRadius: '3px',  // 稍大圆角
                  boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)'  // 添加阴影防止重叠
                }}
              >
                {item.pinyin}
              </span>
            )}
            
            {/* 汉字本身 */}
            <span 
              style={{ 
                position: 'relative', 
                zIndex: 2,
                color: '#2c3e50',  // 更深的文字颜色提高对比度
                fontWeight: '500',
                display: 'inline-block',
                textAlign: 'center',
                minWidth: item.is_chinese ? '20px' : 'auto'  // 增加汉字最小宽度
              }}
            >
              {item.char}
            </span>
          </span>
        );
      })}
    </span>
  );
};

export default PinyinText;
