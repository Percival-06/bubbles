import {AbsoluteFill} from 'remotion';

type EnergySeedSpriteProps = {
  size?: number;
};

export const EnergySeedSprite = ({size = 46}: EnergySeedSpriteProps) => {
  const ring = size * 1.55;
  const crystalW = size * 0.76;
  const crystalH = size * 1.35;

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
          position: 'absolute',
          width: ring,
          height: ring,
          borderRadius: '50%',
          border: `${Math.max(2, size * 0.055)}px solid rgba(224, 255, 102, 0.70)`,
          boxShadow: '0 0 10px rgba(230, 255, 100, 0.50), inset 0 0 10px rgba(255, 246, 110, 0.18)',
        }}
      />
      <div
        style={{
          position: 'relative',
          width: crystalW,
          height: crystalH,
          clipPath: 'polygon(50% 0%, 92% 30%, 82% 77%, 50% 100%, 18% 77%, 8% 30%)',
          background:
            'linear-gradient(112deg, rgba(255,255,190,0.96) 0%, rgba(255,226,76,0.95) 38%, rgba(255,246,134,0.92) 68%, rgba(242,177,48,0.88) 100%)',
          boxShadow: '0 0 14px rgba(255, 237, 83, 0.85)',
        }}
      >
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background:
              'linear-gradient(28deg, rgba(244,177,48,0.42) 0 27%, transparent 28%), linear-gradient(146deg, rgba(255,255,220,0.54) 0 34%, transparent 35%)',
          }}
        />
        <div
          style={{
            position: 'absolute',
            left: '27%',
            top: '42%',
            width: '46%',
            height: '27%',
            borderRadius: '45%',
            background: 'rgba(206, 255, 112, 0.58)',
            filter: 'blur(0.4px)',
          }}
        />
        <div
          style={{
            position: 'absolute',
            left: '30%',
            top: '32%',
            width: '52%',
            height: '5%',
            borderRadius: 999,
            background: 'rgba(255, 255, 220, 0.70)',
            transform: 'rotate(-2deg)',
          }}
        />
      </div>
      {[
        {left: '18%', top: '40%', scale: 0.11},
        {left: '78%', top: '47%', scale: 0.13},
        {left: '28%', top: '72%', scale: 0.09},
      ].map((spark, index) => (
        <div
          key={index}
          style={{
            position: 'absolute',
            left: spark.left,
            top: spark.top,
            width: size * spark.scale,
            height: size * spark.scale,
            borderRadius: '50%',
            background: 'rgba(239, 255, 211, 0.88)',
            boxShadow: '0 0 5px rgba(239, 255, 211, 0.80)',
          }}
        />
      ))}
    </AbsoluteFill>
  );
};
