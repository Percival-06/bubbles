import {Composition, Still} from 'remotion';
import {BubbleSprite} from './compositions/BubbleSprite';
import {CoverStill} from './compositions/CoverStill';
import {DeepSeaBackground} from './compositions/DeepSeaBackground';
import {EnergySeedSprite} from './compositions/EnergySeedSprite';

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
      <Still
        id="BubbleLarge"
        component={BubbleSprite}
        width={160}
        height={160}
        defaultProps={{size: 152}}
      />
      <Still
        id="BubbleSmall"
        component={BubbleSprite}
        width={48}
        height={48}
        defaultProps={{size: 42}}
      />
      <Still
        id="EnergySeed"
        component={EnergySeedSprite}
        width={64}
        height={64}
        defaultProps={{size: 34}}
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
