const ETHNOMED_TB_PROFILE_URL =
  'https://ethnomed.org/resource/ethiopian-tuberculosis-cultural-profile/';

export default function LandingImageCredit() {
  return (
    <a
      href={ETHNOMED_TB_PROFILE_URL}
      target="_blank"
      rel="noopener noreferrer"
      className="landingImageCredit"
      title="Opens EthnoMed in a new tab"
    >
      <span className="landingImageCredit__eyebrow">About this image</span>
      <span className="landingImageCredit__text">
        UNICEF Ethiopia — TB recovery context. Read the Ethiopian TB cultural profile on EthnoMed.
      </span>
    </a>
  );
}
