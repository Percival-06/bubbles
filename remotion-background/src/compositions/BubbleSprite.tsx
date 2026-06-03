import {AbsoluteFill} from 'remotion';

type BubbleSpriteProps = {
  size?: number;
};

export const BubbleSprite = ({size = 160}: BubbleSpriteProps) => {
  const rim = Math.max(2, size * 0.022);

  return (
    <AbsoluteFill
      style={{
        alignItems: 'center',
        justifyContent: 'center',
        background: 'transparent',
      }}
    >
      <div
        style={{
          position: 'relative',
          width: size,
          height: size,
          borderRadius: '50%',
          background:
            'radial-gradient(circle at 50% 52%, rgba(255,255,255,0.34) 0%, rgba(232,246,255,0.24) 42%, rgba(210,231,244,0.40) 73%, rgba(112,139,153,0.38) 100%)',
          border: `${rim}px solid rgba(53, 72, 82, 0.64)`,
          boxShadow:
            'inset -9px -4px 8px rgba(24, 35, 43, 0.42), inset 10px 11px 16px rgba(255, 255, 255, 0.70), 0 0 3px rgba(0, 0, 0, 0.28)',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            position: 'absolute',
            left: '12%',
            top: '16%',
            width: '42%',
            height: '18%',
            borderRadius: '50%',
            background: 'rgba(255, 255, 255, 0.70)',
            transform: 'rotate(-28deg)',
            filter: 'blur(1px)',
          }}
        />
        <div
          style={{
            position: 'absolute',
            right: '12%',
            bottom: '19%',
            width: '35%',
            height: '14%',
            borderRadius: '50%',
            background: 'rgba(255, 255, 255, 0.76)',
            transform: 'rotate(-45deg)',
            filter: 'blur(0.6px)',
          }}
        />
        <div
          style={{
            position: 'absolute',
            right: '28%',
            top: '38%',
            width: '15%',
            height: '15%',
            borderRadius: '50%',
            border: `${Math.max(1, rim * 0.5)}px solid rgba(255, 255, 255, 0.46)`,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
