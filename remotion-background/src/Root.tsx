import {Composition, Still} from 'remotion';
import {CoverStill} from './compositions/CoverStill';
import {DeepSeaBackground} from './compositions/DeepSeaBackground';

export const RemotionRoot = () => {
  return (
    <>
      <Still
        id="CoverStill"
        component={CoverStill}
        width={1280}
        height={720}
      />
      <Still
        id="MainMenuBackground"
        component={DeepSeaBackground}
        width={800}
        height={600}
      />
      <Composition
        id="MainMenuLoop"
        component={DeepSeaBackground}
        width={800}
        height={600}
        fps={30}
        durationInFrames={180}
      />
    </>
  );
};
