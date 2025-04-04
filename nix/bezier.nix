{
  fetchFromGitHub,
  buildPythonPackage,
  setuptools,
  numpy,
}:

buildPythonPackage rec {
  version = "2024.6.20";
  pname = "bezier";
  src = fetchFromGitHub {
    owner = "dhermes";
    repo = "bezier";
    tag = version;
    hash = "sha256-TH3x6K5S3uV/K/5e+TXCSiJsyJE0tZ+8ZLc+i/x/fV8=";
  };

  build-system = [ setuptools ];

  dependencies = [
    numpy
  ];

  env.BEZIER_NO_EXTENSION = "True";
}
