import {AbsoluteFill} from 'remotion';
import {DeepSeaBackground} from './DeepSeaBackground';

export const CoverStill = () => {
  return (
    <AbsoluteFill>
      <DeepSeaBackground />
      <AbsoluteFill
        style={{
          alignItems: 'center',
          justifyContent: 'center',
          paddingTop: 24,
          color: '#fff6c0',
          textShadow: '0 7px 28px rgba(0, 0, 0, 0.72)',
          fontFamily: '"Microsoft YaHei", "PingFang SC", sans-serif',
        }}
      >
        <div style={{fontSize: 88, fontWeight: 900, letterSpacing: 0}}>
          泡泡上升
        </div>
        <div
          style={{
            marginTop: 20,
            color: '#d8f2ff',
            fontSize: 30,
            fontWeight: 600,
          }}
        >
          保护生命种子，从深海抵达陆地
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
