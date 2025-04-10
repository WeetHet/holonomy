{
  system ? builtins.currentSystem,
  sources ? import ./npins,
  pkgs ? import sources.nixpkgs { inherit system; },
  pyproject-nix ? import sources.pyproject-nix { inherit lib; },
  lib ? pkgs.lib,
}:
let
  project = pyproject-nix.lib.project.loadPyproject { projectRoot = ./.; };
  python = pkgs.python3.override {
    packageOverrides = pyfinal: pyprev: {
      bezier = pyfinal.callPackage ./nix/bezier.nix { };
    };
  };
  pythonEnv = project.renderers.withPackages {
    inherit python;
    groups = [ "dev" ];
  };
  pythonDrv = python.withPackages pythonEnv;
  pythonToLink = pkgs.symlinkJoin {
    name = "python-holonomy-env";
    paths = [
      pythonDrv
      pkgs.ruff
      pkgs.pyright
    ];
  };
  relaxedDeps.pythonRelaxDeps = [ "plotly" ];
  holonomy = python.pkgs.buildPythonPackage (
    relaxedDeps
    // project.renderers.buildPythonPackage {
      inherit python;
      groups = [ "dev" ];
    }
  );
in
pkgs.mkShell {
  packages = [
    pkgs.uv

    holonomy

    pythonDrv
    pkgs.ruff
    pkgs.pyright

    pkgs.npins
  ];

  shellHook = ''
    ln -snf ${pythonToLink} .python-env
    [[ -d .venv ]] && source .venv/bin/activate
  '';

  env.UV_NO_SYNC = 1;
}
