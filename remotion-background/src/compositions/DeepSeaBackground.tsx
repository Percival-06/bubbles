import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';

type Bubble = {
  left: number;
  size: number;
  delay: number;
  speed: number;
  opacity: number;
};

const bubbles: Bubble[] = [
  {left: 8, size: 42, delay: 18, speed: 0.82, opacity: 0.35},
  {left: 17, size: 16, delay: 84, speed: 1.18, opacity: 0.55},
  {left: 29, size: 28, delay: 42, speed: 0.92, opacity: 0.42},
  {left: 43, size: 12, delay: 124, speed: 1.35, opacity: 0.52},
  {left: 57, size: 36, delay: 6, speed: 0.78, opacity: 0.32},
  {left: 71, size: 20, delay: 68, speed: 1.1, opacity: 0.5},
  {left: 84, size: 48, delay: 104, speed: 0.74, opacity: 0.28},
  {left: 92, size: 14, delay: 28, speed: 1.28, opacity: 0.54},
];

const rays = [
  {left: -8, width: 18, rotate: -14, opacity: 0.2},
  {left: 19, width: 14, rotate: -8, opacity: 0.15},
  {left: 54, width: 20, rotate: 11, opacity: 0.13},
  {left: 78, width: 13, rotate: 7, opacity: 0.1},
];

export const DeepSeaBackground = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const loopFrame = durationInFrames > 1 ? frame % durationInFrames : 45;
  const slowWave = Math.sin(loopFrame / 34);

  return (
    <AbsoluteFill
      style={{
        overflow: 'hidden',
        background:
          'linear-gradient(180deg, #12436f 0%, #08274c 42%, #020814 100%)',
      }}
    >
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(circle at 21% 25%, rgba(98, 174, 214, 0.28), transparent 22%), radial-gradient(circle at 53% 80%, rgba(38, 160, 149, 0.18), transparent 26%), linear-gradient(90deg, rgba(0,0,0,0.46), transparent 30%, transparent 68%, rgba(0,0,0,0.52))',
        }}
      />
      {rays.map((ray, index) => (
        <div
          key={index}
          style={{
            position: 'absolute',
            top: -40,
            left: `${ray.left + slowWave * (index % 2 === 0 ? 2 : -2)}%`,
            width: `${ray.width}%`,
            height: '118%',
            transform: `rotate(${ray.rotate}deg)`,
            transformOrigin: 'top center',
            background:
              'linear-gradient(180deg, rgba(211, 248, 255, 0.85), rgba(128, 211, 236, 0.18) 42%, transparent 82%)',
            opacity: ray.opacity,
            filter: 'blur(7px)',
            mixBlendMode: 'screen',
          }}
        />
      ))}
      <AbsoluteFill
        style={{
          opacity: 0.18,
          background:
            'repeating-radial-gradient(ellipse at 48% 8%, transparent 0 23px, rgba(218, 251, 255, 0.5) 24px 25px, transparent 26px 48px)',
          transform: `translateY(${slowWave * 8}px) skewY(-4deg)`,
          mixBlendMode: 'screen',
        }}
      />
      {bubbles.map((bubble, index) => {
        const travel = interpolate(
          (loopFrame * bubble.speed + bubble.delay) % 180,
          [0, 180],
          [106, -16],
        );
        const sway = Math.sin(loopFrame / 19 + index * 1.7) * 1.8;
        return (
          <div
            key={index}
            style={{
              position: 'absolute',
              left: `${bubble.left + sway}%`,
              top: `${travel}%`,
              width: bubble.size,
              height: bubble.size,
              borderRadius: '999px',
              border: '1.5px solid rgba(238, 253, 255, 0.72)',
              boxShadow: 'inset -7px -10px 16px rgba(255, 255, 255, 0.13)',
              opacity: bubble.opacity,
            }}
          >
            <div
              style={{
                position: 'absolute',
                left: '24%',
                top: '20%',
                width: '26%',
                height: '26%',
                borderRadius: '999px',
                background: 'rgba(255, 255, 255, 0.72)',
              }}
            />
          </div>
        );
      })}
      <div
        style={{
          position: 'absolute',
          left: '-8%',
          right: '-8%',
          bottom: -4,
          height: '23%',
          background:
            'radial-gradient(ellipse at 25% 100%, #071e2b 0 27%, transparent 28%), radial-gradient(ellipse at 51% 100%, #061927 0 36%, transparent 37%), radial-gradient(ellipse at 75% 100%, #04131f 0 31%, transparent 32%)',
        }}
      />
      <AbsoluteFill
        style={{
          background:
            'radial-gradient(ellipse at 50% 100%, rgba(18, 72, 73, 0.58), transparent 35%), linear-gradient(180deg, transparent 64%, rgba(1, 6, 13, 0.48))',
        }}
      />
    </AbsoluteFill>
  );
};
