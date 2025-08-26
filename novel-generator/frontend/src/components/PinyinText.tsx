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
    lineHeight: showPinyin ? '2.5' : '1.6',
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
              margin: item.is_chinese && showPinyin ? '0 1px' : '0'
            }}
          >
            {/* 拼音标注 - 只为中文字符显示 */}
            {showPinyin && item.is_chinese && item.pinyin && (
              <span
                style={{
                  position: 'absolute',
                  top: '-1.3em',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  fontSize: '0.65em',
                  color: '#666',
                  fontWeight: 'normal',
                  whiteSpace: 'nowrap',
                  zIndex: 1,
                  textAlign: 'center',
                  lineHeight: '1.2',
                  pointerEvents: 'none' // 防止拼音影响点击
                }}
              >
                {item.pinyin}
              </span>
            )}
            
            {/* 汉字本身 */}
            <span style={{ position: 'relative', zIndex: 2 }}>
              {item.char}
            </span>
          </span>
        );
      })}
    </span>
  );
};

export default PinyinText;
